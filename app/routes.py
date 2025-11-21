# app/routes.py
from fastapi import APIRouter, Body, HTTPException
from . import storage, service
import uuid
from typing import List, Dict, Any

router = APIRouter()

# ---------------------------
# FUNCIONES DE VALIDACIÓN
# ---------------------------

def validate_team_create_input(
    name: str,
    titulares: List[str],
    suplentes: List[str]
) -> Dict[str, Any]:
    """
    Valida los datos de entrada para crear un nuevo equipo.
    
    Reglas de validación:
    - name: String no vacío (mínimo 1 carácter después de strip)
    - titulares: Máximo 11 jugadores
    - suplentes: Máximo 3 jugadores
    
    Args:
        name: Nombre del equipo
        titulares: Lista de nombres de titulares
        suplentes: Lista de nombres de suplentes
    
    Returns:
        Diccionario validado con estructura:
        {'name': str, 'titulares': list, 'suplentes': list}
    
    Raises:
        ValueError: Si alguna validación falla
    
    Ejemplo:
        >>> validate_team_create_input("Barcelona", [], [])
        {'name': 'Barcelona', 'titulares': [], 'suplentes': []}
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("El nombre del equipo debe ser un string no vacío.")
    
    if not isinstance(titulares, list):
        raise ValueError("Titulares debe ser una lista.")
    if len(titulares) > 11:
        raise ValueError("No puede haber más de 11 titulares.")
    
    if not isinstance(suplentes, list):
        raise ValueError("Suplentes debe ser una lista.")
    if len(suplentes) > 3:
        raise ValueError("No puede haber más de 3 suplentes.")
    
    return {
        "name": name.strip(),
        "titulares": titulares,
        "suplentes": suplentes
    }


def validate_team_id(team_id: str) -> None:
    """
    Valida que el team_id sea un string válido.
    
    Args:
        team_id: ID a validar
    
    Raises:
        ValueError: Si el ID no es válido
    """
    if not isinstance(team_id, str) or not team_id.strip():
        raise ValueError("El team_id debe ser un string válido.")


def validate_teams_minimum(teams: List[Dict[str, str]]) -> None:
    """
    Valida que haya mínimo 2 equipos.
    
    Args:
        teams: Lista de equipos
    
    Raises:
        ValueError: Si hay menos de 2 equipos
    """
    if len(teams) < 2:
        raise ValueError("Se requieren al menos 2 equipos para generar un fixture.")


def validate_team_has_no_matches(
    team_id: str,
    matches: List[Dict[str, Any]]
) -> None:
    """
    Valida que un equipo no tenga partidos asociados.
    
    Args:
        team_id: ID del equipo a verificar
        matches: Lista de partidos
    
    Raises:
        ValueError: Si el equipo tiene partidos
    """
    if any(m for m in matches if m["home"] == team_id or m["away"] == team_id):
        raise ValueError("No se puede borrar: el equipo aparece en partidos generados.")


# ---------------------------
# RUTA INICIO
# ---------------------------
@router.get("/")
def home():
    return {
        "mensaje": "Bienvenido a la API del Proyecto Fixture y Tabla de Posiciones ⚽",
        "descripcion": (
            "Esta aplicación permite gestionar torneos de fútbol: "
            "registrar equipos, generar un fixture de todos contra todos, "
            "cargar resultados y visualizar la tabla de posiciones en tiempo real."
        ),
        "integrantes": [
            "Juan Bogado",
            "Agustin Bonicalzi",
            "Federico Roger",
            "Santino Ianeo"
        ],
        "titulo_proyecto": "Fixture y Tabla de Posiciones para Torneos de Fútbol",
        "curso": "Programación 1",
        "materia": "Sistemas de Administración",
        "tecnologias": {
            "backend": "FastAPI (Python)",
            "frontend": "React",
            "persistencia": "Archivos JSON"
        }
    }

# ---------------------------
# EQUIPOS
# ---------------------------

@router.get("/teams")
def list_teams():
    """Devuelve todos los equipos almacenados."""
    state = storage.load_state()
    return state.get("teams", [])

@router.post("/teams")
def create_team(
    name: str = Body(...),
    titulares: list[str] = Body(default=[]),
    suplentes: list[str] = Body(default=[])
):
    """
    Crea un nuevo equipo.
    
    Validaciones:
    - Nombre no vacío
    - Máximo 11 titulares
    - Máximo 3 suplentes
    
    Args:
        name: Nombre del equipo
        titulares: Lista de titulares
        suplentes: Lista de suplentes
    
    Returns:
        Equipo creado con ID único
    """
    try:
        validated_data = validate_team_create_input(name, titulares, suplentes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    state = storage.load_state()
    
    team = {
        "id": uuid.uuid4().hex,
        "name": validated_data["name"],
        "titulares": validated_data["titulares"],
        "suplentes": validated_data["suplentes"]
    }

    state["teams"].append(team)
    storage.save_state(state)
    return team

@router.delete("/teams/{team_id}")
def delete_team(team_id: str):
    """
    Elimina un equipo del almacenamiento si no tiene partidos asociados.
    
    Args:
        team_id: ID del equipo a eliminar
    
    Raises:
        HTTPException 400: Si el equipo tiene partidos asociados
    
    Returns:
        {'ok': True} si se eliminó correctamente
    """
    try:
        validate_team_id(team_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    state = storage.load_state()

    try:
        validate_team_has_no_matches(team_id, state.get("matches", []))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    state["teams"] = [t for t in state["teams"] if t["id"] != team_id]
    storage.save_state(state)
    return {"ok": True}


# ---------------------------
# FIXTURE
# ---------------------------

@router.get("/fixture")
def get_fixture():
    """Devuelve todos los partidos del fixture."""
    state = storage.load_state()
    return state.get("matches", [])

@router.post("/fixture/generate")
def generate_fixture():
    """
    Genera un fixture de todos contra todos (round-robin).
    
    Requisitos:
    - Mínimo 2 equipos registrados
    
    Returns:
        {'matches_created': int} - Número de partidos generados
    """
    state = storage.load_state()
    teams = state.get("teams", [])
    
    try:
        validate_teams_minimum(teams)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    matches = service.generate_matches_from_teams(teams)
    state["matches"] = matches
    storage.save_state(state)
    return {"matches_created": len(matches)}

# ---------------------------
# RESULTADOS
# ---------------------------

@router.post("/matches/{match_id}/result")
def post_result(match_id: str, score: str):
    """
    Registra el resultado de un partido.
    
    Args:
        match_id: ID del partido a actualizar
        score: String con formato "goles_local-goles_visitante" (ej: "2-1")
    
    Returns:
        Partido actualizado con resultado registrado
    
    Raises:
        HTTPException 400: Si el partido no existe o score inválido
    """
    state = storage.load_state()

    try:
        updated = service.record_result(state, match_id, score)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    storage.save_state(state)
    return updated

# ---------------------------
# TABLA DE POSICIONES
# ---------------------------

@router.get("/standings")
def get_standings():
    """Calcula y devuelve la tabla de posiciones."""
    state = storage.load_state()
    table = service.compute_standings(state)
    return table
