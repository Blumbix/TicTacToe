import pygame
from grid import Grid

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '200,100'

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
conn, addr = None, None

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

def receive_data():
    global turn, connection_established, playing, result
    while True:
        try:
            data = conn.recv(1024).decode()
            data = data.split('-')
            x, y = int(data[0]), int(data[1])
            turn = True
            if data[2] == 'False':
                grid.game_over = True
                result = data[3]
            if grid.get_cell_value(x, y) == 0:
                grid.set_cell_value(x, y, 'O')
        except ConnectionResetError:
            connection_established = False
            grid.clear_grid()
            grid.game_over = False
            turn = True
            playing = 'True'
            waiting_for_connection()

def waiting_for_connection():
    global connection_established, conn, addr
    conn, addr = sock.accept()  # wait for a connection
    print("Client is connected")
    connection_established = True
    receive_data()

create_thread(waiting_for_connection)
grid = Grid()
running = True
player = "X"
turn = True
playing = 'True'
result = ''
waiting_message = fontS.render("Waiting for 2nd player.", True, (255, 255, 0))
waiting_message2 = fontM.render("Press SPACE to restart.", True, (255, 255, 0))

while running:
    if connection_established:
        surface.fill((50, 50, 50))
        grid.draw(surface)
        if grid.game_over:
            win_message = fontB.render(result, True, (255, 255, 0))
            surface.blit(win_message, (5, 130))
            surface.blit(waiting_message2, (5, 275))
        pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and connection_established:
            if pygame.mouse.get_pressed()[0]:
                if turn and not grid.game_over:
                    pos = pygame.mouse.get_pos()
                    cellX, cellY = pos[0]//100, pos[1]//100
                    if grid.get_cell_value(cellX, cellY) != 0:
                        continue
                    grid.get_mouse(cellX, cellY, player)
                    if grid.game_over:
                        playing = 'False'
                        if grid.winner == None:
                            result = '        Draw!'
                        else:
                            result = 'Player X wins!'
                    send_data = '{}-{}-{}-{}'.format(cellX, cellY, playing, result).encode()
                    conn.send(send_data)
                    turn = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and grid.game_over:
                grid.clear_grid()
                grid.game_over = False
                playing = 'True'
                send_data = 'ready'.encode()
                conn.send(send_data)
            elif event.key == pygame.K_ESCAPE:
                running = False

    if not connection_established:
        surface.fill((50, 50, 50))
        surface.blit(waiting_message, (5, 130))
        pygame.display.flip()