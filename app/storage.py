# app/storage.py
import json
import os
import tempfile
import threading
from typing import Dict, Any


# Se define la ruta en donde se guarda el json y se crea un candado (lock) para evitar que se escriba el archivo al mismo tiempo 
STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "state.json")
_lock = threading.Lock()



def load_state(path: str = STATE_PATH) -> Dict[str, Any]:
    # Se verifica que la carpeta en donde se guarda el json exista
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Si no existe:
    if not os.path.exists(path):
        return {"teams": [], "matches": []}
    # Si existe, lo abre, lo lee y lo devuelve en el formato Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state: Dict[str, Any], path: str = STATE_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _lock:
        fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path), prefix="tmp_state_", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
                json.dump(state, tmpf, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)  # atomic replace
        finally:
            # if tmp_path still exists and error, try remove
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass