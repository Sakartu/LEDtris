#!/usr/bin/env python3

import sys
from random import choice
import pygame
from pygame.locals import *
from block import O, I, S, Z, L, J, T
import paho.mqtt.client as mqtt

COLS = 12
ROWS = 10
CELLS = COLS * ROWS
CELLPX = 30
POS_FIRST_APPEAR = 5
SCREEN_SIZE = (COLS*CELLPX, ROWS*CELLPX)
COLOR_BG = (0, 0, 0)


def draw(grid, pos=None):
    if pos:   # 6x5
        s = pos - 3 - 2 * COLS   # upper left position
        for p in range(0, 5):
            q = s + p * COLS
            for i in range(q, q+6):
                if 0 <= i < CELLS:
                    c = eval(grid[i]+".color") if grid[i] else COLOR_BG
                    screen.fill(c, (i % COLS, i // COLS, 1, 1))
        if '-v' in sys.argv:
            print()
    else:   # all
        screen.clear()
        for i, occupied in enumerate(grid):
            if occupied:
                c = eval(grid[i]+".color")
                screen.fill(c, (i % COLS, i // COLS, 1, 1))
    screen.flip()


def phi(grid1, grid2, pos):  # 4x4
    s = pos - 2 - 1 * COLS  # upper left position
    for p in range(0, 4):
        q = s + p * COLS
        for i in range(q, q+4):
            try:
                if grid1[i] and grid2[i]:
                    return False
            except IndexError:
                pass
    return True


def merge(grid1, grid2):
    grid = grid1[:]
    for i, c in enumerate(grid2):
        if c:
            grid[i] = c
    return grid


def complete(grid):
    n = 0
    for i in range(0, CELLS, COLS):
        if None not in grid[i:i+COLS]:
            grid = [None]*COLS + grid[:i] + grid[i+COLS:]
            n += 1
    return grid, n


def max_pos(grid, block, pos):
    while True:
        grid_block = block.grid(pos+COLS, COLS, ROWS)
        if grid_block and phi(grid, grid_block, pos+COLS):
            pos += COLS
        else:
            return pos


class LEDScreen(object):
    def __init__(self):
        self.conn = mqtt.Client('rest')
        self.buffer = [(0, 0, 0)] * CELLS
        self.connect()

    def connect(self):
        self.conn.connect(sys.argv[1])

    def clear(self):
        guiscreen.fill(COLOR_BG, (0, 0, COLS*CELLPX, ROWS*CELLPX))
        self.buffer = [(0, 0, 0)] * CELLS

    def fill(self, col, rect=(0, 0, COLS, ROWS)):
        left, top, width, height = rect
        for i in range(CELLS):
            x = i % COLS
            y = i // COLS
            if (left <= x < (left + width)) and (top <= y < (top + height)):  # in rect
                self.buffer[i] = col
        guiscreen.fill(col, (left * CELLPX, top*CELLPX, width*CELLPX, height*CELLPX))

    def flip(self):
        msg = ''.join('{:03d}{:03d}{:03d}'.format(*c) for c in self.buffer)
        try:
            self.conn.publish('/ledstrip', msg, retain=True)
        except Exception:
            self.connect()
            self.conn.publish('/ledstrip', msg, retain=True)
        if '-v' in sys.argv:
            self.print_msg(msg)
        pygame.display.flip()

    @staticmethod
    def print_msg(msg):
        print('-'*COLS + '--')
        for row in LEDScreen.chunks(msg, COLS * 9):
            print('|', end='')
            for c in LEDScreen.chunks(row, 9):
                if c == '000000000':
                    print(' ', end='')
                else:
                    print('X', end='')
            print('|')
        print('-'*COLS + '--')

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]


pygame.mixer.init(48000)
pygame.init()
pygame.event.set_blocked(None)
pygame.event.set_allowed((KEYDOWN, QUIT))
# noinspection PyArgumentList
pygame.key.set_repeat(75, 0)
screen = LEDScreen()
guiscreen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.update()

file = 'tetris.mp3'
pygame.mixer.music.load(file)
pygame.mixer.music.play()

print('Welcome to tetris!')
print('Original Tetris Theme (Tetris Soundtrack) Gameboy by Sanitaryum is licensed under a Creative Commons License (https://creativecommons.org/licenses/by-nc/3.0/).')
print('The music can be found at https://soundcloud.com/sanitaryum/original-tetris-theme-tetris')

while True:  # start(restart) game
    grid = [None] * CELLS
    speed = 1000
    screen.clear()
    while True:  # spawn a block
        block = choice([O, I, S, Z, L, J, T])()
        pos = POS_FIRST_APPEAR
        if not phi(grid, block.grid(pos, COLS, ROWS), pos):
            break  # you lose
        pygame.time.set_timer(KEYDOWN, speed)
        while True:  # move the block
            g = block.grid(pos, COLS, ROWS)
            draw(merge(grid, g), pos)
            event = pygame.event.wait()
            if event.type == QUIT:
                sys.exit()
            try:
                aim = {
                    K_UNKNOWN: pos+COLS,
                    K_UP: pos,
                    K_DOWN: pos+COLS,
                    K_LEFT: pos-1,
                    K_RIGHT: pos+1,
                    K_SPACE: None,
                }[event.key]
            except KeyError:
                continue
            if event.key == K_UP:
                block.rotate()
            elif event.key in (K_LEFT, K_RIGHT) and pos // COLS != aim // COLS:
                continue
            elif event.key == K_SPACE:
                pos_old = pos
                pos = max_pos(grid, block, pos)
                draw(grid, pos_old)
                draw(merge(grid, block.grid(pos, COLS, ROWS)), pos)
                break
            grid_aim = block.grid(aim, COLS, ROWS)
            if grid_aim and phi(grid, grid_aim, aim):
                pos = aim
            else:
                if event.key == K_UP:
                    block.rotate(times=3)
                elif event.key not in (K_LEFT, K_RIGHT):
                    break
        grid = merge(grid, block.grid(pos, COLS, ROWS))
        grid, n = complete(grid)
        if n:
            draw(grid)
            speed -= 5 * n
            if speed < 75:
                speed = 75
