# app/storage.py
"""
Módulo de persistencia para almacenamiento del estado en archivos JSON.

Gestiona:
- Lectura del estado desde archivo
- Escritura atómica del estado (thread-safe)
- Inicialización de estructuras de datos
"""

import json
import os
import tempfile
import threading
from typing import Dict, Any


# Ruta donde se almacena el estado del aplicación
STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "state.json")

# Lock para sincronización entre threads (escritura atómica)
_lock = threading.Lock()


def load_state(path: str = STATE_PATH) -> Dict[str, Any]:
    """
    Carga el estado del aplicación desde el archivo JSON.
    
    Si el archivo no existe, devuelve un estado inicial vacío.
    Crea el directorio 'data' si no existe.
    
    Args:
        path: Ruta del archivo JSON de estado (por defecto STATE_PATH)
    
    Returns:
        Diccionario con estructura {'teams': list, 'matches': list}
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    if not os.path.exists(path):
        return {"teams": [], "matches": []}
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: Dict[str, Any], path: str = STATE_PATH) -> None:
    """
    Guarda el estado en el archivo JSON de forma atómica y thread-safe.
    
    Utiliza:
    - Lock para sincronización entre threads
    - Archivo temporal para evitar corrupción en caso de error
    - Reemplazo atómico (os.replace) para mayor seguridad
    
    Args:
        state: Diccionario de estado a guardar
        path: Ruta del archivo JSON de destino (por defecto STATE_PATH)
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with _lock:
        # Crear archivo temporal
        fd, tmp_path = tempfile.mkstemp(
            dir=os.path.dirname(path),
            prefix="tmp_state_",
            suffix=".json"
        )
        
        try:
            # Escribir en archivo temporal
            with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
                json.dump(state, tmpf, ensure_ascii=False, indent=2)
            
            # Reemplazo atómico
            os.replace(tmp_path, path)
        finally:
            # Limpiar archivo temporal si algo falla
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
