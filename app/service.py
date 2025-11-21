import re
from typing import Dict, Any, List
from .fixture import generate_fixture_recursive, build_matches_from_rounds


SCORE_RE = re.compile(r'^\s*(\d+)\s*-\s*(\d+)\s*$')


def generate_matches_from_teams(teams: List[Dict[str, str]]):
    """Devuelve lista de matches (dict) basada en team['id']"""
    ids = [t["id"] for t in teams]
    names = [t["name"] for t in teams]
    rounds = generate_fixture_recursive(ids, names)
    return build_matches_from_rounds(rounds)


def record_result(state: Dict[str, Any], match_id: str, score: str) -> Dict[str, Any]:
    """Registra/actualiza un resultado; valida formato."""
    m = next((x for x in state["matches"] if x["id"] == match_id), None)
    if m is None:
        raise ValueError("Match not found")
    mo = SCORE_RE.match(score)
    if not mo:
        raise ValueError("Invalid score format. Expected e.g. '2-1'")
    hg = int(mo.group(1))
    ag = int(mo.group(2))
    m["home_goals"] = hg
    m["away_goals"] = ag
    m["played"] = True
    return m  # devolvemos el partido actualizado

def compute_standings(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Calcula la tabla a partir de matches jugados (recalcula todo)."""
    # inicializar stats
    stats = {}
    for t in state.get("teams", []):
        stats[t["id"]] = {
            "team_id": t["id"],
            "team_name": t["name"],
            "PJ": 0, "PG": 0, "PE": 0, "PP": 0,
            "GF": 0, "GC": 0, "GD": 0, "PTS": 0
        }

    for m in state.get("matches", []):
        if not m.get("played"):
            continue
        home = m["home"]
        away = m["away"]
        hg = m["home_goals"]
        ag = m["away_goals"]
        if home not in stats or away not in stats:
            # partido con equipo inexistente (posible si borraron equipos) -> saltar
            continue
        stats[home]["PJ"] += 1
        stats[away]["PJ"] += 1
        stats[home]["GF"] += hg
        stats[home]["GC"] += ag
        stats[away]["GF"] += ag
        stats[away]["GC"] += hg

        if hg > ag:
            stats[home]["PG"] += 1
            stats[home]["PTS"] += 3
            stats[away]["PP"] += 1
        elif hg < ag:
            stats[away]["PG"] += 1
            stats[away]["PTS"] += 3
            stats[home]["PP"] += 1
        else:
            stats[home]["PE"] += 1
            stats[away]["PE"] += 1
            stats[home]["PTS"] += 1
            stats[away]["PTS"] += 1

    for s in stats.values():
        s["GD"] = s["GF"] - s["GC"]

    # ordenar: PTS desc, GD desc, GF desc, team_name asc
    ordered = sorted(stats.values(), key=lambda x: (-x["PTS"], -x["GD"], -x["GF"], x["team_name"]))
    return ordered