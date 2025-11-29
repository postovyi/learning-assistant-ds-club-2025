from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.database import get_db
from app.dto.content import HomeworkRead, HomeworkTaskRead
from app.models import Homework, HomeworkTask
from app.enums import HomeworkStatus

router = APIRouter(prefix="/homework", tags=["Homework"])

@router.post("/generate", response_model=HomeworkRead, status_code=201)
async def generate_homework(
    session_id: UUID,
    title: str,
    db: Session = Depends(get_db)
) -> HomeworkRead:
    """Генерувати нову домашню роботу для сесії"""
    # Створюємо нову домашню роботу
    new_homework = Homework(
        session_id=session_id,
        title=title,
        status=HomeworkStatus.PENDING,
        generated_at=datetime.utcnow()
    )
    db.add(new_homework)
    db.commit()
    db.refresh(new_homework)
    
    return HomeworkRead.model_validate(new_homework)


@router.get("/{homework_id}", response_model=HomeworkRead)
async def get_homework(
    homework_id: UUID,
    db: Session = Depends(get_db)
) -> HomeworkRead:
    """Отримати домашню роботу за ID"""
    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    return HomeworkRead.model_validate(homework)


@router.get("/session/{session_id}", response_model=list[HomeworkRead])
async def get_session_homeworks(
    session_id: UUID,
    db: Session = Depends(get_db)
) -> list[HomeworkRead]:
    """Отримати всі домашні роботи для певної сесії"""
    homeworks = db.query(Homework).filter(Homework.session_id == session_id).all()
    return [HomeworkRead.model_validate(hw) for hw in homeworks]


@router.post("/{homework_id}/tasks", response_model=HomeworkTaskRead, status_code=201)
async def add_homework_task(
    homework_id: UUID,
    task_number: int,
    description: str,
    uploaded_file_url: str = None,
    db: Session = Depends(get_db)
) -> HomeworkTaskRead:
    """Додати завдання до домашньої роботи"""
    # Перевіряємо чи існує домашня робота
    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    # Створюємо нове завдання
    new_task = HomeworkTask(
        homework_id=homework_id,
        task_number=task_number,
        description=description,
        uploaded_file_url=uploaded_file_url
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return HomeworkTaskRead.model_validate(new_task)


@router.get("/{homework_id}/tasks", response_model=list[HomeworkTaskRead])
async def get_homework_tasks(
    homework_id: UUID,
    db: Session = Depends(get_db)
) -> list[HomeworkTaskRead]:
    """Отримати всі завдання домашньої роботи"""
    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    tasks = db.query(HomeworkTask).filter(HomeworkTask.homework_id == homework_id).all()
    return [HomeworkTaskRead.model_validate(task) for task in tasks]


@router.patch("/{homework_id}/submit", response_model=HomeworkRead)
async def submit_homework(
    homework_id: UUID,
    db: Session = Depends(get_db)
) -> HomeworkRead:
    """Подати домашню роботу (змінити статус)"""
    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    homework.status = HomeworkStatus.SUBMITTED
    homework.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(homework)
    
    return HomeworkRead.model_validate(homework)

