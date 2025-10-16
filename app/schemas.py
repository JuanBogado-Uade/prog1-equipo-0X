# Crear los schemas o modelos a utilzar

from typing import Optional, List
from pydantic import BaseModel

class TeamCreate(BaseModel):
    name:str

class Team(BaseModel):
    id: str
    name: str

class Match(BaseModel):
    id: str
    home: str
    away: str
    round: int
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None
    palyed: bool = False

class ScoreInputs(BaseModel):
    score: str