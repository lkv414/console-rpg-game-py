import os
import time
import random
import keyboard
import threading
from reprint import output
from map import generate_map, move_player, interact, draw_field, interaction_log, CONSOLE_HEIGHT, CONSOLE_WIDTH, wrap_text, spawn_quest_target
from classes import Warrior, Mage, Archer, Herbalist, Blacksmith, Trader, WanderingWizard, Imp, Necromancer, Boss, Potion, Quest

# Глобальные переменные
player = None
is_trading = False
current_quest = None
city_choice_state = None
quests_list = None
is_interacting = False  # Флаг для предотвращения повторных взаимодействий

def display_game_over():
    os.system('cls' if os.name == 'nt' else 'clear')
    game_over_message = "Game Over"
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
        f"Money: {player.money}",
        f"Health Potions: {len(player.health_potions)}",
        f"Mana Potions: {len(player.mana_potions)}",
        f"Weapon: {getattr(player, 'weapon', 'None')}",
        f"Spells: {', '.join(player.spells) if hasattr(player, 'spells') and player.spells else 'None'}",
        f"Quest: {current_quest.name if current_quest else 'None'}"
    ]

    return stats[line - 1] if 1 <= line <= len(stats) else ""

def get_interaction_log(line):
    if line <= 0 or line > len(interaction_log):
        return ""
    return interaction_log[line - 1]

def interact_with_entity(action, entity=None):
    global player, is_trading, current_quest, city_choice_state, quests_list
    if action == "create_monster":
        monster_types = [Imp, Necromancer, Boss]
        return random.choice(monster_types)()
    elif action == "create_npc":
        npc_types = [Herbalist, Blacksmith, Trader, WanderingWizard]
        npc = random.choice(npc_types)()
        if isinstance(npc, Herbalist):
            npc.items.append(Potion("Health Potion", 20))
        return npc
    elif action == "monster" and entity:
        damage = random.randint(5, 15)
        if isinstance(player, Warrior):
            msg = player.attack(entity.name, damage)
        elif isinstance(player, Mage):
            msg = player.cast_spell('Magic Bolt', entity.name, damage)
        elif isinstance(player, Archer):
            msg = player.attack(entity.name, damage)
        entity.health -= damage
        if isinstance(player, Warrior):
            entity.health -= player.strength
        elif isinstance(player, Mage):
            entity.health -= player.intellect * 2
        elif isinstance(player, Archer):
            entity.health -= player.agility
        msg += f" {entity.name} осталось {entity.health} HP."

        if entity.health > 0:
            monster_damage = random.randint(3, 10)
            dodge_chance = player.agility * 2
            msg += f" {entity.attack(player, monster_damage, dodge_chance)}"
            msg += f" Вам осталось {player.health} HP."
            if player.health < 1:
                msg = "Вы погибли! Игра окончена."
                display_game_over()
        else:
            dropped_money = random.randint(5, 20)
            player.money += dropped_money
            msg += f" {entity.name} побеждён! Вы получили {dropped_money} монет."
            if current_quest and current_quest.target == entity.name:
                reward = current_quest.complete(player)
                msg += f" {reward}"
                current_quest = None

        return msg
    elif action == "npc" and entity:
        if not is_trading:
            msg = entity.scream()
            if isinstance(entity, (Herbalist, Trader, Blacksmith, WanderingWizard)):
                msg += " Хотите взаимодействовать? Нажмите 'e' ещё раз."
                is_trading = True
            return msg
        else:
            if isinstance(entity, Herbalist):
                potion_name = "Health Potion"
                msg = entity.job(player, potion_name)
            elif isinstance(entity, Trader):
                item_name = random.choice(["Health Potion", "Mana Potion"])
                price = 10
                msg = entity.sell_item(player, item_name, price)
            elif isinstance(entity, Blacksmith):
                weapon_name = "Меч"
                price = 15
                msg = entity.sell_weapon(player, weapon_name, price)
            elif isinstance(entity, WanderingWizard):
                spell_name = "Fireball"
                price = 20
                msg = entity.sell_spell(player, spell_name, price)
            else:
                msg = "Этот NPC не торгует."
            is_trading = False
            return msg
    elif action == "city":
        if not is_trading:
            city_choice_state = "awaiting_choice"
            msg = "Добро пожаловать в город! Выберите действие: 'k' - Квесты, 'b' - Биржа"
            is_trading = True
            return msg
        else:
            if city_choice_state == "awaiting_choice":
                msg = "Ожидаю выбора: 'k' - Квесты, 'b' - Биржа"
                return msg
            elif city_choice_state == "quests":
                if quests_list is None:
                    quests_list = [
                        Quest("Убить Беса", "Imp", 50),
                        Quest("Сразить Некроманта", "Некромант", 100),
                        Quest("Победить Короля Бесов", "Король Бесов", 200)
                    ]
                msg = "Доступные квесты:\n"
                for idx, quest in enumerate(quests_list, 1):
                    msg += f"{idx}. {quest.name} (Цель: {quest.target}, Награда: {quest.reward} монет)\n"
                msg += "Выберите квест: '1', '2', '3'"
                return msg
            elif city_choice_state == "exchange":
                items = [
                    {"name": "Меч", "price": random.randint(10, 30)},
                    {"name": "Лук", "price": random.randint(15, 35)},
                    {"name": "Health Potion", "price": random.randint(5, 15)}
                ]
                msg = "На бирже доступно:\n"
                for idx, item in enumerate(items, 1):
                    msg += f"{idx}. {item['name']} - {item['price']} монет\n"
                msg += "Выберите предмет: '1', '2', '3'"
                return msg
            else:
                msg = "Неизвестное состояние выбора."
                city_choice_state = None
                is_trading = False
                return msg
    return "Ничего не произошло."

def select_quests():
    global city_choice_state
    if city_choice_state == "awaiting_choice":
        city_choice_state = "quests"
        interaction_log.clear()
        wrapped_msgs = wrap_text("Вы выбрали квесты. Выберите квест: '1', '2', '3'", 63 - 1)
        interaction_log.extend(wrapped_msgs)

def select_exchange():
    global city_choice_state
    if city_choice_state == "awaiting_choice":
        city_choice_state = "exchange"
        interaction_log.clear()
        wrapped_msgs = wrap_text("Вы выбрали биржу. Выберите предмет: '1', '2', '3'", 63 - 1)
        interaction_log.extend(wrapped_msgs)

def select_quest_or_item(key):
    global city_choice_state, current_quest, is_trading, quests_list, player
    if city_choice_state == "quests":
        if quests_list is None:
            return
        try:
            choice = int(key) - 1
            if 0 <= choice < len(quests_list):
                current_quest = quests_list[choice]
                spawn_quest_target(current_quest.target)
                msg = f"Вы взяли квест: {current_quest.name}. Убейте {current_quest.target} за {current_quest.reward} монет. Враг появился неподалеку!"
                interaction_log.clear()
                wrapped_msgs = wrap_text(msg, 63 - 1)
                interaction_log.extend(wrapped_msgs)
                city_choice_state = None
                is_trading = False
                quests_list = None
            else:
                interaction_log.clear()
                wrapped_msgs = wrap_text("Неверный выбор квеста.", 63 - 1)
                interaction_log.extend(wrapped_msgs)
        except ValueError:
            interaction_log.clear()
            wrapped_msgs = wrap_text("Пожалуйста, используйте '1', '2', '3'.", 63 - 1)
            interaction_log.extend(wrapped_msgs)
    elif city_choice_state == "exchange":
        items = [
            {"name": "Меч", "price": random.randint(10, 30)},
            {"name": "Лук", "price": random.randint(15, 35)},
            {"name": "Health Potion", "price": random.randint(5, 15)}
        ]
        try:
            choice = int(key) - 1
            if 0 <= choice < len(items):
                item = items[choice]
                if player.money >= item["price"]:
                    player.money -= item["price"]
                    if "Potion" in item["name"]:
                        player.health_potions.append(Potion(item["name"], 20))
                    else:
                        player.weapon = item["name"]
                    msg = f"Вы купили {item['name']} за {item['price']} монет."
                else:
                    msg = "Недостаточно денег!"
                interaction_log.clear()
                wrapped_msgs = wrap_text(msg, 63 - 1)
                interaction_log.extend(wrapped_msgs)
                city_choice_state = None
                is_trading = False
            else:
                interaction_log.clear()
                wrapped_msgs = wrap_text("Неверный выбор предмета.", 63 - 1)
                interaction_log.extend(wrapped_msgs)
        except ValueError:
            interaction_log.clear()
            wrapped_msgs = wrap_text("Пожалуйста, используйте '1', '2', '3'.", 63 - 1)
            interaction_log.extend(wrapped_msgs)

def use_health_potion():
    msg = player.use_health_potion()
    interaction_log.clear()
    wrapped_msgs = wrap_text(msg, 63 - 1)
    interaction_log.extend(wrapped_msgs)

def use_mana_potion():
    msg = player.use_mana_potion()
    interaction_log.clear()
    wrapped_msgs = wrap_text(msg, 63 - 1)
    interaction_log.extend(wrapped_msgs)

def on_press_e(_):
    global is_interacting
    if not is_interacting:
        is_interacting = True
        interact(interact_with_entity)

def on_release_e(_):
    global is_interacting
    is_interacting = False

def main():
    choose_class()
    generate_map()

    with output(initial_len=CONSOLE_HEIGHT, interval=0) as out:
        thread = threading.Thread(target=draw_field, args=(out, get_player_stats, get_interaction_log))
        thread.start()

        # Управление движением
        keyboard.on_press_key("w", lambda _: move_player('w'))
        keyboard.on_press_key("s", lambda _: move_player('s'))
        keyboard.on_press_key("a", lambda _: move_player('a'))
        keyboard.on_press_key("d", lambda _: move_player('d'))
        # Взаимодействие
        keyboard.on_press_key("e", on_press_e)
        keyboard.on_release_key("e", on_release_e)
        # Использование зелий
        keyboard.on_press_key("h", lambda _: use_health_potion())
        keyboard.on_press_key("m", lambda _: use_mana_potion())
        # Выбор квестов или биржи
        keyboard.on_press_key("k", lambda _: select_quests())
        keyboard.on_press_key("b", lambda _: select_exchange())
        # Выбор квеста или предмета
        keyboard.on_press_key("1", lambda _: select_quest_or_item("1"))
        keyboard.on_press_key("2", lambda _: select_quest_or_item("2"))
        keyboard.on_press_key("3", lambda _: select_quest_or_item("3"))

        thread.join()

if __name__ == "__main__":
    main()