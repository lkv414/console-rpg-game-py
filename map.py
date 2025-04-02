import random
import time
from classes import Herbalist, Blacksmith, Trader, WanderingWizard, Imp, Necromancer, Boss
from reprint import output
import threading

# Константы
CONSOLE_WIDTH = 120
CONSOLE_HEIGHT = 29
VIEW_WIDTH = 27      # Видимая ширина карты в клетках (54 символа с пробелами)
VIEW_HEIGHT = 27     # Видимая высота карты в клетках
MAP_WIDTH = 200
MAP_HEIGHT = 200
STATS_WIDTH = 63     # Ширина области статистики и лога (120 - 54 (карта) - 3 (разделитель и рамка))
LOG_HEIGHT = 15      # Высота области лога (15 строк)
STATS_HEIGHT = 10    # Высота области статистики (10 строк, итого 27 строк с учётом рамки)
INTERACTION_RADIUS = 2  # Радиус взаимодействия (2 клетки)

# Символы
PLAYER = "@"
MONSTER = "M"
NPC = "N"
CITY = "C"
EMPTY = "\033[32mW\033[0m"  # Зелёный W
BORDER = "\033[30m#\033[0m"  # Чёрный # с ANSI-кодом
DIVIDER = "|"

# Глобальные переменные
player_x, player_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
field = [[EMPTY for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
interaction_log = []  # Лог взаимодействий
current_entity = None  # Текущий объект взаимодействия (монстр или NPC)
entity_position = None  # Позиция текущего объекта взаимодействия

def place_random(symbol, count=1):
    global player_x, player_y
    for _ in range(count):
        while True:
            x, y = random.randint(0, MAP_WIDTH - 1), random.randint(0, MAP_HEIGHT - 1)
            if field[y][x] == EMPTY and not (player_x <= x < player_x + 3 and player_y <= y < player_y + 2):
                field[y][x] = symbol
                break

def generate_map():
    global field
    field = [[EMPTY for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    draw_person(player_x, player_y)
    place_random(MONSTER, 10)
    place_random(NPC, 10)
    place_random(CITY, 6)

def draw_person(x, y):
    for i in range(2):
        for j in range(3):
            if 0 <= y + i < MAP_HEIGHT and 0 <= x + j < MAP_WIDTH:
                if field[y + i][x + j] == EMPTY:
                    field[y + i][x + j] = PLAYER

def can_move(new_x, new_y):
    for i in range(2):
        for j in range(3):
            if (0 <= new_x + j < MAP_WIDTH and 0 <= new_y + i < MAP_HEIGHT and
                field[new_y + i][new_x + j] in [MONSTER, CITY, NPC]):
                return False
    return True

def move_player(direction):
    global player_x, player_y, current_entity, entity_position
    old_x, old_y = player_x, player_y
    new_x, new_y = player_x, player_y

    if direction == 'w' and player_y > 0:
        new_y -= 1
    elif direction == 's' and player_y < MAP_HEIGHT - 2:
        new_y += 1
    elif direction == 'a' and player_x > 0:
        new_x -= 1
    elif direction == 'd' and player_x < MAP_WIDTH - 3:
        new_x += 1

    if (new_x, new_y) != (old_x, old_y) and can_move(new_x, new_y):
        for i in range(2):
            for j in range(3):
                if (0 <= old_y + i < MAP_HEIGHT and 0 <= old_x + j < MAP_WIDTH and
                    field[old_y + i][old_x + j] == PLAYER):
                    field[old_y + i][old_x + j] = EMPTY
        player_x, player_y = new_x, new_y
        draw_person(player_x, player_y)
        # Если игрок отошёл от объекта, сбрасываем текущее взаимодействие
        if entity_position and not (abs(player_x - entity_position[0]) <= INTERACTION_RADIUS and abs(player_y - entity_position[1]) <= INTERACTION_RADIUS):
            current_entity = None
            entity_position = None
            interaction_log.append("Вы отошли от объекта.")

def interact(interact_callback):
    global interaction_log, current_entity, entity_position
    interactions = []

    # Если уже есть текущее взаимодействие (например, бой с монстром), продолжаем его
    if current_entity:
        if isinstance(current_entity, (Imp, Necromancer, Boss)):
            # Продолжаем бой с монстром
            msg = interact_callback("monster", current_entity)
            interactions.append(msg)
            # Если монстр мёртв, убираем его с карты
            if current_entity.health <= 0:
                field[entity_position[1]][entity_position[0]] = EMPTY
                current_entity = None
                entity_position = None
        elif isinstance(current_entity, (Herbalist, Blacksmith, Trader, WanderingWizard)):
            # Продолжаем взаимодействие с NPC
            msg = interact_callback("npc", current_entity)
            interactions.append(msg)
        interaction_log.extend(interactions)
        if len(interaction_log) > LOG_HEIGHT:
            interaction_log = interaction_log[-LOG_HEIGHT:]
        return interactions

    # Проверяем, есть ли рядом объекты для взаимодействия (в радиусе 2 клеток)
    for i in range(-INTERACTION_RADIUS, INTERACTION_RADIUS + 1):
        for j in range(-INTERACTION_RADIUS, INTERACTION_RADIUS + 1):
            target_x, target_y = player_x + j, player_y + i
            if 0 <= target_x < MAP_WIDTH and 0 <= target_y < MAP_HEIGHT:
                target = field[target_y][target_x]
                if target == MONSTER:
                    current_entity = interact_callback("create_monster")
                    entity_position = (target_x, target_y)
                    msg = interact_callback("monster", current_entity)
                    interactions.append(msg)
                elif target == NPC:
                    current_entity = interact_callback("create_npc")
                    entity_position = (target_x, target_y)
                    msg = interact_callback("npc", current_entity)
                    interactions.append(msg)
                elif target == CITY:
                    interactions.append("Житель говорит: Добро пожаловать в наш город!")
    interaction_log.extend(interactions)
    if len(interaction_log) > LOG_HEIGHT:
        interaction_log = interaction_log[-LOG_HEIGHT:]
    return interactions

def draw_field(out, get_stats_callback, get_log_callback):
    while True:
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

        map_width_symbols = VIEW_WIDTH * 2  # 27 клеток * 2 = 54 символа с пробелами

        out[0] = BORDER * CONSOLE_WIDTH
        for i in range(VIEW_HEIGHT):
            row_idx = start_y + i
            map_row = " ".join([field[row_idx][j] for j in range(start_x, end_x)])
            if i < LOG_HEIGHT:
                # Верхняя часть: лог взаимодействий
                log_line = get_log_callback(i + 1)
                row = f"{BORDER}{map_row} {DIVIDER} {log_line.ljust(STATS_WIDTH - 1)}{BORDER}"
            else:
                # Нижняя часть: статистика
                stats = get_stats_callback(i - LOG_HEIGHT + 1)
                row = f"{BORDER}{map_row} {DIVIDER} {stats.ljust(STATS_WIDTH - 1)}{BORDER}"
            out[i + 1] = row
        out[VIEW_HEIGHT + 1] = BORDER * CONSOLE_WIDTH

        time.sleep(0.1)