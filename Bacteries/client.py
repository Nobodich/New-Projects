import socket
import pygame
import math
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import time
buffer = 1024
name = ""
color = ""


def login():
    global name
    name = row.get()
    if name and color:
        root.destroy()
        root.quit()
    else:
        tk.messagebox.showerror("Ошибка", "Ты не выбрал цвет или не ввёл имя!")


def scroll(event):
    global color
    color = combo.get()
    style.configure("TCombobox", fieldbackground=color, background="white")


root = tk.Tk()
root.title("Логин")
root.geometry("300x200")
style = ttk.Style()
style.theme_use('clam')
name_label = tk.Label(root, text="Введи свой никнейм:")
name_label.pack()
row = tk.Entry(root, width=30, justify="center")
row.pack()
color_label = tk.Label(root, text="Выбери цвет:")
color_label.pack()
colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
          'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
          'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
          'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DeepSkyBlue',
          'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']
combo = ttk.Combobox(root, values=colors, textvariable=color)
combo.bind("<<ComboboxSelected>>", scroll)
combo.pack()
name_btn = tk.Button(root, text="Зайти в игру", command=login)
name_btn.pack()
root.mainloop()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(("localhost", 22822))
sock.send(("color:<" + name + "," + color + ">").encode())
pygame.init()
WIDTH = 800
HEIGHT = 600
radius = 50
center = (WIDTH // 2, HEIGHT // 2)
old_vector = (0, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")


def find(vector: str):
    global buffer
    first = None
    for num, sign in enumerate(vector):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            result = vector[first + 1:second]  # Поменяли
            return result
    if buffer < 1000000:
        buffer = int(buffer * 1.5)
    return ""


def draw_bacteries(data: list[str]):
    for num, bact in enumerate(data):
        data = bact.split(" ")  # Разбиваем по пробелам подстроку одной бактерии
        x = center[0] + int(data[0])
        y = center[1] + int(data[1])
        size = int(data[2])
        color = data[3]
        pygame.draw.circle(screen, color, (x, y), size)
        if len(data) > 4:
            draw_text(x, y, size // 2, data[4], "black")


class Grid:
    def __init__(self, screen, color):
        self.screen = screen
        self.x = 0
        self.y = 0
        self.start_size = 200
        self.size = self.start_size
        self.color = color

    def update(self, parameters: list[int]):
        x, y, L = parameters
        self.size = self.start_size // L
        self.x = -self.size + (-x) % self.size
        self.y = -self.size + (-y) % self.size

    def draw(self):
        for i in range(WIDTH // self.size + 2):
            pygame.draw.line(self.screen, self.color,
                             (self.x + i * self.size, 0),  # Координаты начала линии
                             (self.x + i * self.size, HEIGHT),  # Координаты конца линии
                             1)
        for i in range(HEIGHT // self.size + 2):
            pygame.draw.line(self.screen, self.color,
                             (0, self.y + i * self.size),  # Координаты начала линии
                             (WIDTH, self.y + i * self.size),  # Координаты конца линии
                             1)


grid = Grid(screen, "gray25")


def draw_text(x, y, r, text, color):
    font = pygame.font.Font(None, r)
    text = font.render(text, True, color)
    rect = text.get_rect(center=(x, y))
    screen.blit(text, rect)


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if pygame.mouse.get_focused():
            coord = pygame.mouse.get_pos()
            vector = coord[0] - center[0], coord[1] - center[1]
            lvector = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
            vector = vector[0] / lvector, vector[1] / lvector

            if lvector <= radius:
                vector = (0, 0)

            if vector != old_vector:
                old_vector = vector
                try:
                    sock.send(f"<{vector[0]}, {vector[1]}>".encode())
                except:
                    run= False
                    continue

    data = sock.recv(buffer).decode()
    data = find(data).split(",")
    screen.fill('white')
    if data != ['']:
        parameters = list(map(int, data[0].split(" ")))
        radius = parameters[0]
        grid.update(parameters[1:])
        grid.draw()
        draw_bacteries(data[1:])
    pygame.draw.circle(screen, color, center, radius)
    draw_text(center[0], center[1], radius // 2, name, "black")
    pygame.display.update()
screen.fill('gray25')
draw_text(center[0], center[1], 100, "Спасибо за игру!", "white")
pygame.display.update()


time.sleep(3)
pygame.quit()
