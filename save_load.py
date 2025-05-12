# Модуль для сохранения и загрузки состояния игры
import json

def save_game(state, filename="savegame.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_game(filename="savegame.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
