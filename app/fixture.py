#función
"""
Módulo para generación de fixtures deportivos usando el método round-robin.

Implementa el algoritmo de "todos contra todos" donde cada equipo juega 
exactamente una vez contra cada otro equipo, tanto como local como visitante.

Propiedades:
- Número de rondas: n-1 (donde n es el número de equipos)
- Número de partidos por equipo: n-1
- Total de partidos: n(n-1)/2
- Manejo de equipos impares: Se agrega un "BYE" (equipo virtual que descansa)
"""

from typing import List, Tuple
import uuid

# Constante que representa un equipo que descansa en una ronda
BYE = "BYE"


def rotate_teams(order: List[str]) -> List[str]:
    """
    Rota los equipos usando el método circular para generar el fixture.
    
    Algoritmo:
    - Mantiene el primer equipo fijo en su posición
    - Rota el resto de equipos hacia la derecha (el último pasa al inicio)
    - Esto asegura que no haya conflictos de repetición en emparejamientos
    
    Args:
        order: Lista de IDs o nombres de equipos
    
    Returns:
        Lista rotada con el primer elemento en la misma posición
    
    Ejemplo:
        >>> rotate_teams(['A', 'B', 'C', 'D'])
        ['A', 'D', 'B', 'C']
    """
    if len(order) <= 1:
        return order
    
    first = order[0]
    rest = order[1:]
    # Rotar el resto hacia la derecha: último elemento al inicio
    new_rest = [rest[-1]] + rest[:-1]
    
    return [first] + new_rest


def generate_fixture_recursive(
    team_ids: List[str],
    team_names: List[str]
) -> List[List[Tuple[str, str, str, str]]]:
    """
    Genera un fixture completo de todos contra todos (round-robin) recursivamente.
    
    Algoritmo de funcionamiento:
    1. Si hay número impar de equipos, agrega un "BYE" para hacer el número par
    2. En cada ronda, empareja: primero con último, segundo con penúltimo, etc.
    3. Rota todos los equipos para la siguiente ronda (excepto el primero que es fijo)
    4. Repite recursivamente hasta completar n-1 rondas
    
    Complejidad:
    - Temporal: O(n²) - n rondas, cada ronda genera n/2 partidos
    - Espacial: O(n²) - almacena todos los partidos
    
    Args:
        team_ids: Lista de IDs únicos de los equipos
        team_names: Lista de nombres de equipos (debe tener mismo índice que team_ids)
    
    Returns:
        Lista de rondas: cada ronda es una lista de tuplas
        (home_id, away_id, home_name, away_name)
    
    Ejemplo:
        >>> generate_fixture_recursive(['t1', 't2', 't3'], ['TeamA', 'TeamB', 'TeamC'])
        # Devuelve 2 rondas (n-1 donde n=3) con 3 partidos totales
    """
    # Clonar listas para evitar mutación de entrada
    ids = list(team_ids)
    names = list(team_names)

    # Si hay número impar, agregar BYE (equipo que descansa)
    if len(ids) % 2 == 1:
        ids.append(BYE)
        names.append(BYE)

    # Calcular número total de rondas
    total_rounds = len(ids) - 1
    
    # Acumulador de todas las rondas generadas
    rounds: List[List[Tuple[str, str, str, str]]] = []

    def helper(current_ids: List[str], current_names: List[str], rounds_left: int) -> None:
        """
        Función recursiva interna que construye las rondas.
        
        Args:
            current_ids: IDs de equipos en orden actual
            current_names: Nombres de equipos en orden actual
            rounds_left: Número de rondas aún por generar
        """
        if rounds_left == 0:
            return
        
        # Crear pares para esta ronda
        pairs: List[Tuple[str, str, str, str]] = []
        n = len(current_ids)

        # Emparejar: primero[i] vs último[i]
        for i in range(n // 2):
            pairs.append((
                current_ids[i],
                current_ids[n - 1 - i],
                current_names[i],
                current_names[n - 1 - i]
            ))

        # Agregar esta ronda a la lista de resultados
        rounds.append(pairs)

        # Rotar para la siguiente ronda
        next_ids = rotate_teams(current_ids)
        next_names = rotate_teams(current_names)

        # Llamada recursiva
        helper(next_ids, next_names, rounds_left - 1)

    # Iniciar generación recursiva
    helper(ids, names, total_rounds)
    return rounds


def build_matches_from_rounds(
    rounds: List[List[Tuple[str, str, str, str]]]
) -> List[dict]:
    """
    Convierte las rondas (tuplas) en diccionarios de partidos con metadatos.
    
    Características:
    - Filtra automáticamente partidos con "BYE" (equipos que descansan)
    - Asigna UUID único a cada partido
    - Inicializa campos de resultado vacíos
    - Marca partidos como no jugados
    
    Args:
        rounds: Lista de rondas generadas por generate_fixture_recursive()
    
    Returns:
        Lista de diccionarios con estructura:
        {
            'id': str (UUID único),
            'home': str (ID local),
            'away': str (ID visitante),
            'home_name': str (nombre local),
            'away_name': str (nombre visitante),
            'round': int (número de ronda, 1-indexado),
            'home_goals': None (se llena al registrar resultado),
            'away_goals': None (se llena al registrar resultado),
            'played': False (se cambia a True cuando se registra resultado)
        }
    
    Ejemplo:
        >>> rounds = [[(id1, id2, 'A', 'B')]]
        >>> matches = build_matches_from_rounds(rounds)
        >>> len(matches)
        1
    """
    matches = []
    
    for round_idx, pairs in enumerate(rounds, start=1):
        for home_id, away_id, home_name, away_name in pairs:
            # Ignorar partidos donde algún equipo es BYE (está descansando)
            if home_id == BYE or away_id == BYE:
                continue
            
            # Crear objeto partido
            matches.append({
                "id": uuid.uuid4().hex,
                "home": home_id,
                "away": away_id,
                "home_name": home_name,
                "away_name": away_name,
                "round": round_idx,
                "home_goals": None,
                "away_goals": None,
                "played": False
            })
    
    return matches
