#función
from typing import List, Tuple
import uuid

BYE = "BYE"

def rotate_teams(order: List[str]) -> List[str]:
    """Fija el primero y rota el resto (circle method)."""
    if len(order) <= 1:
        return order
    first = order[0]
    rest = order[1:]
    new_rest = [rest[-1]] + rest[:-1]
    return [first] + new_rest

def round_pairs(order: List[str]) -> List[Tuple[str, str]]:
    """Genera pares para una ronda a partir del orden."""
    n = len(order)
    pairs = []
    for i in range(n // 2):
        a = order[i]
        b = order[n - 1 - i]
        # si alguno es BYE, lo saltamos (no se crea partido)
        if a == BYE or b == BYE:
            continue
        pairs.append((a, b))
    return pairs

def generate_fixture_recursive(team_ids: List[str], team_names: List[str]) -> List[List[Tuple[str, str, str, str]]]:
    """
    Devuelve una lista de rondas,
    cada ronda es lista de tuples (home_id, away_id).
    Implementado recursivamente.
    """
    ids = list(team_ids)
    names = list(team_names)

    if len(ids) % 2 == 1:
        ids.append(BYE)
        names.append(BYE)

    total_rounds = len(ids) - 1
    rounds: List[List[Tuple[str, str, str, str]]] = []

    def helper(current_ids: List[str], current_names: List[str], rounds_left: int):
        if rounds_left == 0:
            return
        pairs = []
        n = len(current_ids)
        for i in range(n // 2):
            pairs.append((
                current_ids[i],
                current_ids[n - 1 - i],
                current_names[i],
                current_names[n - 1 - i]
            ))
        rounds.append(pairs)
        # rotamos ambos en paralelo
        next_ids = rotate_teams(current_ids)
        next_names = rotate_teams(current_names)
        helper(next_ids, next_names, rounds_left - 1)

    helper(ids, names, total_rounds)
    return rounds

def build_matches_from_rounds(rounds: List[List[Tuple[str, str, str, str]]]):
    """Convierte rounds en dicts tipo match con id, número de ronda y nombres."""
    matches = []
    for r_idx, pairs in enumerate(rounds, start=1):
        for home_id, away_id, home_name, away_name in pairs:
            if home_id == BYE or away_id == BYE:
                continue
            matches.append({
                "id": uuid.uuid4().hex,
                "home": home_id,
                "away": away_id,
                "home_name": home_name,
                "away_name": away_name,
                "round": r_idx,
                "home_goals": None,
                "away_goals": None,
                "played": False
            })
    return matches