from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.dependencies import get_db, get_current_admin
from app.models import Question
from app.schemas import QuestionCreate, QuestionResponse, QuestionUpdate

router = APIRouter(prefix="/questions", tags=["questions"])

@router.post("/", response_model=QuestionResponse)
async def create_question(q: QuestionCreate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    new_q = Question(**q.model_dump())
    db.add(new_q)
    await db.commit()
    await db.refresh(new_q)
    return new_q

@router.get("/", response_model=List[QuestionResponse])
async def get_questions(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(select(Question))
    return result.scalars().all()

@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, q_data: QuestionUpdate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """Редактирование вопроса администратором"""
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    for key, value in q_data.model_dump(exclude_unset=True).items():
        setattr(question, key, value)
    await db.commit()
    await db.refresh(question)
    return question

@router.delete("/{question_id}")
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """Удаление вопроса администратором"""
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    await db.delete(question)
    await db.commit()
    return {"msg": "Question deleted"}