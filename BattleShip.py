from random import randint

class dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other): # проверка двух аргументов
            return self.x == other.x and self.y == other.y

    def __repr__(self): #возврат точек в консоль
            return f"Dot({self.x}, {self.y})"

class BoardException(Exception): # содержит остальные классы исключений
    pass

class BoardOutException(BoardException): #класс пользовательских исключений
    def __str__(self):
        return  "Снаряды улететят из зоны сражения!!! Наводчик, скорректируй огонь!!"

class BoardUserException(BoardException): #класс пользовательских исключений
    def __str__(self):
        return "Ты палил сюда из всех орудий, выбери другое место!!"

class BoardWrongShipException(BoardException): #исключение для размещения кораблей
    pass

class Ship: #конструктор корабля
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot): #проверка на попадание
        return shot in self.dots

class Board:  #создаем поле
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid

        self.count = 0 #количество пораженных кораблей

        self.field = [["0"] * size for _ in range(size)]

        self.busy = [] #тут хранятся занятые точки
        self.ships = [] #список кораблей доски

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, -1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self): #конструктор поля
        res = ""
        res += " | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("*", "o")
        return res

    def out(self, d): #проверка точки за пределами поля
        return not ((0 <= d.x < self.size))and (0 <= d.y < self.size)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count +=1
                    self.contour(ship, verb = True)
                    print("Отличная работа, капитан!!! Корабль идет ко дну!!!Пираты прыгают в воду")
                    return False
                else:
                    print("Есть попадание!!!Пираты в панике")
                    return True

        self.field[d.x][d.y] = "."
        print("Жаль, залп рядом лег")
        return False

    def begin(self):
        self.busy = []

class player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(player):
    def ask(self):
        d = dot(randint(0, 5), randint(0, 5))
        print(f"Пираты ведут огонь: {d.x + 1} {d.y}")
        return d

class User(player):
    def ask(self):
        while True:
            cords = input("Орудия заряжены, давай стрелять!!!   ").split()

            if len(cords) != 2:
                print("Введи 2 координаты  ")
                continue

            x, y = cords

            if not(x.isdigit()) or not (y.isdigit()):
                print("Введи числа! ")
                continue

            x, y = int(x), int(y)

            return dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("********************************")
        print("   Приветствую тебя, капитан!!!!")
        print(" Настало время проучить пиратов!")
        print(" Орудия заряжены, корабль готов!")
        print("********************************")
        print("       формат наводки: x y      ")
        print("         х - номер строки       ")
        print("         у - номер столбца      ")
        print(" Точной стрельбы тебе, капитан! ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("доска капитана:")
            print(self.us.board)
            print("-" * 20)
            print("доска пиратов:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("твой ход, капитан!")
                repeat = self.us.move()
            else:
                print("пираты ведут огонь!")
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Ты победил, капитан, возвращайся домой!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Пираты празднуют победу!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()

