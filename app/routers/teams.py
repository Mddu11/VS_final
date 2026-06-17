from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.dependencies import get_db, get_current_admin
from app.models import Team
from app.schemas import TeamCreate, TeamResponse, TeamUpdate

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/", response_model=TeamResponse)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    new_team = Team(name=team.name)
    db.add(new_team)
    await db.commit()
    await db.refresh(new_team)
    return new_team

@router.get("/", response_model=List[TeamResponse])
async def get_teams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team))
    return result.scalars().all()

@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(team_id: int, t_data: TeamUpdate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """Редактирование команды администратором"""
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    for key, value in t_data.model_dump(exclude_unset=True).items():
        setattr(team, key, value)
    await db.commit()
    await db.refresh(team)
    return team

@router.delete("/{team_id}")
async def delete_team(team_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """Удаление команды администратором"""
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    await db.delete(team)
    await db.commit()
    return {"msg": "Team deleted"}