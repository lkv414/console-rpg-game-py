import os
import time
import random
import keyboard
import threading
import logging
from reprint import output
from map import generate_map, move_player, interact, draw_field_with_menu, interaction_log, CONSOLE_HEIGHT, CONSOLE_WIDTH, wrap_text, spawn_quest_target, player_x, player_y, VIEW_WIDTH, VIEW_HEIGHT, MAP_WIDTH, MAP_HEIGHT, EMPTY, entity_positions, player_class, WARRIOR_SKIN, MAGE_SKIN, ARCHER_SKIN, IMP_SKIN, NECROMANCER_SKIN, BOSS_SKIN, HERBALIST_SKIN, TRADER_SKIN, BLACKSMITH_SKIN, WIZARD_SKIN, CITY_SKIN, BORDER, LOG_HEIGHT, DIVIDER, STATS_WIDTH
from classes import Warrior, Mage, Archer, Herbalist, Blacksmith, Trader, WanderingWizard, Imp, Necromancer, Boss, Potion, Quest
from colorama import init, Fore, Style
from save_load import save_game, load_game
import state

init(autoreset=True)

logging.basicConfig(filename='game_errors.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')

player = None
is_interacting = False  # Флаг для предотвращения повторных взаимодействий

def display_game_over():
    import state
    state.game_state = "game_over"
    # draw_field_with_menu сам завершит поток

def choose_class():
    """Позволяет игроку выбрать класс персонажа."""
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
    os.system('cls' if os.name == 'nt' else 'clear')

    player.money = 50
    player.health_potions.append(Potion("Health Potion", 20))
    player.mana_potions.append(Potion("Mana Potion", 20))

def save_player_state():
    """Сохраняет текущее состояние игрока в файл savegame.json."""
    state_data = {
        'player': {
            'name': player.name,
            'class': player.__class__.__name__,
            'health': player.health,
            'mana': player.mana,
            'strength': player.strength,
            'agility': player.agility,
            'intellect': player.intellect,
            'experience': player.experience,
            'level': player.level,
            'money': player.money,
            'health_potions': len(player.health_potions),
            'mana_potions': len(player.mana_potions),
            'weapon': getattr(player, 'weapon', None),
            'spells': getattr(player, 'spells', []),
        }
    }
    save_game(state_data)

def load_player_state():
    """Загружает состояние игрока из файла savegame.json."""
    try:
        state_data = load_game()
        if state_data and 'player' in state_data:
            p = state_data['player']
            if p['class'] == 'Warrior':
                cls = Warrior
            elif p['class'] == 'Mage':
                cls = Mage
            elif p['class'] == 'Archer':
                cls = Archer
            else:
                cls = Warrior
            global player
            player = cls(name=p['name'])
            player.health = p['health']
            player.mana = p['mana']
            player.strength = p['strength']
            player.agility = p['agility']
            player.intellect = p['intellect']
            player.experience = p['experience']
            player.level = p['level']
            player.money = p['money']
            player.health_potions = [Potion("Health Potion", 20)] * p['health_potions']
            player.mana_potions = [Potion("Mana Potion", 20)] * p['mana_potions']
            if hasattr(player, 'weapon'):
                player.weapon = p['weapon']
            if hasattr(player, 'spells'):
                player.spells = p['spells']
    except Exception as e:
        logging.error(f"Ошибка при загрузке состояния игрока: {e}")

def get_player_stats(line):
    """Возвращает строку со статистикой игрока для отображения."""
    if player is None:
        return ""

    stats = [
        Style.BRIGHT + Fore.GREEN + f"Name: {player.name}",
        Style.BRIGHT + Fore.CYAN + f"Class: {player.__class__.__name__}",
        Style.BRIGHT + Fore.RED + f"Health: {player.health}",
        Style.BRIGHT + Fore.BLUE + f"Mana: {player.mana}",
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
        f"Quest: {state.current_quest.name if state.current_quest else 'None'}"
    ]

    return stats[line - 1] if 1 <= line <= len(stats) else ""

def get_interaction_log(line):
    """Возвращает строку из журнала взаимодействий."""
    if line <= 0 or line > len(interaction_log):
        return ""
    return interaction_log[line - 1]

def interact_with_entity(action, entity=None):
    """Обрабатывает взаимодействие игрока с сущностями."""
    global player
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
            if state.current_quest and state.current_quest.target == entity.name:
                reward = state.current_quest.complete(player)
                msg += f" {reward}"
                state.current_quest = None

        return msg
    elif action == "npc" and entity:
        if not state.is_trading:
            msg = entity.scream()
            if isinstance(entity, (Herbalist, Trader, Blacksmith, WanderingWizard)):
                msg += " Хотите взаимодействовать? Нажмите 'e' ещё раз."
                state.is_trading = True
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
            state.is_trading = False
            return msg
    elif action == "city":
        if not state.is_trading:
            state.city_choice_state = "awaiting_choice"
            msg = "Добро пожаловать в город! Выберите действие: 'k' - Квесты, 'b' - Биржа"
            state.is_trading = True
            return msg
        else:
            if state.city_choice_state == "awaiting_choice":
                msg = "Ожидаю выбора: 'k' - Квесты, 'b' - Биржа"
                return msg
            elif state.city_choice_state == "quests":
                if state.quests_list is None:
                    state.quests_list = [
                        Quest("Убить Беса", "Imp", 50),
                        Quest("Сразить Некроманта", "Некромант", 100),
                        Quest("Победить Короля Бесов", "Король Бесов", 200)
                    ]
                msg = "Доступные квесты:\n"
                for idx, quest in enumerate(state.quests_list, 1):
                    msg += f"{idx}. {quest.name} (Цель: {quest.target}, Награда: {quest.reward} монет)\n"
                msg += "Выберите квест: '1', '2', '3'"
                return msg
            elif state.city_choice_state == "exchange":
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
                state.city_choice_state = None
                state.is_trading = False
                return msg
    return "Ничего не произошло."

def select_quests():
    """Выбор квестов в городе."""
    if state.city_choice_state == "awaiting_choice":
        state.city_choice_state = "quests"
        interaction_log.clear()
        wrapped_msgs = wrap_text("Вы выбрали квесты. Выберите квест: '1', '2', '3'", 63 - 1)
        interaction_log.extend(wrapped_msgs)

def select_exchange():
    """Выбор биржи в городе."""
    if state.city_choice_state == "awaiting_choice":
        state.city_choice_state = "exchange"
        interaction_log.clear()
        wrapped_msgs = wrap_text("Вы выбрали биржу. Выберите предмет: '1', '2', '3'", 63 - 1)
        interaction_log.extend(wrapped_msgs)

def select_quest_or_item(key):
    """Обрабатывает выбор квеста или предмета на бирже."""
    # Обработка только если активен выбор квеста или биржи
    if state.city_choice_state == "quests":
        if state.quests_list is None:
            return
        try:
            choice = int(key) - 1
            if 0 <= choice < len(state.quests_list):
                state.current_quest = state.quests_list[choice]
                spawn_quest_target(state.current_quest.target)
                msg = f"Вы взяли квест: {state.current_quest.name}. Убейте {state.current_quest.target} за {state.current_quest.reward} монет. Враг появился неподалеку!"
                interaction_log.clear()
                wrapped_msgs = wrap_text(msg, 63 - 1)
                interaction_log.extend(wrapped_msgs)
                state.city_choice_state = None
                state.is_trading = False
                state.quests_list = None
            else:
                interaction_log.clear()
                wrapped_msgs = wrap_text("Неверный выбор квеста.", 63 - 1)
                interaction_log.extend(wrapped_msgs)
        except ValueError:
            interaction_log.clear()
            wrapped_msgs = wrap_text("Пожалуйста, используйте '1', '2', '3'.", 63 - 1)
            interaction_log.extend(wrapped_msgs)
    elif state.city_choice_state == "exchange":
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
                state.city_choice_state = None
                state.is_trading = False
            else:
                interaction_log.clear()
                wrapped_msgs = wrap_text("Неверный выбор предмета.", 63 - 1)
                interaction_log.extend(wrapped_msgs)
        except ValueError:
            interaction_log.clear()
            wrapped_msgs = wrap_text("Пожалуйста, используйте '1', '2', '3'.", 63 - 1)
            interaction_log.extend(wrapped_msgs)

def use_health_potion():
    """Использует зелье здоровья."""
    msg = player.use_health_potion()
    interaction_log.clear()
    wrapped_msgs = wrap_text(msg, 63 - 1)
    interaction_log.extend(wrapped_msgs)

def use_mana_potion():
    """Использует зелье маны."""
    msg = player.use_mana_potion()
    interaction_log.clear()
    wrapped_msgs = wrap_text(msg, 63 - 1)
    interaction_log.extend(wrapped_msgs)

def on_press_e():
    """Обрабатывает нажатие клавиши E для взаимодействия."""
    global is_interacting
    if not is_interacting:
        is_interacting = True
        interact(interact_with_entity)

def on_release_e(_):
    """Обрабатывает отпускание клавиши E."""
    global is_interacting
    is_interacting = False

def on_press_esc():
    if state.game_state == "playing":
        state.game_state = "paused"

def on_press_menu_key(key=None):
    # Если key не передан, определяем его через keyboard.get_hotkey_name()
    if key is None:
        key = keyboard.get_hotkey_name()
    # Если в меню паузы
    if state.game_state == "paused":
        if key == "1":
            state.game_state = "playing"
        elif key == "2":
            state.game_state = "help"
        elif key == "3":
            state.game_state = "exit"
    # Если в справке
    elif state.game_state == "help":
        if key == "1":
            state.game_state = "playing"
    # Если в режиме выбора квеста/биржи — делегируем в select_quest_or_item
    elif state.city_choice_state in ("quests", "exchange"):
        select_quest_or_item(key)

def main():
    """Основная функция игры."""
    choose_class()
    generate_map()

    with output(initial_len=CONSOLE_HEIGHT, interval=0) as out:
        thread = threading.Thread(target=draw_field_with_menu, args=(out, get_player_stats, get_interaction_log), daemon=True)
        thread.start()

        # Управление движением
        keyboard.add_hotkey("w", lambda: move_player('w'))
        keyboard.add_hotkey("s", lambda: move_player('s'))
        keyboard.add_hotkey("a", lambda: move_player('a'))
        keyboard.add_hotkey("d", lambda: move_player('d'))
        # Взаимодействие
        keyboard.add_hotkey("e", on_press_e)
        keyboard.on_release_key("e", on_release_e)
        # Использование зелий
        keyboard.add_hotkey("h", use_health_potion)
        keyboard.add_hotkey("m", use_mana_potion)
        # Сохранение и загрузка
        keyboard.add_hotkey("f5", save_player_state)
        keyboard.add_hotkey("f9", load_player_state)
        # Выбор квестов или биржи
        keyboard.add_hotkey("k", select_quests)
        keyboard.add_hotkey("b", select_exchange)
        # Универсальный обработчик для "1", "2", "3" — теперь только один
        keyboard.add_hotkey("1", lambda: on_press_menu_key("1"))
        keyboard.add_hotkey("2", lambda: on_press_menu_key("2"))
        keyboard.add_hotkey("3", lambda: on_press_menu_key("3"))
        # Пауза
        keyboard.add_hotkey("esc", on_press_esc)

        thread.join()

if __name__ == "__main__":
    main()