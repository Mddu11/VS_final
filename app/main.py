from fastapi import FastAPI
from app.routers import auth, teams, questions, games

app = FastAPI(title="Quiz Service API")

app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(questions.router)
app.include_router(games.router)