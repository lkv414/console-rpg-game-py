import os
import time
import keyboard
import threading
from reprint import output
from map import generate_map, move_player, interact, draw_field, VIEW_HEIGHT, CONSOLE_HEIGHT
from classes import Warrior, Mage, Archer

# Глобальная переменная для игрока
player = None

def choose_class():
    global player
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Выберите класс:")
    print("1. Warrior (Воин)")
    print("2. Mage (Маг)")
    print("3. Archer (Лучник)")
    choice = input("Введите номер класса (1-3): ").strip()
    name = input("Введите имя персонажа: ").strip()

    if choice == "1":
        player = Warrior(name=name)
    elif choice == "2":
        player = Mage(name=name)
    elif choice == "3":
        player = Archer(name=name)
    else:
        print("Неверный выбор, выбран Воин по умолчанию.")
        player = Warrior(name=name)
    print(player.scream())
    time.sleep(2)

def get_player_stats(line):
    if player is None:
        return ""

    stats = [
        f"Name: {player.name}",
        f"Class: {player.__class__.__name__}",
        f"Health: {player.health}",
        f"Mana: {player.mana}",
        f"Strength: {player.strength}",
        f"Agility: {player.agility}",
        f"Intellect: {player.intellect}",
        f"Level: {player.level}",
        f"Experience: {player.experience}",
        f"Weapon: {getattr(player, 'weapon', 'None')}",
        f"Spells: {', '.join(player.spells) if hasattr(player, 'spells') and player.spells else 'None'}"
    ]

    return stats[line - 1] if 1 <= line <= len(stats) else ""

def main():
    choose_class()
    generate_map()

    with output(initial_len=CONSOLE_HEIGHT, interval=0) as out:
        thread = threading.Thread(target=draw_field, args=(out, get_player_stats))
        thread.start()

        keyboard.on_press_key("w", lambda _: move_player('w'))
        keyboard.on_press_key("s", lambda _: move_player('s'))
        keyboard.on_press_key("a", lambda _: move_player('a'))
        keyboard.on_press_key("d", lambda _: move_player('d'))
        keyboard.on_press_key("e", lambda _: [print(msg) for msg in interact()])
        keyboard.on_press_key("q", lambda _: exit(0))

        thread.join()

if __name__ == "__main__":
    main()