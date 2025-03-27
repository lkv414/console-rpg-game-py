from reprint import output
import random
import time

# Константы
MAP_SIZE = 20
VISION_SIZE = 2  # Поле зрения 2x2 вокруг игрока

# Символы для отображения
PLAYER = "😊"
MONSTER = "👾"
NPC = "🙂"
CITY = "🏰"
EMPTY = "⬜"
BORDER = "🟥"


class GameMap:
    def __init__(self):
        self.size = MAP_SIZE
        self.map = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.player_x = random.randint(0, MAP_SIZE - 1)
        self.player_y = random.randint(0, MAP_SIZE - 1)
        self.generate_map()

    def generate_map(self):
        # Очищаем карту
        self.map = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]

        # Размещаем игрока
        self.map[self.player_y][self.player_x] = PLAYER

        # Размещаем монстра
        self.place_random(MONSTER)

        # Размещаем NPC
        self.place_random(NPC)

        # Размещаем город
        self.place_random(CITY)

    def place_random(self, symbol):
        while True:
            x, y = random.randint(0, MAP_SIZE - 1), random.randint(0, MAP_SIZE - 1)
            if self.map[y][x] == EMPTY:
                self.map[y][x] = symbol
                break

    def display_map(self, out):
        # Формируем карту для вывода через reprinter
        for y in range(self.size):
            row = ""
            for x in range(self.size):
                if abs(self.player_x - x) <= VISION_SIZE and abs(self.player_y - y) <= VISION_SIZE:
                    row += self.map[y][x] + " "
                else:
                    row += "⬛ "
            out[y] = row
        out[self.size] = "Управление: w - вверх, s - вниз, a - лево, d - право, e - взаимодействие, q - выход"

    def move_player(self, direction):
        new_x, new_y = self.player_x, self.player_y
        if direction == 'w' and self.player_y > 0:
            new_y -= 1
        elif direction == 's' and self.player_y < MAP_SIZE - 1:
            new_y += 1
        elif direction == 'a' and self.player_x > 0:
            new_x -= 1
        elif direction == 'd' and self.player_x < MAP_SIZE - 1:
            new_x += 1

        # Проверка перехода на новый блок
        if new_x < 0 or new_x >= MAP_SIZE or new_y < 0 or new_y >= MAP_SIZE:
            return self.switch_map()

        # Проверка столкновения
        target = self.map[new_y][new_x]
        if target == MONSTER:
            print("Ты встретил монстра! Бой начался!")
        elif target == NPC:
            print("NPC говорит: Привет, путешественник!")
        elif target == CITY:
            self.enter_city()
        elif target == EMPTY:
            self.map[self.player_y][self.player_x] = EMPTY
            self.player_x, self.player_y = new_x, new_y
            self.map[self.player_y][self.player_x] = PLAYER

    def switch_map(self):
        print("Переход на новый блок карты!")
        self.generate_map()

    def enter_city(self):
        print("Ты вошел в город!")
        action = input("Говорить с жителями? (y/n): ").lower()
        if action == 'y':
            print("Житель говорит: Добро пожаловать в наш город!")


def main():
    game = GameMap()
    with output(initial_len=MAP_SIZE + 1, interval=0) as out:
        while True:
            game.display_map(out)
            time.sleep(0.1)  # Небольшая задержка для стабильности вывода
            action = input("Твой ход: ").lower()
            if action in ['w', 's', 'a', 'd']:
                game.move_player(action)
            elif action == 'e':
                if game.map[game.player_y][game.player_x] == CITY:
                    game.enter_city()
            elif action == 'q':
                print("Игра окончена!")
                break


if __name__ == "__main__":
    main()


