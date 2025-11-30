from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, UploadFile
import os
import shutil
from io import BytesIO
from pypdf import PdfReader

from app.repos.content_repo import HomeworkRepo, MaterialRepo
from app.repos.chat_repo import SessionRepo
from app.models.content import Homework, HomeworkTask, HomeworkStatus
from app.dto.content import HomeworkCreate
from app.services.vector_store import VectorStoreService
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
from app.enums.db_enums import Grade
from app.prompts.HOMEWORK_GENERATION_PROMPT import HOMEWORK_GENERATION_PROMPT

class TaskGrade(BaseModel):
    task_number: int
    score: float
    feedback: str

class HomeworkGrade(BaseModel):
    overall_feedback: str
    grade: Grade
    tasks: List[TaskGrade]

class HomeworkService:
    def __init__(self, homework_repo: HomeworkRepo, session_repo: SessionRepo, material_repo: MaterialRepo, vector_store_service: VectorStoreService):
        self.homework_repo = homework_repo
        self.session_repo = session_repo
        self.material_repo = material_repo
        self.vector_store_service = vector_store_service

    async def create_homework(self, session_id: UUID, user_id: UUID, data: HomeworkCreate) -> Homework:
        session = await self.session_repo.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")

        homework = await self.homework_repo.create(
            session_id=session_id,
            title=f"Homework for {session.title} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            status=HomeworkStatus.PENDING
        )

        # Generate tasks using LLM
        vector_store_name = f"session_{session_id}"
        vector_store_id = await self.vector_store_service.get_or_create_vector_store(vector_store_name)
        
        # Fetch specific materials if provided
        focus_materials_text = ""
        if data.material_ids:
            materials = await self.material_repo.get_by_ids(data.material_ids)
            if materials:
                filenames = ", ".join([f"'{m.name}'" for m in materials])
                focus_materials_text = f"Please focus specifically on the following materials: {filenames}."
        
        # Construct the detailed prompt with materials context
        if focus_materials_text:
            context_note = f"\n\nIMPORTANT: {focus_materials_text}"
        else:
            context_note = ""
        
        user_prompt = f"""
{HOMEWORK_GENERATION_PROMPT}

---
USER REQUEST: {data.prompt}{context_note}

Based on the materials in the vector store and the user's request above, create 3-5 precise, actionable homework tasks.
Return ONLY the JSON with the tasks array as specified in the prompt.
        """
        
        client = self.vector_store_service.client
        assistant = await client.beta.assistants.create(
            name="Homework Generator",
            instructions="You are an expert teacher who creates precise, actionable homework tasks. Follow the provided prompt structure exactly.",
            model="gpt-4o-2024-08-06",
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
        )
        
        # Define response schema for generation
        class TaskGen(BaseModel):
            description: str
            
        class HomeworkGen(BaseModel):
            tasks: List[TaskGen]
            
        thread = await client.beta.threads.create(
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "homework_generation",
                    "schema": HomeworkGen.model_json_schema()
                }
            }
        )
        
        tasks_data = []
        if run.status == 'completed':
            messages = await client.beta.threads.messages.list(thread_id=thread.id)
            response_text = messages.data[0].content[0].text.value
            try:
                gen_result = HomeworkGen.model_validate_json(response_text)
                tasks_data = gen_result.tasks
            except Exception as e:
                print(f"Error parsing generation response: {e}")
                
        # Cleanup
        await client.beta.assistants.delete(assistant.id)

        # Fallback if generation failed
        if not tasks_data:
            tasks_data = [
                TaskGen(description=f"Summarize the key points from the provided materials based on: {data.prompt}"),
                TaskGen(description="Identify 3 main concepts and explain them."),
                TaskGen(description="Create a quiz question based on the material.")
            ]

        tasks = [
            HomeworkTask(
                homework_id=homework.id,
                task_number=i+1,
                description=t.description
            ) for i, t in enumerate(tasks_data)
        ]
        
        self.homework_repo.session.add_all(tasks)
        await self.homework_repo.session.commit()
        
        # Re-fetch to ensure DTO fields (tasks) are loaded
        return await self.homework_repo.get(homework.id)

    async def get_session_homeworks(self, session_id: UUID, user_id: UUID) -> list[Homework]:
        session = await self.session_repo.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        return await self.homework_repo.get_by_session(session_id)

    async def get_homework(self, homework_id: UUID, user_id: UUID) -> Homework:
        homework = await self.homework_repo.get(homework_id)
        if not homework:
            raise HTTPException(status_code=404, detail="Homework not found")
        
        session = await self.session_repo.get(homework.session_id)
        if not session or session.user_id != user_id:
             raise HTTPException(status_code=403, detail="Not authorized")
             
        return homework

    async def upload_task_solution(self, homework_id: UUID, task_id: UUID, user_id: UUID, file: UploadFile) -> HomeworkTask:
        # Verify homework and ownership
        homework = await self.get_homework(homework_id, user_id)
        
        # Fetch task by id, then verify it belongs to the provided homework
        result = await self.homework_repo.session.execute(
            select(HomeworkTask).where(HomeworkTask.id == task_id)
        )
        task = result.scalars().first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.homework_id != homework_id:
            raise HTTPException(status_code=404, detail="Task does not belong to this homework")

        # Read file into memory (avoid persisting locally) and upload to vector store
        await file.seek(0)
        file_bytes = await file.read()
        filename = file.filename or f"task_{task_id}"

        vector_store_name = f"session_{homework.session_id}"
        vector_store_id = await self.vector_store_service.get_or_create_vector_store(vector_store_name)

        # If PDF, attempt to extract text and upload as .txt for better searchability
        uploaded = None
        if filename.lower().endswith('.pdf'):
            try:
                reader = PdfReader(BytesIO(file_bytes))
                pages_text = []
                for page in reader.pages:
                    txt = page.extract_text() or ''
                    pages_text.append(txt)
                extracted = "\n\n".join(pages_text).strip()
                if extracted:
                    txt_name = os.path.splitext(filename)[0] + '.txt'
                    uploaded = await self.vector_store_service.upload_bytes(txt_name, extracted.encode('utf-8'), vector_store_id)
            except Exception as e:
                # Fallback to uploading original bytes if parsing fails
                pass

        if not uploaded:
            uploaded = await self.vector_store_service.upload_bytes(filename, file_bytes, vector_store_id)

        # Update task with a reference-friendly display name
        task.uploaded_file_url = filename
        await self.homework_repo.session.commit()
        await self.homework_repo.session.refresh(task)
        
        return task

    async def submit_homework(self, homework_id: UUID, user_id: UUID) -> Homework:
        homework = await self.get_homework(homework_id, user_id)
        
        # Fetch session to avoid lazy-loading in async context
        session = await self.session_repo.get(homework.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all tasks
        result = await self.homework_repo.session.execute(
            select(HomeworkTask).where(HomeworkTask.homework_id == homework_id).order_by(HomeworkTask.task_number)
        )
        tasks = result.scalars().all()
        
        # Construct prompt
        prompt = f"Please grade the following homework for the session '{session.title}'.\n\n"
        for task in tasks:
            prompt += f"Task {task.task_number}: {task.description}\n"
            if task.uploaded_file_url:
                filename = os.path.basename(task.uploaded_file_url)
                prompt += f"Solution File: {filename} (available in vector store)\n"
            else:
                prompt += "Solution: No solution provided.\n"
            prompt += "\n"
            
        # Call LLM
        vector_store_name = f"session_{homework.session_id}"
        vector_store_id = await self.vector_store_service.get_or_create_vector_store(vector_store_name)
        
        client = self.vector_store_service.client
        assistant = await client.beta.assistants.create(
            name="Homework Grader",
            instructions="You are a strict but fair grader. You have access to the student's submitted files in your vector store.",
            model="gpt-4o-2024-08-06", # Ensure model supports structured outputs
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
        )
        
        thread = await client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "homework_grading",
                    "schema": HomeworkGrade.model_json_schema()
                }
            }
        )
        
        if run.status == 'completed':
            messages = await client.beta.threads.messages.list(
                thread_id=thread.id
            )
            response_text = messages.data[0].content[0].text.value
            
            try:
                # Parse JSON using Pydantic
                grading_result = HomeworkGrade.model_validate_json(response_text)
                    
                # Save reviews
                from app.models.content import HomeworkReview, HomeworkTaskReview
                
                # Overall review
                review = HomeworkReview(
                    homework_id=homework.id,
                    grade=grading_result.grade,
                    overall_feedback=grading_result.overall_feedback,
                    reviewed_by="AI Grader"
                )
                self.homework_repo.session.add(review)
                
                # Task reviews
                for task_review in grading_result.tasks:
                    task = next((t for t in tasks if t.task_number == task_review.task_number), None)
                    if task:
                        tr = HomeworkTaskReview(
                            homework_task_id=task.id,
                            task_feedback=task_review.feedback,
                            score=task_review.score
                        )
                        self.homework_repo.session.add(tr)
                
                homework.status = HomeworkStatus.GRADED
                await self.homework_repo.session.commit()
                
            except Exception as e:
                print(f"Error parsing grading response: {e}")
                # Fallback or error handling
                pass
                
        # Cleanup
        await client.beta.assistants.delete(assistant.id)
        
        return homework
