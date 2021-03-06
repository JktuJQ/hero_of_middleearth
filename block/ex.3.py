import pygame
import pyganim
from pygame import *


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2
    l = min(0, l)
    l = max(-(camera.width - WIN_WIDTH), l)
    t = max(-(camera.height - WIN_HEIGHT), t)
    t = min(0, t)

    return Rect(l, t, w, h)


def main():
    pygame.init()
    hero = Player(410, 95)
    entities.add(hero)
    left = right = False
    up = down = False
    weapon = 1
    screen = pygame.display.set_mode(DISPLAY) # Создаем окошко
    pygame.display.set_caption("First top game") # Пишем в шапку
    bg = Surface((WIN_WIDTH, WIN_HEIGHT)) # Создание видимой поверхности
    bg.fill(Color(BACKGROUND_COLOR))
    total_level_width = len(level[0]) * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
    total_level_height = len(level) * PLATFORM_HEIGHT
    camera = Camera(camera_configure, total_level_width, total_level_height)
    while 1:
        if not door:
            timer.tick(20)
            pos = ('', '')
            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                if e.type == KEYDOWN and e.key == K_LEFT:
                    left = True
                if e.type == KEYDOWN and e.key == K_RIGHT:
                    right = True
                if e.type == KEYUP and e.key == K_RIGHT:
                    right = False
                if e.type == KEYUP and e.key == K_LEFT:
                    left = False
                if e.type == KEYDOWN and e.key == K_UP:
                    up = True
                if e.type == KEYUP and e.key == K_UP:
                    up = False
                if e.type == KEYDOWN and e.key == K_DOWN:
                    down = True
                if e.type == KEYUP and e.key == K_DOWN:
                    down = False
                if e.type == pygame.MOUSEBUTTONDOWN:
                    pos = e.pos
                if e.type == KEYUP and e.key == K_1:
                    weapon = 1
                if e.type == KEYUP and e.key == K_2:
                    weapon = 2
            screen.blit(bg, (0, 0))
            hero.update(left, right, up, down, pos, weapon, platforms)
            for i in bullets:
                i.update()
            camera.update(hero)
            for e in entities:
                screen.blit(e.image, camera.apply(e))
            pygame.display.update()


class Player(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        boltAnim = []
        self.xvel = 0  # скорость перемещения. 0 - стоять на месте
        self.startX = x  # Начальная позиция Х, пригодится когда будем переигрывать уровень
        self.startY = y
        self.yvel = 0  # скорость вертикального перемещения
        self.image = Surface((WIDTH, HEIGHT))
        self.image.fill('white')
        self.rect = Rect(x, y, WIDTH, HEIGHT)
        for anim in ANIMATION_STAY:
            boltAnim.append((anim, ANIMATION_DELAY))
        self.boltStay = pyganim.PygAnimation(boltAnim)
        self.boltStay.play()
        boltAnim = []
        for anim in ANIMATION_RIGHT:
            boltAnim.append((anim, ANIMATION_DELAY))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.play()

    def get_cord(self):
        return (self.rect.x, self.rect.y)

    def update(self, left, right, up, down, pos, weap, platforms):
        if pos != ('', ''):
            self.weapon(pos, weap)

        if left and not right:
            self.xvel = -MOVE_SPEED  # Лево = x- n

        if right and not left:
            self.xvel = MOVE_SPEED
            self.image.set_colorkey("WHITE")
            self.boltAnimRight.blit(self.image, (0, 0))
        if not (left or right):
            self.xvel = 0

        if not (up or down):
            self.yvel = 0

        if (not (left or right)) and (not (up or down)):
            self.image.set_colorkey("WHITE")
            self.boltStay.blit(self.image, (0, 0))
        if up:
            self.yvel = -MOVE_SPEED
        if down:
            self.yvel = +MOVE_SPEED
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0, platforms)

    def weapon(self, pos, weap):
        bullet = Bullet(self.rect.x + 15, self.rect.y + 15, pos[0], pos[1], INVENTORY[weap])
        entities.add(bullet)
        bullets.add(bullet)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
                if xvel > 0:  # вправо
                    self.rect.right = p.rect.left  # то не движется вправо

                if xvel < 0:  # влево
                    self.rect.left = p.rect.right  # то не движется влево

                if yvel > 0:  # вниз
                    self.rect.bottom = p.rect.top  # то не падает вниз
                    self.yvel = 0

                if yvel < 0:
                    self.rect.top = p.rect.bottom  # то не движется вверх
                    self.yvel = 0
        for p in doors:
            if sprite.collide_rect(self, p):
                if xvel > 0:
                    door = True  # то не движется вправо

                if xvel < 0:  # влево
                    door = True  # то не движется влево

                if yvel > 0:  # вниз
                    door = True

                if yvel < 0:
                    door = True

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, x1, y1, type):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((15, 10))
        self.image.fill('YELLOW')
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
        self.mouse_x = x1
        self.distan = 0
        self.dist = INVENTORY_PROP[type][0]
        self.power = INVENTORY_PROP[type][1]
        self.mouse_y = y1

    def update(self):
        import math
        speed = 4
        distance = [self.mouse_x - self.rect.x, self.mouse_y - self.rect.y]
        print(distance)
        if distance == 0:
            self.distan = distance
        norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
        for p in platforms:
            if sprite.collide_rect(self, p):
                self.kill()
        if int(norm) < 5:
            self.kill()
        else:
            direction = [distance[0] / norm, distance[1] / norm]
            bullet_vector = [direction[0] * speed, direction[1] * speed]

            self.rect.x += bullet_vector[0]
            self.rect.y += bullet_vector[1]



class Platform(sprite.Sprite):
    def __init__(self, x, y, status):
        sprite.Sprite.__init__(self)
        if status == 'wall':
            self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
            self.image = image.load("block/wall.png")
            self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        elif status == 'tree':
            self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
            self.image = image.load("block/Tree.png")
            self.image.set_colorkey("WHITE")
            self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        elif status == 'build':
            self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
            self.image = image.load("block/build.png")
            self.image.set_colorkey("WHITE")
            self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        elif status == 'top':
            self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
            self.image = image.load("block/top.png")
            self.image.set_colorkey("WHITE")
            self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        elif status == 'window':
            self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
            self.image = image.load("block/window.png")
            self.image.set_colorkey("WHITE")
            self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        elif status == 'door':
            self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
            self.image = image.load("block/door.png")
            self.image.set_colorkey("WHITE")
            self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class Door(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = image.load("block/door.png")
        self.image.set_colorkey("WHITE")
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class Floor(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = image.load("block/floor1.png")
        self.image.set_colorkey("WHITE")
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


WIN_WIDTH = 800  # Ширина создаваемого окна
WIN_HEIGHT = 640  # Высота
INVENTORY = ['gun', 'sword']
bullets = pygame.sprite.Group()
INVENTORY_PROP = {'gun': [200, 20], 'sword': [50, 50]}
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "#004400"
PLATFORM_WIDTH = 32
ANIMATION_DELAY = 1
ANIMATION_STAY = [('block/Player/pass1.png'), ('block/Player/pass2.png')]
ANIMATION_RIGHT = [('block/Player/go_r_l.png'),
                   ('block/Player/go_r_stay.png'),
                   ('block/Player/go_r_r.png'),
                   ('block/Player/go_r_stay.png')]
PLATFORM_HEIGHT = 32
door = False
floor = []
timer = pygame.time.Clock()
entities = pygame.sprite.Group()
platforms = []
doors = []
level = [
        "----------------------------------",
        "- kkkkkkk          ***********   -",
        "- bbbbbbb                        -",
        "- b+bbb+b                        -",
        "- bbbdbbb    --                  -",
        "-                                -",
        "---   -------------------        -",
        "-                                -",
        "-         ------------------------",
        "-                                -",
        "-------------------------        -",
        "-                                -",
        "-        -------------------------",
        "-                                -",
        "-                                -",
        "-      -                         -",
        "-                                -",
        "-                                -",
        "-                                -",
        "-                         -      -",
        "-                            --  -",
        "-                                -",
        "-                                -",
        "-                                -",
        "- kkkkkkk                        -",
        "- bbbbbbb                        -",
        "- b+bbb+b                        -",
        "- bbbdbbb    --                  -",
        "-                                -",
        "---   -------------------        -",
        "-                                -",
        "-         ------------------------",
        "-                                -",
        "-------------------------        -",
        "-                                -",
        "-        -------------------------",
        "-                                -",
        "-                                -",
        "-      -                         -",
        "-                                -",
        "-                                -",
        "-                                -",
        "-                         -      -",
        "-                            --  -",
        "-                                -",
        "-                                -",
        "----------------------------------"]
level1 = [
        "----------------------------------",
        "-                  ***********   -",
        "-                                -",
        "-  kkkkk                         -",
        "-  bbdbb     --                  -",
        "-                                -",
        "---   -------------------        -",
        "-                                -",
        "-         ------------------------",
        "-                                -",
        "-------------------------        -",
        "-                                -",
        "-        -------------------------",
        "-                                -",
        "-                                -",
        "-      -                         -",
        "-                                -",
        "-                                -",
        "-                                -",
        "-                         -      -",
        "-                            --  -",
        "-                                -",
        "-                                -",
        "-                                -",
        "- kkkkkkk                        -",
        "- bbbbbbb                        -",
        "- b+bbb+b                        -",
        "- bbbdbbb    --                  -",
        "-                                -",
        "---   -------------------        -",
        "-                                -",
        "-         ------------------------",
        "-                                -",
        "-------------------------        -",
        "-                                -",
        "-        -------------------------",
        "-                                -",
        "-                                -",
        "-      -                         -",
        "-                                -",
        "-                                -",
        "-                                -",
        "-                         -      -",
        "-                            --  -",
        "-                                -",
        "-                                -",
        "----------------------------------"]

x = y = 0
for row in level:  # вся строка
    for col in row:  # каждый символ
        if col == "-":
            pf = Platform(x, y, 'wall')
            entities.add(pf)
            platforms.append(pf)
        elif col == '*':
            pf = Platform(x, y, 'tree')
            entities.add(pf)
            platforms.append(pf)
        elif col == 'b':
            pf = Platform(x, y, 'build')
            entities.add(pf)
            platforms.append(pf)
        elif col == 'k':
            pf = Platform(x, y, 'top')
            entities.add(pf)
            platforms.append(pf)
        elif col == 'd':
            pf = Door(x, y)
            entities.add(pf)
            doors.append(pf)
        elif col == '+':
            pf = Platform(x, y, 'window')
            entities.add(pf)
            platforms.append(pf)
        elif col == ' ':
            pf = Floor(x, y)
            entities.add(pf)
        x += PLATFORM_WIDTH  # блоки платформы ставятся на ширине блоков
    y += PLATFORM_HEIGHT  # то же самое и с высотой
    x = 0
MOVE_SPEED = 7
WIDTH = 22
HEIGHT = 32
COLOR = "#888888"
GRAVITY = 0.35
JUMP_POWER = 10

if __name__ == "__main__":
    main()
