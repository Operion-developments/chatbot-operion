import os
import json
from datetime import datetime

def get_saudacao():
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return "Bom dia"
    elif 12 <= hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def load_data(filename, default=None):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        # Se o arquivo não existir ou estiver vazio, cria com o valor padrão
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(default if default is not None else {}, f)
        return default if default is not None else {}
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # Se o arquivo estiver corrompido, sobrescreve com o padrão
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(default if default is not None else {}, f)
        return default if default is not None else {}

def save_users_data(users_data):
    filepath = os.path.join(os.path.dirname(__file__), "users.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)