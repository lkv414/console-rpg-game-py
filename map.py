import random
import time
from classes import Herbalist, Blacksmith, Trader, WanderingWizard, Imp, Necromancer, Boss, Potion
import state

# Константы
CONSOLE_WIDTH = 120
CONSOLE_HEIGHT = 29
VIEW_WIDTH = 27
VIEW_HEIGHT = 27
MAP_WIDTH = 200
MAP_HEIGHT = 200
STATS_WIDTH = 63
LOG_HEIGHT = 15
STATS_HEIGHT = 10
INTERACTION_RADIUS = 3
SPAWN_RADIUS = 5

# Символы
EMPTY = "\033[32mW\033[0m"
BORDER = "\033[30m#\033[0m"
DIVIDER = "|"

# Скины (3x3)
WARRIOR_SKIN = [
    [" ", " ", " "],
    ["/", "|", "\\"],
    ["/", " ", "\\"]
]
MAGE_SKIN = [
    [" ", "*", " "],
    ["/", "|", "\\"],
    ["/", " ", "\\"]
]
ARCHER_SKIN = [
    [" ", "^", " "],
    ["/", "|", "\\"],
    ["/", " ", "\\"]
]
IMP_SKIN = [
    [" ", "X", " "],
    ["/", "|", "\\"],
    ["/", " ", "\\"]
]
NECROMANCER_SKIN = [
    [" ", "~", " "],
    ["/", "|", "\\"],
    ["/", " ", "\\"]
]
BOSS_SKIN = [
    [" ", "#", " "],
    ["/", "|", "\\"],
    ["/", " ", "\\"]
]
HERBALIST_SKIN = [
    [" ", "@", " "],
    ["/", "|", "\\"],
    ["/", " ", "\\"]
]
TRADER_SKIN = [
    [" ", "$", " "],
    ["/", "|", "\\"],
    ["/", " ", "\\"]
]
BLACKSMITH_SKIN = [
    [" ", "&", " "],
    ["/", "|", "\\"],
    ["/", " ", "\\"]
]
WIZARD_SKIN = [
    [" ", "?", " "],
    ["/", "|", "\\"],
    ["/", " ", "\\"]
]
CITY_SKIN = [
    ["#", "#", "#"],
    ["|", "|", "|"],
    ["_", "_", "_"]
]

# Глобальные переменные
player_x, player_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
field = [[{"type": "empty", "entity": None, "skin": EMPTY} for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
interaction_log = []
current_entity = None
entity_position = None
player_class = None
entity_positions = {}  # (x, y) -> {"type": type, "entity": entity}

def wrap_text(text, width):
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1
        if current_length + word_length <= width:
            current_line.append(word)
            current_length += word_length
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word) + 1

    if current_line:
        lines.append(" ".join(current_line))

    return lines

def place_random(entity_type, count=1):
    global player_x, player_y, entity_positions
    for _ in range(count):
        while True:
            x, y = random.randint(0, MAP_WIDTH - 3), random.randint(0, MAP_HEIGHT - 3)
            can_place = True
            for i in range(3):
                for j in range(3):
                    if not (0 <= y + i < MAP_HEIGHT and 0 <= x + j < MAP_WIDTH) or \
                       field[y + i][x + j]["type"] != "empty" or \
                       (player_x <= x + j < player_x + 3 and player_y <= y + i < player_y + 3):
                        can_place = False
                        break
                if not can_place:
                    break
            if can_place:
                entity = None
                if entity_type == "imp":
                    entity = Imp()
                elif entity_type == "necromancer":
                    entity = Necromancer()
                elif entity_type == "boss":
                    entity = Boss()
                elif entity_type == "herbalist":
                    entity = Herbalist()
                    entity.items.append(Potion("Health Potion", 20))
                elif entity_type == "trader":
                    entity = Trader()
                elif entity_type == "blacksmith":
                    entity = Blacksmith()
                elif entity_type == "wizard":
                    entity = WanderingWizard()
                for i in range(3):
                    for j in range(3):
                        field[y + i][x + j] = {"type": entity_type, "entity": entity, "skin": None}
                entity_positions[(x, y)] = {"type": entity_type, "entity": entity}
                break

def spawn_quest_target(target_name):
    global player_x, player_y, entity_positions
    while True:
        offset_x = random.randint(-SPAWN_RADIUS, SPAWN_RADIUS)
        offset_y = random.randint(-SPAWN_RADIUS, SPAWN_RADIUS)
        target_x = player_x + offset_x
        target_y = player_y + offset_y

        can_place = True
        for i in range(3):
            for j in range(3):
                if not (0 <= target_x + j < MAP_WIDTH and 0 <= target_y + i < MAP_HEIGHT) or \
                   field[target_y + i][target_x + j]["type"] != "empty" or \
                   (player_x <= target_x + j < player_x + 3 and player_y <= target_y + i < player_y + 3):
                    can_place = False
                    break
            if not can_place:
                break
        if can_place:
            entity_type = "imp" if target_name == "Imp" else "necromancer" if target_name == "Некромант" else "boss"
            entity = Imp() if entity_type == "imp" else Necromancer() if entity_type == "necromancer" else Boss()
            for i in range(3):
                for j in range(3):
                    field[target_y + i][target_x + j] = {"type": entity_type, "entity": entity, "skin": None}
            entity_positions[(target_x, target_y)] = {"type": entity_type, "entity": entity}
            break

def generate_map():
    global field, player_class, entity_positions
    from game import player
    field = [[{"type": "empty", "entity": None, "skin": EMPTY} for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    player_class = player.__class__.__name__.lower()
    entity_positions = {}
    draw_person(player_x, player_y)
    place_random("imp", 5)
    place_random("necromancer", 3)
    place_random("boss", 2)
    place_random("herbalist", 3)
    place_random("trader", 3)
    place_random("blacksmith", 2)
    place_random("wizard", 2)
    place_random("city", 6)

def draw_person(x, y):
    global entity_positions
    skin = WARRIOR_SKIN if player_class == "warrior" else MAGE_SKIN if player_class == "mage" else ARCHER_SKIN
    for i in range(3):
        for j in range(3):
            if 0 <= y + i < MAP_HEIGHT and 0 <= x + j < MAP_WIDTH:
                if field[y + i][x + j]["type"] == "empty":
                    field[y + i][x + j] = {"type": "player", "entity": None, "skin": skin[i][j]}
    entity_positions[(x, y)] = {"type": "player", "entity": None}

def can_move(new_x, new_y):
    for i in range(3):
        for j in range(3):
            if not (0 <= new_x + j < MAP_WIDTH and 0 <= new_y + i < MAP_HEIGHT) or \
               field[new_y + i][new_x + j]["type"] in ["imp", "necromancer", "boss", "city", "herbalist", "trader", "blacksmith", "wizard"]:
                return False
    return True

def move_player(direction):
    global player_x, player_y, current_entity, entity_position, entity_positions
    old_x, old_y = player_x, player_y
    new_x, new_y = player_x, player_y

    if direction == 'w' and player_y > 0:
        new_y -= 1
    elif direction == 's' and player_y < MAP_HEIGHT - 3:
        new_y += 1
    elif direction == 'a' and player_x > 0:
        new_x -= 1
    elif direction == 'd' and player_x < MAP_WIDTH - 3:
        new_x += 1

    if (new_x, new_y) != (old_x, old_y) and can_move(new_x, new_y):
        for i in range(3):
            for j in range(3):
                if (0 <= old_y + i < MAP_HEIGHT and 0 <= old_x + j < MAP_WIDTH and
                    field[old_y + i][old_x + j]["type"] == "player"):
                    field[old_y + i][old_x + j] = {"type": "empty", "entity": None, "skin": EMPTY}
        if (old_x, old_y) in entity_positions:
            del entity_positions[(old_x, old_y)]
        player_x, player_y = new_x, new_y
        draw_person(player_x, player_y)
        if entity_position and not (abs(player_x - entity_position[0]) <= INTERACTION_RADIUS and abs(player_y - entity_position[1]) <= INTERACTION_RADIUS):
            current_entity = None
            entity_position = None
            if state.city_choice_state is not None:
                state.city_choice_state = None
                state.is_trading = False
                state.quests_list = None
            interaction_log.clear()
            interaction_log.append("Вы отошли от объекта.")

def interact(interact_callback):
    global interaction_log, current_entity, entity_position, entity_positions
    interactions = []
    interaction_log.clear()

    # Если уже есть текущий объект взаимодействия, работаем только с ним
    if current_entity:
        if isinstance(current_entity, (Imp, Necromancer, Boss)):
            msg = interact_callback("monster", current_entity)
            wrapped_msgs = wrap_text(msg, STATS_WIDTH - 1)
            interactions.extend(wrapped_msgs)
            if current_entity.health <= 0:
                for i in range(3):
                    for j in range(3):
                        field[entity_position[1] + i][entity_position[0] + j] = {"type": "empty", "entity": None, "skin": EMPTY}
                if entity_position in entity_positions:
                    del entity_positions[entity_position]
                current_entity = None
                entity_position = None
        elif isinstance(current_entity, (Herbalist, Blacksmith, Trader, WanderingWizard)):
            msg = interact_callback("npc", current_entity)
            wrapped_msgs = wrap_text(msg, STATS_WIDTH - 1)
            interactions.extend(wrapped_msgs)
        interaction_log.extend(interactions)
        if len(interaction_log) > LOG_HEIGHT:
            interaction_log = interaction_log[-LOG_HEIGHT:]
        return interactions

    # Ищем ближайший объект для взаимодействия
    closest_entity = None
    closest_position = None
    closest_distance = float('inf')

    for pos, data in entity_positions.items():
        if data["type"] == "player":  # Пропускаем игрока
            continue
        entity_x, entity_y = pos
        # Проверяем, находится ли игрок в радиусе взаимодействия с объектом
        distance = max(abs(player_x - entity_x), abs(player_y - entity_y))
        if distance <= INTERACTION_RADIUS:
            if distance < closest_distance:
                closest_distance = distance
                closest_entity = data["entity"]
                closest_position = pos

    # Если нашли объект, взаимодействуем с ним
    if closest_position:
        target_type = entity_positions[closest_position]["type"]
        current_entity = closest_entity
        entity_position = closest_position
        if target_type in ["imp", "necromancer", "boss"]:
            msg = interact_callback("monster", current_entity)
            wrapped_msgs = wrap_text(msg, STATS_WIDTH - 1)
            interactions.extend(wrapped_msgs)
        elif target_type in ["herbalist", "trader", "blacksmith", "wizard"]:
            msg = interact_callback("npc", current_entity)
            wrapped_msgs = wrap_text(msg, STATS_WIDTH - 1)
            interactions.extend(wrapped_msgs)
        elif target_type == "city":
            msg = interact_callback("city")
            wrapped_msgs = wrap_text(msg, STATS_WIDTH - 1)
            interactions.extend(wrapped_msgs)

    interaction_log.extend(interactions)
    if len(interaction_log) > LOG_HEIGHT:
        interaction_log = interaction_log[-LOG_HEIGHT:]
    return interactions

def draw_field_with_menu(out, get_stats_callback, get_log_callback):
    """Расширенная функция отрисовки: поддержка меню паузы и справки."""
    from colorama import Style, Fore
    while True:
        if state.game_state == "playing":
            # Встроенная логика отрисовки поля (заменяет draw_field)
            center_x, center_y = player_x + 1, player_y + 1
            start_x = max(0, center_x - VIEW_WIDTH // 2)
            end_x = start_x + VIEW_WIDTH
            start_y = max(0, center_y - VIEW_HEIGHT // 2)
            end_y = start_y + VIEW_HEIGHT

            if end_x > MAP_WIDTH:
                end_x = MAP_WIDTH
                start_x = max(0, end_x - VIEW_WIDTH)
            if end_y > MAP_HEIGHT:
                end_y = MAP_HEIGHT
                start_y = max(0, end_y - VIEW_HEIGHT)

            display_field = [[EMPTY for _ in range(VIEW_WIDTH)] for _ in range(VIEW_HEIGHT)]

            for (entity_x, entity_y), data in entity_positions.items():
                entity_type = data["type"]
                if entity_type == "player":
                    skin = WARRIOR_SKIN if player_class == "warrior" else MAGE_SKIN if player_class == "mage" else ARCHER_SKIN
                elif entity_type == "imp":
                    skin = IMP_SKIN
                elif entity_type == "necromancer":
                    skin = NECROMANCER_SKIN
                elif entity_type == "boss":
                    skin = BOSS_SKIN
                elif entity_type == "herbalist":
                    skin = HERBALIST_SKIN
                elif entity_type == "trader":
                    skin = TRADER_SKIN
                elif entity_type == "blacksmith":
                    skin = BLACKSMITH_SKIN
                elif entity_type == "wizard":
                    skin = WIZARD_SKIN
                elif entity_type == "city":
                    skin = CITY_SKIN
                else:
                    skin = [["?", "?", "?"], ["?", "?", "?"], ["?", "?", "?"]]
                for i in range(3):
                    for j in range(3):
                        map_y = entity_y - start_y + i
                        map_x = entity_x - start_x + j
                        if 0 <= map_y < VIEW_HEIGHT and 0 <= map_x < VIEW_WIDTH:
                            if skin[i][j] != " ":
                                display_field[map_y][map_x] = skin[i][j]

            out[0] = BORDER * CONSOLE_WIDTH
            for i in range(VIEW_HEIGHT):
                map_row = " ".join(display_field[i])
                if i < LOG_HEIGHT:
                    log_line = get_log_callback(i + 1)
                    row = f"{BORDER}{map_row.ljust(VIEW_WIDTH * 2)} {DIVIDER} {log_line.ljust(STATS_WIDTH - 1)}{BORDER}"
                else:
                    stats = get_stats_callback(i - LOG_HEIGHT + 1)
                    row = f"{BORDER}{map_row.ljust(VIEW_WIDTH * 2)} {DIVIDER} {stats.ljust(STATS_WIDTH - 1)}{BORDER}"
                out[i + 1] = row
            out[VIEW_HEIGHT + 1] = BORDER * CONSOLE_WIDTH
            time.sleep(0.1)
        elif state.game_state == "paused":
            menu = [
                Style.BRIGHT + Fore.YELLOW + "\nПауза",
                "1. Продолжить игру",
                "2. Справка по управлению",
                "3. Выйти из игры"
            ]
            for i in range(CONSOLE_HEIGHT):
                if i < len(menu):
                    out[i] = menu[i]
                else:
                    out[i] = " " * CONSOLE_WIDTH
            time.sleep(0.1)
        elif state.game_state == "help":
            help_lines = [
                Style.BRIGHT + Fore.YELLOW + "\nУправление:",
                "WASD — перемещение",
                "E — взаимодействие",
                "H — использовать зелье здоровья",
                "M — использовать зелье маны",
                "F5 — сохранить игру",
                "F9 — загрузить игру",
                "K — квесты, B — биржа, 1-3 — выбор",
                "ESC — пауза/выход в меню",
                "\nНажмите 1 для возврата в игру"
            ]
            for i in range(CONSOLE_HEIGHT):
                if i < len(help_lines):
                    out[i] = help_lines[i]
                else:
                    out[i] = " " * CONSOLE_WIDTH
            time.sleep(0.1)
        elif state.game_state == "exit":
            for i in range(CONSOLE_HEIGHT):
                out[i] = ""
            out[CONSOLE_HEIGHT // 2] = Style.BRIGHT + Fore.RED + "Выход из игры..."
            time.sleep(1)
            import os
            os._exit(0)
        elif state.game_state == "game_over":
            game_over_message = Style.BRIGHT + Fore.RED + "GAME OVER"
            for i in range(CONSOLE_HEIGHT):
                if i == CONSOLE_HEIGHT // 2:
                    out[i] = game_over_message.center(CONSOLE_WIDTH)
                else:
                    out[i] = " " * CONSOLE_WIDTH
            time.sleep(3)
            import os
            os._exit(0)
        else:
            time.sleep(0.1)