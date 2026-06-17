import enum
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Enum

Base = declarative_base()

class RoleEnum(str, enum.Enum):
    admin = "admin"
    player = "player"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True, index=True) 
    hashed_password = Column(String) 
    role = Column(Enum(RoleEnum), default=RoleEnum.player)   
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    team_id = Column(Integer, nullable=True)
    
class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    scheduled_time = Column(String)
    is_active = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)



class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_option = Column(String)

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    score = Column(Integer, default=0)
    games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)