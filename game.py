import os
import time
import random
import keyboard
import threading
from reprint import output
from map import generate_map, move_player, interact, draw_field, interaction_log, CONSOLE_HEIGHT, CONSOLE_WIDTH, \
    wrap_text
from classes import Warrior, Mage, Archer, Herbalist, Blacksmith, Trader, WanderingWizard, Imp, Necromancer, Boss, \
    Potion

# Глобальная переменная для игрока
player = None
# Переменная для отслеживания состояния торговли
is_trading = False


def display_game_over():
    """Отображает экран Game Over."""
    os.system('cls' if os.name == 'nt' else 'clear')
    game_over_message = "Game Over"
    # Центрируем сообщение по горизонтали и вертикали
    vertical_center = CONSOLE_HEIGHT // 2
    horizontal_center = (CONSOLE_WIDTH - len(game_over_message)) // 2
    for i in range(CONSOLE_HEIGHT):
        if i == vertical_center:
            print(" " * horizontal_center + game_over_message)
        else:
            print()
    time.sleep(3)
    exit(0)


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

    # Даём игроку начальные деньги и зелья для теста
    player.money = 50
    player.health_potions.append(Potion("Health Potion", 20))
    player.mana_potions.append(Potion("Mana Potion", 20))


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
        f"Money: {player.money}",  # Добавляем деньги
        f"Health Potions: {len(player.health_potions)}",  # Количество зелий здоровья
        f"Mana Potions: {len(player.mana_potions)}",  # Количество зелий маны
        f"Weapon: {getattr(player, 'weapon', 'None')}",
        f"Spells: {', '.join(player.spells) if hasattr(player, 'spells') and player.spells else 'None'}"
    ]

    return stats[line - 1] if 1 <= line <= len(stats) else ""


def get_interaction_log(line):
    if line <= 0 or line > len(interaction_log):
        return ""
    return interaction_log[line - 1]


def interact_with_entity(action, entity=None):
    global player, is_trading
    if action == "create_monster":
        # Создаём нового монстра
        monster_types = [Imp, Necromancer, Boss]
        return random.choice(monster_types)()
    elif action == "create_npc":
        # Создаём нового NPC
        npc_types = [Herbalist, Blacksmith, Trader, WanderingWizard]
        npc = random.choice(npc_types)()
        # Если это Травник, добавляем зелье для передачи
        if isinstance(npc, Herbalist):
            npc.items.append(Potion("Health Potion", 20))
        return npc
    elif action == "monster" and entity:
        # Бой с монстром
        damage = random.randint(5, 15)
        if isinstance(player, Warrior):
            msg = player.attack(entity.name, damage)
        elif isinstance(player, Mage):
            msg = player.cast_spell('Magic Bolt', entity.name, damage)
        elif isinstance(player, Archer):
            msg = player.attack(entity.name, damage)
        entity.health -= damage
        # Учитываем бонусный урон от характеристик
        if isinstance(player, Warrior):
            entity.health -= player.strength
        elif isinstance(player, Mage):
            entity.health -= player.intellect * 2
        elif isinstance(player, Archer):
            entity.health -= player.agility
        msg += f" {entity.name} осталось {entity.health} HP."

        if entity.health > 0:
            # Монстр отвечает
            monster_damage = random.randint(3, 10)
            # Шанс уклонения игрока зависит от agility (agility * 2%)
            dodge_chance = player.agility * 2
            msg += f" {entity.attack(player, monster_damage, dodge_chance)}"
            msg += f" Вам осталось {player.health} HP."

            if player.health < 1:  # Условие на < 1
                msg = "Вы погибли! Игра окончена."
                display_game_over()
        else:
            # Монстр побеждён, дропаем деньги
            dropped_money = random.randint(5, 20)
            player.money += dropped_money
            msg += f" {entity.name} побеждён! Вы получили {dropped_money} монет."

        return msg
    elif action == "npc" and entity:
        # Взаимодействие с NPC
        if not is_trading:
            msg = entity.scream()
            if isinstance(entity, (Herbalist, Trader, Blacksmith, WanderingWizard)):
                msg += " Хотите взаимодействовать? Нажмите 'e' ещё раз."
                is_trading = True
            return msg
        else:
            # Взаимодействие с NPC
            if isinstance(entity, Herbalist):
                # Травник передаёт зелье здоровья
                potion_name = "Health Potion"
                msg = entity.job(player, potion_name)
            elif isinstance(entity, Trader):
                # Торговец продаёт зелья
                item_name = random.choice(["Health Potion", "Mana Potion"])
                price = 10
                msg = entity.sell_item(player, item_name, price)
            elif isinstance(entity, Blacksmith):
                # Кузнец продаёт меч
                weapon_name = "Меч"
                price = 15
                msg = entity.sell_weapon(player, weapon_name, price)
            elif isinstance(entity, WanderingWizard):
                # Волшебник продаёт заклинание
                spell_name = "Fireball"
                price = 20
                msg = entity.sell_spell(player, spell_name, price)
            else:
                msg = "Этот NPC не торгует."
            is_trading = False
            return msg
    return "Ничего не произошло."


def use_health_potion():
    """Использовать зелье здоровья."""
    msg = player.use_health_potion()
    interaction_log.clear()
    wrapped_msgs = wrap_text(msg, 63 - 1)
    interaction_log.extend(wrapped_msgs)


def use_mana_potion():
    """Использовать зелье маны."""
    msg = player.use_mana_potion()
    interaction_log.clear()
    wrapped_msgs = wrap_text(msg, 63 - 1)
    interaction_log.extend(wrapped_msgs)


def main():
    choose_class()
    generate_map()

    with output(initial_len=CONSOLE_HEIGHT, interval=0) as out:
        thread = threading.Thread(target=draw_field, args=(out, get_player_stats, get_interaction_log))
        thread.start()

        keyboard.on_press_key("w", lambda _: move_player('w'))
        keyboard.on_press_key("s", lambda _: move_player('s'))
        keyboard.on_press_key("a", lambda _: move_player('a'))
        keyboard.on_press_key("d", lambda _: move_player('d'))
        keyboard.on_press_key("e", lambda _: interact(interact_with_entity))
        keyboard.on_press_key("h", lambda _: use_health_potion())  # Использовать зелье здоровья
        keyboard.on_press_key("m", lambda _: use_mana_potion())  # Использовать зелье маны
        keyboard.on_press_key("q", lambda _: exit(0))

        thread.join()


if __name__ == "__main__":
    main()
