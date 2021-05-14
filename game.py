
import pygame
import random
import tetris_ai

colors = [
    (15, 155, 215),#I
    (215, 15, 55),#z
    (89, 117, 1),#reverse z
    (33, 65, 198),#reverse L
    (227, 91, 2),#L
    (175, 41, 138),#T
    (227, 159, 2),#O
    (7,77,107),#I shadow
    (107, 7, 27),#z shadow
    (44, 88, 0),#reverse z shadow
    (16, 32, 99),#reverse L shadow
    (113, 45, 1),#L shadow
    (87, 20, 69),#T shadow
    (113, 79, 1),#O shadow
    (70, 70, 70) #Junk
]

class Figure:
    x = 0
    y = 0

    figures = [
        [[4, 5, 6, 7],[2, 6, 10, 14], [8, 9, 10, 11], [1, 5, 9, 13]],
        [[4, 5, 9, 10], [2, 6, 5, 9],[5, 6, 10, 11],[6, 9, 10, 13]],
        [[6, 7, 9, 10], [5, 9, 10, 14], [5, 6, 8, 9],[1, 5, 6, 10]],
        [[0, 4, 5, 6], [1, 2, 5, 9], [4, 5, 6, 10], [1, 5, 9, 8]],
        [[2, 4, 5, 6], [1, 5, 9, 10], [4, 5, 6, 8], [0, 1, 5, 9]],
        [[1, 4, 5, 6], [1, 5, 6, 9], [4, 5, 6, 9], [1, 4, 5, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        rng=random.randint(0, len(self.figures) - 1)
        self.type = rng
        self.color = rng
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])

    def reset(self):
        self.rotation = 0

class Tetris:
    level = 1
    state = "start"
    field = []
    height = 0
    width = 0
    x = 100
    y = 60
    zoom = 20
    figure = None


    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.accjunk = []
        self.nextjunkid = 1
        self.field = []
        self.sendjunk=[]
        self.combo = -1
        self.pressing_down = False
        self.pressing_left = 0
        self.pressing_right = 0
        self.state = "start"
        self.holdfigure = None
        self.holdlock = False
        self.queue1 = None
        self.queue2 = None
        self.queue3 = None
        self.figure = None
        while self.figure is None:
            self.new_figure()
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(-1)
            self.field.append(new_line)
        self.resetshadow()

    def new_figure(self):
        self.figure = self.queue1
        self.queue1 = self.queue2
        self.queue2 = self.queue3
        self.queue3 = Figure(3,0)
        self.holdlock = False
        if self.figure is not None and self.field != []:
            self.resetshadow()

    def intersects(self,igap=0):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y + igap > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            (self.field[i + self.figure.y + igap][j + self.figure.x] > -1 and self.field[i + self.figure.y + igap][j + self.figure.x] < 7) or \
                            self.field[i + self.figure.y + igap][j + self.figure.x] ==14:
                        intersection = True
        return intersection

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == -1:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        if lines == 0:
            if self.accjunk != []:
                count = 0
                id = self.accjunk[0]
                for i in range(len(self.accjunk)):
                    if id != self.accjunk[i]:
                         self.junk_lines(count)
                         count = 1
                         id = self.accjunk[i]
                    else:
                        count += 1
                self.junk_lines(count)
                self.accjunk = []
            self.combo = -1
        else:
            totlinesent = lines - 1
            if lines == 4:
                totlinesent += 1
            if self.combo >= 7:
                totlinesent += 4
            elif self.combo >=5:
                totlinesent += 3
            elif self.combo >= 3:
                totlinesent += 2
            elif self.combo >= 2:
                totlinesent += 1
            for i in range(totlinesent):
                self.sendjunk.append(self.nextjunkid)
            self.nextjunkid = 1 - self.nextjunkid
            self.combo += 1

    def junk_lines(self,n):
        blankx=random.randint(0, self.width - 1)
        for i in range(1, self.height):
            if i + n < self.height:
                for j in range(self.width):
                    self.field[i][j] = self.field[i + n][j]
            else:
                for j in range(self.width):
                    if j == blankx:
                        self.field[i][j] = -1
                    else:
                        self.field[i][j] = 14

    def hold(self):
        if self.holdlock == False:
            self.figure.reset()
            self.holdfigure,self.figure = self.figure,self.holdfigure
            self.holdlock = True
            if self.figure is not None:
                self.figure.y = 0
                self.figure.x = 3
                self.resetshadow()

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x
        else:
            self.resetshadow()
			
    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.go_side(-1)
        if self.intersects():
            self.go_side(+2)
        if self.intersects():
            self.figure.rotation = old_rotation
        self.resetshadow()

    def resetshadow(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.field[i][j] >= 7 and self.field[i][j] != 14:
                        self.field[i][j]=-1
        gap=0
        while not self.intersects(gap):
            gap += 1
        gap -= 1
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y+gap][j + self.figure.x] = self.figure.color + 7

def rendering(game,topleftx,toplefty):
    #hold colour and grid
    for i in range(4):
        for j in range(4):
            pygame.draw.rect(screen, GRAY,[topleftx + game.x + game.zoom * (j) - (5 * game.zoom),
                                               game.y + game.zoom * (i) ,game.zoom, game.zoom],1)
            if game.holdfigure is not None:
                p = i * 4 + j
                if p in game.holdfigure.image():
                    pygame.draw.rect(screen, colors[game.holdfigure.color],
                                     [topleftx + game.x + game.zoom * (j) + 1 - (5 * game.zoom),
                                      game.y + game.zoom * (i) + 1,
                                      game.zoom - 2, game.zoom - 2])
    #queue 1 colour and grid
    if game.queue1 is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                pygame.draw.rect(screen, GRAY,[topleftx + game.x + game.zoom * (j) + ((1 + game.width) * game.zoom),
                                               game.y + game.zoom * (i) ,game.zoom, game.zoom],1)
                if p in game.queue1.image():
                    pygame.draw.rect(screen, colors[game.queue1.color],
                                     [topleftx + game.x + game.zoom * (j) + 1 + ((1 + game.width) * game.zoom),
                                      game.y + game.zoom * (i) + 1,
                                      game.zoom - 2, game.zoom - 2])
    #queue 2 colour and grid
    if game.queue2 is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                pygame.draw.rect(screen, GRAY,[topleftx + game.x + game.zoom * (j) + ((1 + game.width) * game.zoom),
                                               game.y + game.zoom * (i) + (5 * game.zoom),game.zoom, game.zoom],1)
                if p in game.queue2.image():
                    pygame.draw.rect(screen, colors[game.queue2.color],
                                     [topleftx + game.x + game.zoom * (j) + 1 + ((1 + game.width) * game.zoom),
                                      game.y + game.zoom * (i) + 1 + (5 * game.zoom),
                                      game.zoom - 2, game.zoom - 2])
    #queue 3 colour and grid
    if game.queue3 is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                pygame.draw.rect(screen, GRAY,[topleftx + game.x + game.zoom * (j) + ((1 + game.width) * game.zoom),
                                               game.y + game.zoom * (i) + (10 * game.zoom),game.zoom, game.zoom],1)
                if p in game.queue3.image():
                    pygame.draw.rect(screen, colors[game.queue3.color],
                                     [topleftx + game.x + game.zoom * (j) + 1 + ((1 + game.width) * game.zoom),
                                      game.y + game.zoom * (i) + 1 + (10 * game.zoom),
                                      game.zoom - 2, game.zoom - 2])
    #Acc junk line
    pygame.draw.rect(screen, (255,0,0), [topleftx + game.x + (game.width * game.zoom),game.y + (game.height - len(game.accjunk)) * game.zoom,
                                         game.zoom/4, len(game.accjunk)* game.zoom])
    #field colour and grid
    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRAY, [topleftx + game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
            if game.field[i][j] > -1:
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                 [topleftx + game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])
    #current figure colour
    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(screen, colors[game.figure.color],
                                     [topleftx + game.x + game.zoom * (j + game.figure.x) + 1,
                                      game.y + game.zoom * (i + game.figure.y) + 1,
                                      game.zoom - 2, game.zoom - 2])

def speedmove(game):
    if game.state == "start":
        if counter % (fps // game.level // 2) == 0 or game.pressing_down:
            game.go_down()

        if game.pressing_left>5: #Delay for sideway movements
            game.go_side(-1)
        elif game.pressing_left>0:
            game.pressing_left += 1

        if game.pressing_right>5:
            game.go_side(1)
        elif game.pressing_right>0:
            game.pressing_right += 1

def control(game,ctrl):
    for event in ctrl:
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN and game.state == "start" and comp.state == "start":
            if event.key == pygame.K_UP:
                game.rotate()
            if event.key == pygame.K_DOWN:
                game.pressing_down = True
            if event.key == pygame.K_LEFT:
                game.go_side(-1)
                game.pressing_left += 1
            if event.key == pygame.K_RIGHT:
                game.go_side(1)
                game.pressing_right += 1
            if event.key == pygame.K_SPACE:
                game.go_space()
            if event.key == pygame.K_LSHIFT:
                game.hold()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and (game.state == "gameover" or comp.state == "gameover"):
                game.__init__(heightinput, widthinput)
                comp.__init__(heightinput, widthinput)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN and game.pressing_down:
                game.pressing_down = False
            if event.key == pygame.K_LEFT and game.pressing_left > 0:
                game.pressing_left = 0
            if event.key == pygame.K_RIGHT and game.pressing_right > 0:
                game.pressing_right = 0

# Initialize the game engine
pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
heightinput = 30
widthinput = 10
size = (widthinput * 90,heightinput * 25 )
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Tetris")

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()
fps = 25
game = Tetris(heightinput, widthinput)
comp = Tetris(heightinput, widthinput)
counter = 0

while not done:
    if game.figure is None:
        game.new_figure()
    if comp.figure is None:
        comp.new_figure()
    counter += 1
    if counter > 100000:
        counter = 0

    if game.state == "start" and comp.state == "start":
        speedmove(game)
        speedmove(comp)
        if game.sendjunk != []:
            comp.accjunk += game.sendjunk
            game.sendjunk = []
        if comp.sendjunk != []:
            game.accjunk += comp.sendjunk
            comp.sendjunk = []
    control(game,pygame.event.get())
    control(comp,tetris_ai.run_ai(comp,counter))



    screen.fill(BLACK)
    rendering(game,0,0)
    rendering(comp,450,0)

    font = pygame.font.SysFont('Calibri', 25, True, False)
    font1 = pygame.font.SysFont('Calibri', 65, True, False)
    text = font.render("Score: " + str(game.combo), True, WHITE)
    text_game_over = font1.render("Game Over", True, (255, 0, 0))
    text_game_over1 = font1.render("Press ESC", True, WHITE)

    #screen.blit(text, [0, 0])
    if game.state == "gameover" or comp.state == "gameover":
        screen.blit(text_game_over, [20, 200])
        screen.blit(text_game_over1, [25, 265])
        if game.state == "gameover":
            screen.blit(font1.render("You lost!", True, (0, 255, 0)), [15, 130])
        elif comp.state == "gameover":
            screen.blit(font1.render("You won!", True, (0, 255, 0)), [15, 130])

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
