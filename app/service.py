"""
Módulo de lógica de negocio para gestión de torneos de fútbol.

Responsabilidades:
- Generación de fixtures (todos contra todos)
- Registro de resultados de partidos
- Cálculo de tabla de posiciones
"""

import re
from typing import Dict, Any, List
from .fixture import generate_fixture_recursive, build_matches_from_rounds


# Patrón para validar formato de score: "goles_local-goles_visitante"
SCORE_PATTERN = re.compile(r'^\s*(\d+)\s*-\s*(\d+)\s*$')


def generate_matches_from_teams(teams: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Genera una lista de partidos basada en los equipos proporcionados.
    Utiliza el método round-robin (todos contra todos).
    
    Args:
        teams: Lista de diccionarios con estructura {'id': str, 'name': str, ...}
    
    Returns:
        Lista de partidos con estructura:
        {'id': str, 'home': str, 'away': str, 'home_name': str, 'away_name': str, 
         'round': int, 'home_goals': None, 'away_goals': None, 'played': False}
    """
    team_ids = [team["id"] for team in teams]
    team_names = [team["name"] for team in teams]
    rounds = generate_fixture_recursive(team_ids, team_names)
    return build_matches_from_rounds(rounds)


def record_result(state: Dict[str, Any], match_id: str, score: str) -> Dict[str, Any]:
    """
    Registra o actualiza el resultado de un partido específico.
    
    Args:
        state: Diccionario de estado global con 'teams' y 'matches'
        match_id: ID único del partido a actualizar
        score: String con formato "goles_local-goles_visitante" (ej: "2-1")
    
    Returns:
        Diccionario del partido actualizado con resultado
    
    Raises:
        ValueError: Si el partido no existe o el formato de score es inválido
    
    Ejemplo:
        >>> record_result(state, "abc123", "3-1")
        {'id': 'abc123', 'home': '...', 'away': '...', 'home_goals': 3, 'away_goals': 1, 'played': True}
    """
    # Buscar el partido en la lista
    match = next((m for m in state["matches"] if m["id"] == match_id), None)
    if match is None:
        raise ValueError(f"Partido con ID '{match_id}' no encontrado")
    
    # Validar y parsear el score
    score_match = SCORE_PATTERN.match(score)
    if not score_match:
        raise ValueError(
            f"Formato de score inválido: '{score}'. "
            f"Usa el formato 'goles_local-goles_visitante' (ej: '2-1')"
        )
    
    home_goals = int(score_match.group(1))
    away_goals = int(score_match.group(2))
    
    # Registrar resultado en el partido
    match["home_goals"] = home_goals
    match["away_goals"] = away_goals
    match["played"] = True
    
    return match


def compute_standings(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Calcula la tabla de posiciones a partir de todos los partidos jugados.
    Se recalcula completamente cada invocación (sin cacheo).
    
    Criterios de ordenamiento:
    1. Puntos (descendente)
    2. Diferencia de goles (descendente)
    3. Goles a favor (descendente)
    4. Nombre del equipo (ascendente - orden alfabético)
    
    Args:
        state: Diccionario de estado global con 'teams' y 'matches'
    
    Returns:
        Lista de filas de tabla ordenadas con estructura:
        {'team_id': str, 'team_name': str, 'PJ': int, 'PG': int, 'PE': int, 'PP': int,
         'GF': int, 'GC': int, 'GD': int, 'PTS': int}
    
    Nomenclatura:
        PJ = Partidos Jugados
        PG = Partidos Ganados
        PE = Partidos Empatados
        PP = Partidos Perdidos
        GF = Goles a Favor
        GC = Goles en Contra
        GD = Diferencia de Goles
        PTS = Puntos
    """
    # Inicializar estadísticas para cada equipo
    standings = {}
    for team in state.get("teams", []):
        standings[team["id"]] = {
            "team_id": team["id"],
            "team_name": team["name"],
            "PJ": 0,  # Partidos jugados
            "PG": 0,  # Partidos ganados
            "PE": 0,  # Partidos empatados
            "PP": 0,  # Partidos perdidos
            "GF": 0,  # Goles a favor
            "GC": 0,  # Goles en contra
            "GD": 0,  # Diferencia de goles
            "PTS": 0  # Puntos
        }

    # Procesar todos los partidos que han sido jugados
    for match in state.get("matches", []):
        if not match.get("played"):
            continue
        
        home_id = match["home"]
        away_id = match["away"]
        home_goals = match["home_goals"]
        away_goals = match["away_goals"]
        
        # Validar que ambos equipos existan (podrían haber sido eliminados)
        if home_id not in standings or away_id not in standings:
            continue
        
        home_stats = standings[home_id]
        away_stats = standings[away_id]
        
        # Actualizar partidos jugados
        home_stats["PJ"] += 1
        away_stats["PJ"] += 1
        
        # Actualizar goles
        home_stats["GF"] += home_goals
        home_stats["GC"] += away_goals
        away_stats["GF"] += away_goals
        away_stats["GC"] += home_goals

        # Determinar resultado y asignar puntos
        if home_goals > away_goals:
            # Victoria local
            home_stats["PG"] += 1
            home_stats["PTS"] += 3
            away_stats["PP"] += 1
        elif home_goals < away_goals:
            # Victoria visitante
            away_stats["PG"] += 1
            away_stats["PTS"] += 3
            home_stats["PP"] += 1
        else:
            # Empate
            home_stats["PE"] += 1
            away_stats["PE"] += 1
            home_stats["PTS"] += 1
            away_stats["PTS"] += 1

    # Calcular diferencia de goles para cada equipo
    for stats in standings.values():
        stats["GD"] = stats["GF"] - stats["GC"]

    # Ordenar según criterios de desempate
    standings_list = sorted(
        standings.values(),
        key=lambda x: (-x["PTS"], -x["GD"], -x["GF"], x["team_name"])
    )
    
    return standings_list
