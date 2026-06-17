import json
import asyncio
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_admin, get_current_user
from app.models import Game, Question, User
from app.schemas import GameCreate, GameResponse, AnswerSubmit, GameUpdate
from app.core.config import settings

router = APIRouter(prefix="/games", tags=["games"])

@router.post("/", response_model=GameResponse)
async def create_game(game: GameCreate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    new_game = Game(scheduled_time=game.scheduled_time)
    db.add(new_game)
    await db.commit()
    await db.refresh(new_game)
    return new_game

@router.post("/{game_id}/start")
async def start_game(game_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    game.is_active = True
    await db.commit()
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis_client.publish(f"game_{game_id}", json.dumps({"event": "game_started"}))
    await redis_client.close()
    return {"status": "Game started"}

@router.post("/{game_id}/send_question/{question_id}")
async def send_question(game_id: int, question_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    message = {
        "event": "new_question",
        "question_id": question.id,
        "text": question.text,
        "options": [question.option_a, question.option_b, question.option_c, question.option_d]
    }
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis_client.publish(f"game_{game_id}", json.dumps(message))
    await redis_client.setex(f"game_{game_id}_q_{question.id}_timer", 30, "active")
    await redis_client.close()
    return {"status": "Question sent"}

@router.post("/{game_id}/answer")
async def submit_answer(game_id: int, answer: AnswerSubmit, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    timer_active = await redis_client.get(f"game_{game_id}_q_{answer.question_id}_timer")
    await redis_client.close()
    if not timer_active:
        raise HTTPException(status_code=400, detail="Time is up")
    
    question = await db.get(Question, answer.question_id)
    is_correct = (question.correct_option == answer.chosen_option)
    return {"status": "Answer received", "is_correct": is_correct}

@router.websocket("/{game_id}/ws")
async def game_websocket(websocket: WebSocket, game_id: int):
    await websocket.accept()
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"game_{game_id}")
    
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"game_{game_id}")
        await redis_client.close()

@router.put("/{game_id}", response_model=GameResponse)
async def update_game(game_id: int, g_data: GameUpdate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """Редактирование параметров игры администратором"""
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    for key, value in g_data.model_dump(exclude_unset=True).items():
        setattr(game, key, value)
    await db.commit()
    await db.refresh(game)
    return game

@router.delete("/{game_id}")
async def delete_game(game_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """Удаление игры администратором"""
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    await db.delete(game)
    await db.commit()
    return {"msg": "Game deleted"}