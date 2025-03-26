from reprint import output
import keyboard
import time
import random

# Инициализация начальной позиции верхнего левого угла "человека" (2x3)
x, y = 9, 9  # центр поля 20x20 для старта

# Создаем поле 20x20 как список словарей
field = [[{'symbol': '.'} for _ in range(20)] for _ in range(20)]

# Добавляем случайные деревья (W) с низкой вероятностью (например, 5%)
for i in range(20):
    for j in range(20):
        if random.random() < 0.05:  # 5% шанс появления дерева
            field[i][j]['symbol'] = 'W'


# Функция для отрисовки "человека" размером 2x3 на поле
def draw_person(x, y):
    for i in range(2):
        for j in range(3):
            if 0 <= y + i < 20 and 0 <= x + j < 20:  # проверка границ
                if field[y + i][x + j]['symbol'] != 'W':  # не затираем деревья
                    field[y + i][x + j]['symbol'] = '@'


# Инициализируем начальное положение человека
draw_person(x, y)


def draw_field():
    with output(output_type='list', initial_len=10) as output_lines:
        while True:
            # Определяем видимую область 10x10 вокруг центра "человека"
            center_x, center_y = x + 1, y + 1  # центр "человека" (середина 2x3)
            start_y = max(0, center_y - 5)  # верхняя граница видимой области
            end_y = min(20, center_y + 5)  # нижняя граница
            start_x = max(0, center_x - 5)  # левая граница
            end_x = min(20, center_x + 5)  # правая граница

            # Корректируем, чтобы всегда выводилось 10 строк и 10 столбцов
            if end_y - start_y < 10:
                if start_y == 0:
                    end_y = 10
                else:
                    start_y = end_y - 10
            if end_x - start_x < 10:
                if start_x == 0:
                    end_x = 10
                else:
                    start_x = end_x - 10

            # Обновляем строки в reprint
            for i, row_idx in enumerate(range(start_y, end_y)):
                output_lines[i] = ' '.join([field[row_idx][j]['symbol'] for j in range(start_x, end_x)])
            time.sleep(0.1)  # небольшая задержка для плавности


def can_move(new_x, new_y):
    # Проверяем, не пересекается ли новая позиция "человека" с деревьями
    for i in range(2):
        for j in range(3):
            if (0 <= new_y + i < 20 and 0 <= new_x + j < 20 and
                    field[new_y + i][new_x + j]['symbol'] == 'W'):
                return False
    return True


def move_player(direction):
    global x, y
    # Сохраняем старую позицию
    old_x, old_y = x, y
    new_x, new_y = x, y

    # Обновляем координаты в зависимости от направления
    if direction == 'w' and y > 0:  # вверх
        new_y -= 1
    elif direction == 's' and y < 18:  # вниз (18 — максимум для 2 строк)
        new_y += 1
    elif direction == 'a' and x > 0:  # влево
        new_x -= 1
    elif direction == 'd' and x < 17:  # вправо (17 — максимум для 3 столбцов)
        new_x += 1

    # Проверяем, можно ли двигаться
    if (new_x, new_y) != (old_x, old_y) and can_move(new_x, new_y):
        # Очищаем старую позицию "человека"
        for i in range(2):
            for j in range(3):
                if (0 <= old_y + i < 20 and 0 <= old_x + j < 20 and
                        field[old_y + i][old_x + j]['symbol'] == '@'):
                    field[old_y + i][old_x + j]['symbol'] = '.'
        # Обновляем координаты и рисуем новую позицию
        x, y = new_x, new_y
        draw_person(x, y)


# Привязываем клавиши к движению
keyboard.on_press_key("w", lambda _: move_player('w'))
keyboard.on_press_key("s", lambda _: move_player('s'))
keyboard.on_press_key("a", lambda _: move_player('a'))
keyboard.on_press_key("d", lambda _: move_player('d'))

# Запускаем отрисовку поля
draw_field()