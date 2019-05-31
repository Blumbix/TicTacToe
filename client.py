import pygame
import time
from grid import Grid

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '600,100'

surface = pygame.display.set_mode((300,300))
pygame.display.set_caption('Tic tac toe')
pygame.font.init()
fontS = pygame.font.SysFont(None, 39)
fontM = pygame.font.SysFont(None, 30)
fontB = pygame.font.SysFont(None, 60)

import threading
def create_thread(target):
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

import socket
HOST = '127.0.0.1'
PORT = 65432
connection_established = False
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def receive_data():
    global turn, connection_established, sock, playing, result, ready
    while True:
        try:
            if not connection_established:
                try:
                    sock.connect((HOST, PORT))
                    connection_established = True
                except ConnectionRefusedError:
                    continue
            data = sock.recv(1024).decode()
            if data == "ready":
                ready = True
            else:
                data = data.split('-')
                x, y = int(data[0]), int(data[1])
                turn = True
                if data[2] == 'False':
                    grid.game_over = True
                    result = data[3]
                if grid.get_cell_value(x, y) == 0:
                    grid.set_cell_value(x, y, 'X')
        except ConnectionResetError:
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection_established = False
            grid.clear_grid()
            grid.game_over = False
            turn = False
            playing = 'True'

create_thread(receive_data)
grid = Grid()
running = True
player = "O"
turn = False
playing = 'True'
result = ''
ready = False
waiting_message = fontS.render("Waiting for server.", True, (255, 255, 0))
waiting_message2 = fontM.render("Waiting for server.", True, (255, 255, 0))

while running:
    if connection_established:
        surface.fill((50, 50, 50))
        grid.draw(surface)
        if grid.game_over:
            win_message = fontB.render(result, True, (255, 255, 0))
            surface.blit(win_message, (5, 130))
            surface.blit(waiting_message2, (5, 275))
        pygame.display.flip()

    if ready:
        ready = False
        grid.clear_grid()
        grid.game_over = False
        playing = 'True'

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not grid.game_over:
            if pygame.mouse.get_pressed()[0]:
                if turn and not grid.game_over:
                    pos = pygame.mouse.get_pos()
                    cellX, cellY = pos[0] // 100, pos[1] // 100
                    if grid.get_cell_value(cellX, cellY) != 0:
                        continue
                    grid.get_mouse(cellX, cellY, player)
                    if grid.game_over:
                        playing = 'False'
                        if grid.winner == None:
                            result = '        Draw!'
                        else:
                            result = 'Player O wins!'
                    send_data = '{}-{}-{}-{}'.format(cellX, cellY, playing, result).encode()
                    sock.send(send_data)
                    turn = False

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            running = False

    if not connection_established:
        surface.fill((50, 50, 50))
        surface.blit(waiting_message, (30, 130))
        pygame.display.flip()
