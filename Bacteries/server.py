import socket
import pygame
import math
import random
import faker
from sqlalchemy import String, Integer, Column
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
connection = create_engine("postgresql://postgres:(M1quella)@localhost/DB")
base = declarative_base()
session = sessionmaker(bind=connection)
s = session()
pygame.init()
WIDTH = 4000
HEIGHT = 4000
WIDTH_SERVER = 300
HEIGHT_SERVER = 300
FPS = 100
food_quantity = WIDTH * HEIGHT // 40000
mob_quantity = 20
screen = pygame.display.set_mode((WIDTH_SERVER, HEIGHT_SERVER))
pygame.display.set_caption("Server")
clock = pygame.time.Clock()
colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
          'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
          'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
          'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DeepSkyBlue',
          'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']
faker = faker.Faker("RU_ru")


def find_color(vector: str):
    first = None
    for num, sign in enumerate(vector):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            result = vector[first + 1:second].split(",")
            return result
    return ""


def find(vector: str):
    first = None
    for num, sign in enumerate(vector):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            result = list(map(float, vector[first + 1:second].split(",")))
            return result
    return ""


class Player(base):
    __tablename__ = "Players"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250))
    address = Column(String)
    x = Column(Integer, default=500)
    y = Column(Integer, default=500)
    size = Column(Integer, default=50)
    errors = Column(Integer, default=0)
    abs_speed = Column(Integer, default=1)
    speed_x = Column(Integer, default=0)
    speed_y = Column(Integer, default=0)
    color = Column(String, default="Red")
    w_vision = Column(Integer, default=800)
    h_vision = Column(Integer, default=600)
    L = Column(Integer, default=1)

    def __init__(self, name, address):
        self.name = name
        self.address = address


base.metadata.create_all(bind=connection)


class Food:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.size = 15
        self.color = color


class LocalPlayer:
    def __init__(self, id, name, sock, addr):
        self.id = id
        self.db: Player = s.get(Player, self.id)
        self.sock = sock
        self.name = name
        self.address = addr
        self.x = 500
        self.y = 500
        self.size = 50
        self.errors = 0
        self.abs_speed = 1
        self.speed_x = 0
        self.speed_y = 0
        self.color = "Red"
        self.w_vision = 800
        self.h_vision = 600
        self.L = 1

    def update(self):
        if self.x - self.size <= 0:
            if self.speed_x >= 0:
                self.x += self.speed_x
        elif self.x + self.size >= WIDTH:
            if self.speed_x <= 0:
                self.x += self.speed_x
        else:
            self.x += self.speed_x

        if self.y - self.size <= 0:
            if self.speed_y >= 0:
                self.y += self.speed_y
        elif self.y + self.size >= HEIGHT:
            if self.speed_y <= 0:
                self.y += self.speed_y
        else:
            self.y += self.speed_y

        if self.size >= 100:
            self.size -= self.size / 18000
        if self.size >= self.w_vision // 4:
            if self.w_vision <= WIDTH or self.h_vision <= HEIGHT:
                self.L *= 2
                self.w_vision = 800 * self.L
                self.h_vision = 600 * self.L
        if self.size < self.w_vision // 8 and self.size < self.h_vision // 8:
            if self.L > 1:
                self.L //= 2
                self.w_vision = 800 * self.L
                self.h_vision = 600 * self.L

    def change_speed(self, vector):
        vector = find(vector)
        if vector[0] == 0 and vector[1] == 0:
            self.speed_x = self.speed_y = 0
        else:
            vector = vector[0] * self.abs_speed, vector[1] * self.abs_speed
            self.speed_x = vector[0]
            self.speed_y = vector[1]

    def new_speed(self):
        self.abs_speed = 10 / math.sqrt(self.size)

    def sync(self):
        self.db.x = self.x
        self.db.y = self.y
        self.db.size = self.size
        self.db.errors = self.errors
        self.db.abs_speed = self.abs_speed
        self.db.speed_x = self.speed_x
        self.db.speed_y = self.speed_y
        self.db.color = self.color
        self.db.w_vision = self.w_vision
        self.db.h_vision = self.h_vision

    def load(self):
        self.x = self.db.x
        self.y = self.db.y
        self.size = self.db.size
        self.errors = self.db.errors
        self.abs_speed = self.db.abs_speed
        self.speed_x = self.db.speed_x
        self.speed_y = self.db.speed_y
        self.color = self.db.color
        self.w_vision = self.db.w_vision
        self.h_vision = self.db.h_vision
        return self


players: dict[int: LocalPlayer] = {}
link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
link.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
link.bind(("localhost", 22822))
link.setblocking(False)
link.listen(10)

names = []
for i in range(mob_quantity):
    names.append(faker.first_name())
names = list(set(names))


for x in range(mob_quantity):
    server_mob = Player(names[x], None)
    server_mob.color = random.choice(colors)
    server_mob.x, server_mob.y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    #server_mob.speed_x, server_mob.speed_y = random.randint(-1, 1), random.randint(-1, 1)
    server_mob.size = random.randint(10, 100)
    s.add(server_mob)
    s.commit()
    local_mob = LocalPlayer(server_mob.id, server_mob.name, None, None).load()
    players[server_mob.id] = local_mob
foods = []
for i in range(food_quantity):
    foods.append(Food(x=random.randint(0, WIDTH), y=random.randint(0, HEIGHT), color=random.choice(colors)))
tick = -1


run = True
while run:
    clock.tick(FPS)
    tick += 1
    if tick % 200 == 0:
        try:
            new_socket, addr = link.accept()
            print('Подключился', addr)
            new_socket.setblocking(False)
            login = new_socket.recv(1024).decode()
            player = Player("Имя", addr)
            if login.startswith("color"):
                data = find_color(login[6:])
                player.name, player.color = data
            s.merge(player)
            s.commit()
            addr = f'({addr[0]},{addr[1]})'
            data = s.query(Player).filter(Player.address == addr)
            for user in data:
                player = LocalPlayer(user.id, player.name, new_socket, addr).load()
                players[user.id] = player
        except BlockingIOError:
            pass
    if len(foods) != 0:
        need = mob_quantity - len(players)
        if need > 0:
            names = []
            for i in range(mob_quantity):
                names.append(faker.first_name())
            names = list(set(names))
            for i in range(mob_quantity - len(players)):
                server_mob = Player(names[i], None)
                server_mob.color = random.choice(colors)
                spawn = random.choice(foods)
                foods.remove(spawn)
                server_mob.x, server_mob.y = spawn.x, spawn.y
                server_mob.size = random.randint(10, 100)
                s.add(server_mob)
                s.commit()
                local_mob = LocalPlayer(server_mob.id, server_mob.name, None, None).load()
                local_mob.new_speed()
                players[server_mob.id] = local_mob
    need = food_quantity - len(foods)

    for i in range(need):
        foods.append(Food(x=random.randint(0, WIDTH),y=random.randint(0, HEIGHT), color=random.choice(colors)))

    for id in list(players):
        if players[id].sock is not None:
            try:
                data = players[id].sock.recv(1024).decode()
                players[id].change_speed(data)
            except:
                pass
        else:
            if tick % 400 == 0:
                vector = f"<{random.randint(-1, 1)},{random.randint(-1, 1)}>"
                players[id].change_speed(vector)

    visible_bacteries = {}

    for id in list(players):
        visible_bacteries[id] = []
    pairs = list(players.items())

    for i in range(0, len(pairs)):
        for f in foods:
            hero_1: LocalPlayer = pairs[i][1]
            dist_x = f.x - hero_1.x
            dist_y = f.y - hero_1.y

            if abs(dist_x) <= hero_1.w_vision // 2 + f.size and abs(dist_y) <= hero_1.h_vision // 2 + f.size:
                distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
                if distance <= hero_1.size:
                    hero_1.size = math.sqrt(hero_1.size ** 2 + f.size ** 2)
                    hero_1.new_speed()
                    f.size = 0
                    foods.remove(f)
                if hero_1.address is not None and f.size != 0:
                    x_ = str(round(dist_x // hero_1.L))
                    y_ = str(round(dist_y // hero_1.L))
                    size_ = str(round(f.size // hero_1.L))
                    color_ = f.color
                    data = x_ + " " + y_ + " " + size_ + " " + color_
                    visible_bacteries[hero_1.id].append(data)

        for j in range(i + 1, len(pairs)):
            hero_1: LocalPlayer = pairs[i][1]
            hero_2: LocalPlayer = pairs[j][1]
            dist_x = hero_2.x - hero_1.x
            dist_y = hero_2.y - hero_1.y

            if abs(dist_x) <= hero_1.w_vision // 2 + hero_2.size and abs(dist_y) <= hero_1.h_vision // 2 + hero_2.size:
                distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
                if distance <= hero_1.size and hero_1.size > 1.1 * hero_2.size:
                    hero_1.size = math.sqrt(hero_1.size ** 2 + hero_2.size ** 2)
                    hero_1.new_speed()
                    hero_2.size, hero_2.speed_x, hero_2.speed_y = 0, 0, 0
                if hero_1.address is not None:
                    x_ = str(round(dist_x // hero_1.L))
                    y_ = str(round(dist_y // hero_1.L))
                    size_ = str(round(hero_2.size // hero_1.L))
                    color_ = hero_2.color
                    name_ = hero_2.name
                    data = x_ + " " + y_ + " " + size_ + " " + color_
                    if hero_2.size >= 30 * hero_1.L:
                        data += " " + name_
                    visible_bacteries[hero_1.id].append(data)

            if abs(dist_x) <= hero_2.w_vision // 2 + hero_1.size and abs(dist_y) <= hero_2.h_vision // 2 + hero_1.size:
                distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
                if distance <= hero_2.size and hero_2.size > 1.1 * hero_1.size:
                    hero_2.size = math.sqrt(hero_2.size ** 2 + hero_1.size ** 2)
                    hero_2.new_speed()
                    hero_1.size, hero_1.speed_x, hero_1.speed_y = 0, 0, 0
                if hero_2.address is not None:
                    x_ = str(round(-dist_x // hero_2.L))
                    y_ = str(round(-dist_y // hero_2.L))
                    size_ = str(round(hero_1.size // hero_2.L))
                    color_ = hero_1.color
                    name_ = hero_1.name
                    data = x_ + " " + y_ + " " + size_ + " " + color_
                    if hero_2.size >= 30 * hero_1.L:
                        data += " " + name_
                    visible_bacteries[hero_2.id].append(data)

    for id in list(players):
        rad = str(round(players[id].size // players[id].L))
        x = str(round(players[id].x // players[id].L))
        y = str(round(players[id].y // players[id].L))
        L = str(players[id].L)
        visible_bacteries[id] = [rad + " " + x + " " + y + " " + L] + visible_bacteries[id]
        visible_bacteries[id] = "<" + ",".join(visible_bacteries[id]) + ">"

    for id in list(players):
        if players[id].sock is not None:
            try:
                players[id].sock.send(visible_bacteries[id].encode())
            except:
                players[id].errors += 1

    for id in list(players):
        if players[id].errors >= 500 or players[id].size == 0:
            if players[id].sock is not None:
                players[id].sock.close()
                print("Сокет закрыт")
            del players[id]
            s.query(Player).filter(Player.id == id).delete()
            s.commit()

    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            run = False
    screen.fill('black')

    for id in list(players):
        player = players[id]
        x = player.x * WIDTH_SERVER // WIDTH
        y = player.y * HEIGHT_SERVER // HEIGHT
        size = player.size * WIDTH_SERVER // WIDTH
        pygame.draw.circle(screen, player.color, (x, y), size)

    for id in list(players):
        player = players[id]
        players[id].update()
        if tick % 300 == 0:
            players[id].sync()
    pygame.display.update()
pygame.quit()
link.close()
s.query(Player).delete()
s.commit()
# дописать код
