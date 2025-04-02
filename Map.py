from reprint import output
import random
import time
import keyboard
import threading

# Константы
CONSOLE_WIDTH = 120  # Ширина консоли в символах (с пробелами)
CONSOLE_HEIGHT = 30  # Высота консоли
VIEW_WIDTH = 29  # Видимая ширина в клетках (120 символов / 2 из-за пробелов)
VIEW_HEIGHT = 29  # Видимая высота в клетках
MAP_WIDTH = 200  # Полный размер карты
MAP_HEIGHT = 200  # Полный размер карты

# Символы для отображения
PLAYER = "@"
MONSTER = "M"  # Замена 👾 на M
NPC = "N"  # Замена 🙂 на N
CITY = "C"  # Замена 🏰 на C
EMPTY = "\033[32mW\033[0m"  # Зелёный W (дерево) с ANSI-кодом

# Инициализация начальной позиции "человека" (2x3) в центре карты
player_x, player_y = MAP_WIDTH // 2, MAP_HEIGHT // 2

# Создаем поле как список списков
field = [[EMPTY for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]


# Функция для размещения случайных объектов
def place_random(symbol, count=1):
    for _ in range(count):
        while True:
            x, y = random.randint(0, MAP_WIDTH - 1), random.randint(0, MAP_HEIGHT - 1)
            if field[y][x] == EMPTY and not (player_x <= x < player_x + 3 and player_y <= y < player_y + 2):
                field[y][x] = symbol
                break


# Инициализация карты
def generate_map():
    global field
    field = [[EMPTY for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    draw_person(player_x, player_y)
    place_random(MONSTER, 10)
    place_random(NPC, 10)
    place_random(CITY, 6)


# Функция для отрисовки "человека" размером 2x3
def draw_person(x, y):
    for i in range(2):
        for j in range(3):
            if 0 <= y + i < MAP_HEIGHT and 0 <= x + j < MAP_WIDTH:
                if field[y + i][x + j] == EMPTY:
                    field[y + i][x + j] = PLAYER


# Проверка, можно ли двигаться
def can_move(new_x, new_y):
    for i in range(2):
        for j in range(3):
            if (0 <= new_y + i < MAP_HEIGHT and 0 <= new_x + j < MAP_WIDTH and
                    field[new_y + i][new_x + j] in [MONSTER, CITY, NPC]):
                return False
    return True


# Движение игрока
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
        # Очищаем старую позицию
        for i in range(2):
            for j in range(3):
                if (0 <= old_y + i < MAP_HEIGHT and 0 <= old_x + j < MAP_WIDTH and
                        field[old_y + i][old_x + j] == PLAYER):
                    field[old_y + i][old_x + j] = EMPTY
        # Обновляем позицию
        player_x, player_y = new_x, new_y
        draw_person(player_x, player_y)


# Взаимодействие
def interact():
    for i in range(2):
        for j in range(3):
            target = field[player_y + i][player_x + j]
            if target == MONSTER:
                print("Ты встретил монстра! Бой начался!")
            elif target == NPC:
                print("NPC говорит: Привет, путешественник!")
            elif target == CITY:
                print("Житель говорит: Добро пожаловать в наш город!")


# Отрисовка поля
def draw_field(out):
    while True:
        # Центр "человека" (середина 2x3)
        center_x, center_y = player_x + 1, player_y + 1
        start_x = max(0, center_x - VIEW_WIDTH // 2)
        end_x = min(MAP_WIDTH, center_x + VIEW_WIDTH // 2)
        start_y = max(0, center_y - VIEW_HEIGHT // 2)
        end_y = min(MAP_HEIGHT, center_y + VIEW_HEIGHT // 2)

        # Корректируем видимую область
        if end_x - start_x < VIEW_WIDTH:
            if start_x == 0:
                end_x = VIEW_WIDTH
            else:
                start_x = end_x - VIEW_WIDTH
        if end_y - start_y < VIEW_HEIGHT:
            if start_y == 0:
                end_y = VIEW_HEIGHT
            else:
                start_y = end_y - VIEW_HEIGHT

        # Отрисовка видимой области
        for i, row_idx in enumerate(range(start_y, end_y)):
            row = " ".join([field[row_idx][j] for j in range(start_x, end_x)])
            out[i] = row

        time.sleep(0.1)


def main():
    generate_map()

    with output(initial_len=VIEW_HEIGHT, interval=0) as out:
        # Запускаем отрисовку в отдельном потоке
        thread = threading.Thread(target=draw_field, args=(out,))
        thread.start()

        # Привязываем клавиши
        keyboard.on_press_key("w", lambda _: move_player('w'))
        keyboard.on_press_key("s", lambda _: move_player('s'))
        keyboard.on_press_key("a", lambda _: move_player('a'))
        keyboard.on_press_key("d", lambda _: move_player('d'))
        keyboard.on_press_key("e", lambda _: interact())
        keyboard.on_press_key("q", lambda _: exit(0))

        # Держим основной поток активным
        thread.join()


if __name__ == "__main__":
    main()