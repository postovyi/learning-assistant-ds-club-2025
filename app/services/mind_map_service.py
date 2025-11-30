from uuid import UUID
from datetime import datetime
from fastapi import HTTPException
from app.repos.content_repo import MindMapRepo, MaterialRepo
from app.repos.chat_repo import SessionRepo
from app.models.content import MindMap
from app.dto.content import MindMapCreate
from app.services.vector_store import VectorStoreService

class MindMapService:
    def __init__(
        self,
        mind_map_repo: MindMapRepo,
        session_repo: SessionRepo,
        material_repo: MaterialRepo,
        vector_store_service: VectorStoreService
    ):
        self.mind_map_repo = mind_map_repo
        self.session_repo = session_repo
        self.material_repo = material_repo
        self.vector_store_service = vector_store_service

    async def generate_mind_map(self, session_id: UUID, user_id: UUID) -> MindMap:
        session = await self.session_repo.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")

        # 1. Summarize materials using LLM to get a visual description
        vector_store_name = f"session_{session_id}"
        vector_store_id = await self.vector_store_service.get_or_create_vector_store(vector_store_name)
        
        prompt = """
        IMPORTANT: Use the file_search tool to access and read ALL uploaded materials in the vector store.
        
        Your task:
        1. Search and read through ALL the uploaded documents/materials
        2. Analyze the content to identify the main topic, key concepts, and relationships
        3. Create a detailed visual description for a mind map that summarizes these concepts
        
        The description should be suitable for an image generation model (DALL-E 3).
        Structure your description to include:
        - The central topic/theme
        - 3-5 main branches (major concepts)
        - Sub-topics for each branch
        - Key keywords and relationships
        
        Format: Start with "A professional educational mind map about [TOPIC]. The center shows [CENTRAL CONCEPT]. Main branches include: [BRANCH 1] with sub-topics [X,Y,Z], [BRANCH 2] with [A,B,C]..." etc.
        
        Keep the description concise (under 1000 characters) but detailed enough to generate a clear, informative mind map.
        DO NOT ask the user for information - read the files in the vector store.
        """
        
        client = self.vector_store_service.client
        assistant = await client.beta.assistants.create(
            name="Mind Map Architect",
            instructions="You are an expert in creating educational mind maps. Always use the file_search tool to read uploaded materials.",
            model="gpt-4o-2024-08-06",
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
        )
        
        thread = await client.beta.threads.create(
            messages=[{"role": "user", "content": prompt}]
        )
        
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        
        image_prompt = "A mind map." # Fallback
        if run.status == 'completed':
            messages = await client.beta.threads.messages.list(thread_id=thread.id)
            image_prompt = messages.data[0].content[0].text.value
            
        await client.beta.assistants.delete(assistant.id)
        
        # 2. Generate Image using DALL-E 3
        try:
            response = await client.images.generate(
                model="dall-e-3",
                prompt=image_prompt[:4000], # Ensure prompt length is within limits
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
        except Exception as e:
            print(f"Error generating image: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate mind map image")

        # 3. Save to DB
        mind_map = await self.mind_map_repo.create(
            session_id=session_id,
            title=f"Mind Map - {datetime.utcnow().strftime('%Y-%m-%d')}",
            node_count=0, # Not applicable for image
            data={"image_url": image_url, "prompt": image_prompt}
        )
        
        return mind_map

    async def get_session_mind_maps(self, session_id: UUID, user_id: UUID) -> list[MindMap]:
        session = await self.session_repo.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        return await self.mind_map_repo.get_by_session(session_id)
