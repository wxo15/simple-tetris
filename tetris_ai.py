import pygame
import numpy as np

class Event():
    type = None
    key = None

    def __init__(self, type, key):
        self.type = type
        self.key = key

def run_ai(game,counter):
    if counter % 5 != 0:
        return [Event(pygame.KEYUP, pygame.K_UP),
                Event(pygame.KEYUP, pygame.K_DOWN),
                Event(pygame.KEYUP, pygame.K_LEFT),
                Event(pygame.KEYUP, pygame.K_RIGHT)]
    rotation, position = best_rotation_position(game)
    if game.figure.rotation != rotation:
        e = Event(pygame.KEYDOWN, pygame.K_UP)
    elif game.figure.x < position:
        e = Event(pygame.KEYDOWN, pygame.K_RIGHT)
    elif game.figure.x > position:
        e = Event(pygame.KEYDOWN, pygame.K_LEFT)
    else:
        e = Event(pygame.KEYDOWN, pygame.K_SPACE)
    return [e]

def best_rotation_position(game):
    best_height = game.height
    best_holes = game.height*game.width
    best_position = None
    best_rotation = None
    hole_weight = 0.9
    best_metric = hole_weight*(game.height* game.width) + (1-hole_weight)*(game.height * (game.width-1))

    for rotation in range(len(game.figure.figures[game.figure.type])):
        fig = game.figure.figures[game.figure.type][rotation]
        for j in range(-3, game.width):
            if not intersects(game,fig,j):
                holes, height = simulate(game,fig,j)
                if best_position is None or \
                    best_metric > hole_weight*holes + (1-hole_weight)*height:
                    best_metric = hole_weight*holes + (1-hole_weight)*height
                    best_height = height
                    best_holes = holes
                    best_position = j
                    best_rotation = rotation
    return best_rotation, best_position

def simulate(game,figure,position):
    ygap=0
    while not intersects(game, figure, position,ygap):
        ygap += 1
    ygap -= 1
    height = game.height
    holes = 0
    filled = []
    breaks = 0
    topheight=[]
    topheight.extend([game.height]*game.width)
#    print(topheight)
    for j in range(game.width):
        startfill=False
        for i in range(0,game.height, 1):
            u = '_'
            if game.field[i][j] != -1 and game.field[i][j] < 7:
                u = "x"
            for ii in range(4):
                for jj in range(4):
                    if ii * 4 + jj in figure:
                        if jj + position == j and ii + game.figure.y + ygap == i:
                            u = "x"
            if u == "x" and i < topheight[j]:
                topheight[j] = i
            if u == "x":
                startfill = True
            if startfill and u == '_':
                holes += 1
    topheight = [game.height-x for x in topheight]
    cumheight = 0
#    print(game.field)
#    print (ygap)
#    print(figure)
#    print(topheight)
    for i in range(len(topheight)-1):
        cumheight = cumheight + abs(topheight[i] - topheight[i+1])
#    print([holes, cumheight])
    return holes, cumheight

def intersects(self,figure,position,igap=0):
    intersection = False
    for i in range(4):
        for j in range(4):
            if i * 4 + j in figure:
                if i + self.figure.y + igap > self.height - 1 or \
                        j + position > self.width - 1 or \
                        j + position < 0 or \
                        (self.field[i + self.figure.y + igap][j + position] > -1 and self.field[i + self.figure.y + igap][j + position] < 7) or \
                        self.field[i + self.figure.y + igap][j + position] == 14:
                    intersection = True

    return intersection


