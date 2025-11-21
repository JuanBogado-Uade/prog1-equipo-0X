# app/schemas.py
from typing import List, Optional

# ---------------------------
# FUNCIONES DE VALIDACIÓN
# ---------------------------

def validate_team_create(name: str, titulares: Optional[List[str]] = None, suplentes: Optional[List[str]] = None) -> dict:
    """Valida y crea un diccionario de equipo."""
    if not isinstance(name, str) or not name.strip():
    # entra aca si alguno es true
    # La condición será true si:
	#1.	name no es una cadena.
	#2.	name es una cadena vacía o solo tiene espacios.
        raise ValueError("El nombre del equipo debe ser un string no vacío.")
    
    titulares = titulares or []
    suplentes = suplentes or []

    if len(titulares) > 11:
        raise ValueError("No puede haber más de 11 titulares.")
    if len(suplentes) > 3:
        raise ValueError("No puede haber más de 3 suplentes.")

    return {
        "name": name.strip(),
        "titulares": titulares,
        "suplentes": suplentes
    }

def validate_team(id: str, name: str) -> dict:
    """Valida un equipo ya existente (con id)."""
    if not id or not isinstance(id, str):
        # si id es false, cambia a true.
        # si id no es un string es false, y cambia a true
        raise ValueError("El id del equipo debe ser un string válido.")
    if not name or not isinstance(name, str):
        # si name es false, cambia a true.
        # si id no es un string es false, y cambia a true
        raise ValueError("El nombre del equipo debe ser un string válido.")
    #devuelve el objeto
    return {"id": id, "name": name}

def validate_match(
    id: str, home: str, away: str, round: int,
    home_goals: Optional[int] = None, away_goals: Optional[int] = None,
    played: bool = False
) -> dict:
    #se asegura de recibir los tipos correctos
    """Valida y crea un diccionario para un partido."""
    if not all(isinstance(x, str) for x in [id, home, away]):
        # comprension de lista
        # con all() ser verifica que todos los valores sean true
        # agarra cada elemento y verifica si es str
        # si algun elemento no es un str da false, y cambia a true con el not
        raise ValueError("El id, home y away deben ser strings.")
    if not isinstance(round, int) or round <= 0:
        # si round no es un numero da false, y cambia a true
        # round es menor o igual a 0, da true
        raise ValueError("La ronda debe ser un número entero positivo.")

    return {
        "id": id,
        "home": home,
        "away": away,
        "round": round,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "played": played
    }

def validate_score_input(team_id: str, score: int) -> dict:
    """Valida la entrada de resultado."""
    if not isinstance(team_id, str) or not team_id.strip():
        # strip() -> cadena vacia significa false, y cambia a true
        raise ValueError("El team_id debe ser un string válido.")
    if not isinstance(score, int) or score < 0:
        raise ValueError("El score debe ser un número entero no negativo.")
    return {"team_id": team_id, "score": score}
