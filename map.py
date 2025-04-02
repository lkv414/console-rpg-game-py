from reprint import output
import random
import time
import threading

# Константы
CONSOLE_WIDTH = 120
CONSOLE_HEIGHT = 29
VIEW_WIDTH = 27      # Видимая ширина карты в клетках (54 символа с пробелами)
VIEW_HEIGHT = 27     # Видимая высота карты в клетках
MAP_WIDTH = 200
MAP_HEIGHT = 200
STATS_WIDTH = 63     # Ширина области статистики (120 - 54 (карта) - 3 (разделитель и рамка))

# Символы
PLAYER = "@"
MONSTER = "M"
NPC = "N"
CITY = "C"
EMPTY = "\033[32mW\033[0m"  # Зелёный W
BORDER = "#"
DIVIDER = "|"

# Глобальные переменные
player_x, player_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
field = [[EMPTY for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

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
    global player_x, player_y
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

def interact():
    interactions = []
    for i in range(2):
        for j in range(3):
            target = field[player_y + i][player_x + j]
            if target == MONSTER:
                interactions.append("Ты встретил монстра! Бой начался!")
            elif target == NPC:
                interactions.append("NPC говорит: Привет, путешественник!")
            elif target == CITY:
                interactions.append("Житель говорит: Добро пожаловать в наш город!")
    return interactions

def draw_field(out, get_stats_callback):
    while True:
        # Центр персонажа (середина 2x3)
        center_x, center_y = player_x + 1, player_y + 1
        # Вычисляем видимую область так, чтобы персонаж был в центре
        start_x = max(0, center_x - VIEW_WIDTH // 2)
        end_x = start_x + VIEW_WIDTH
        start_y = max(0, center_y - VIEW_HEIGHT // 2)
        end_y = start_y + VIEW_HEIGHT

        # Корректируем границы, чтобы не выходить за пределы карты
        if end_x > MAP_WIDTH:
            end_x = MAP_WIDTH
            start_x = max(0, end_x - VIEW_WIDTH)
        if end_y > MAP_HEIGHT:
            end_y = MAP_HEIGHT
            start_y = max(0, end_y - VIEW_HEIGHT)

        map_width_symbols = VIEW_WIDTH * 2  # 27 клеток * 2 = 54 символа с пробелами

        # Рисуем рамку и карту
        out[0] = BORDER * CONSOLE_WIDTH
        for i in range(VIEW_HEIGHT):
            row_idx = start_y + i
            map_row = " ".join([field[row_idx][j] for j in range(start_x, end_x)])
            stats = get_stats_callback(i + 1)
            row = f"{BORDER}{map_row} {DIVIDER} {stats.ljust(STATS_WIDTH - 1)}{BORDER}"
            out[i + 1] = row
        out[VIEW_HEIGHT + 1] = BORDER * CONSOLE_WIDTH

        time.sleep(0.1)