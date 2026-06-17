from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models import RoleEnum


class Token(BaseModel):
    access_token: str
    token_type: str
    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    role: RoleEnum = RoleEnum.player
    team_id: Optional[int] = None
    

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: RoleEnum
    team_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)

class TeamResponse(BaseModel):
    id: int
    name: str
    score: int
    games_played: int
    wins: int
    losses: int

    model_config = ConfigDict(from_attributes=True)

class QuestionCreate(BaseModel):
    text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str


class QuestionResponse(QuestionCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

class GameCreate(BaseModel):
    scheduled_time: datetime

class GameResponse(GameCreate):
    id: int
    is_active: bool
    is_completed: bool

    model_config = ConfigDict(from_attributes=True)
        
class AnswerSubmit(BaseModel):
    question_id: int
    chosen_option: str
# --- Схемы для редактирования данных (PUT/PATCH запросы) ---

class PasswordChange(BaseModel):
    """Схема валидации данных при смене пароля"""
    old_password: str
    new_password: str

class UserUpdate(BaseModel):
    """Схема для обновления пользователя. Все поля опциональны, 
    чтобы можно было обновить только часть данных"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    team_id: Optional[int] = None

class QuestionUpdate(BaseModel):
    """Схема для частичного обновления данных вопроса"""
    text: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_option: Optional[str] = None

class GameUpdate(BaseModel):
    """Схема для обновления статуса или времени игры"""
    scheduled_time: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None

class TeamUpdate(BaseModel):
    name: Optional[str] = None

class TeamCreate(BaseModel):
    name: str