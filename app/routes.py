# app/routes.py
from fastapi import APIRouter, HTTPException
from . import storage, service
from .schemas import TeamCreate, ScoreInput

router = APIRouter()

# Note: usamos storage.load_state() en startup y guardamos con save_state()
# Metodos HTTP 

@router.get("/teams")
def list_teams():
    state = storage.load_state()
    return state.get("teams", [])

@router.post("/teams")
def create_team(payload: TeamCreate):
    state = storage.load_state()
    # generar id simple (hex)
    import uuid
    team_id = uuid.uuid4().hex
    team = {"id": team_id, "name": payload.name}
    state["teams"].append(team)
    storage.save_state(state)
    return team

@router.delete("/teams/{team_id}")
def delete_team(team_id: str):
    state = storage.load_state()
    # evitar borrar si tiene partidos generados
    if any(m for m in state.get("matches", []) if m["home"] == team_id or m["away"] == team_id):
        raise HTTPException(status_code=400, detail="No se puede borrar: el equipo aparece en partidos generados.")
    state["teams"] = [t for t in state["teams"] if t["id"] != team_id]
    storage.save_state(state)
    return {"ok": True}

@router.post("/fixture/generate")
def generate_fixture():
    state = storage.load_state()
    teams = state.get("teams", [])
    if len(teams) < 2:
        raise HTTPException(status_code=400, detail="Se requieren al menos 2 equipos.")
    matches = service.generate_matches_from_teams(teams)
    state["matches"] = matches
    storage.save_state(state)
    return {"matches_created": len(matches)}

@router.get("/fixture")
def get_fixture():
    state = storage.load_state()
    return state.get("matches", [])

@router.post("/matches/{match_id}/result")
def post_result(match_id: str, payload: ScoreInput):
    state = storage.load_state()
    try:
        updated = service.record_result(state, match_id, payload.score)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    storage.save_state(state)
    return updated

@router.get("/standings")
def get_standings():
    state = storage.load_state()
    table = service.compute_standings(state)
    return table