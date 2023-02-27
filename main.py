import csv
import os
import sys
from random import randint, choice, random

import pygame

pygame.init()
pygame.mixer.init()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)
FPS = 60
all_sprites = pygame.sprite.Group()
patron_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
mons_sprites = pygame.sprite.Group()
particle_count = 500
with open('data/levels.csv', encoding="utf8") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
    LEVELS = sorted(reader, key=lambda x: int(x['lev']))
LEV = 0

def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


ship_monster_im_1 = load_image('blue_ufo_gmc_0021.png', -1)
ship_monster_im_2 = load_image('green_ufo_gmc_0021.png', -1)
ship_monster_im_3 = load_image('red_ufo_gmc_0021.png', -1)


class Ship(pygame.sprite.Sprite):
    ship_im = load_image('Armature_shoot_up_1.png', -1)

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = Ship.ship_im
        self.rect = self.ship_im.get_rect()
        self.rect.x = width // 2
        self.rect.y = height - self.rect.height - 50
        self.life = 300

    def update(self):
        keystate = pygame.key.get_pressed()  # ????????
        if keystate[pygame.K_LEFT]:
            self.rect.x -= 4
        if keystate[pygame.K_RIGHT]:
            self.rect.x += 4
        if keystate[pygame.K_UP]:
            self.rect.y -= 2
        if keystate[pygame.K_DOWN]:
            self.rect.y += 2
        if self.rect.x > width - 105:
            self.rect.x = width - 105
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y > height - 84:
            self.rect.y = height - 84
        if self.rect.y < 0:
            self.rect.y = 0

    def buh(self):
        buh = Bum(self.rect.x + self.rect.width // 3, self.rect.y)
        all_sprites.add(buh)
        patron_sprites.add(buh)


class Bum(pygame.sprite.Sprite):
    bum_im = load_image('bum1.png', -1)

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Bum.bum_im
        self.rect = self.bum_im.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.y += -2


class Monster(pygame.sprite.Sprite):
    def __init__(self, img, lf):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = width // 4
        self.rect.y = 3
        self.life = lf
        self.dead = False

    def update(self):
        self.rect = self.rect.move(randint(-1, 1), randint(-1, 1))
        if self.life == 0:
            self.create_particles(self.rect.x, self.rect.y)
            self.kill()
            self.dead = True

    def create_particles(self, x, y):
        for _ in range(particle_count):
            Particle((x, y), choice(range(-50, 50)), choice(range(10, 50)))


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png", -1)]
    for scale in (2, 5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = choice(self.fire)
        self.rect = self.image.get_rect()
        # у каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos
        self.gravity = random()

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(0, 0, width, height):
            self.kill()


class Meteor(pygame.sprite.Sprite):
    met_im = load_image('air-002-Novaram_48x48.png', -1)

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = Meteor.met_im
        self.rect = self.met_im.get_rect()
        self.rect.x = randint(0, width - self.rect.width)
        self.rect.y = 0
        self.x = randint(-3, 3)
        self.y = randint(1, 2)

    def update(self):
        self.rect.x += self.x
        self.rect.y += self.y
        if self.rect.x > width - self.rect.width or self.rect.x < 0 or self.rect.y > height - self.rect.height:
            self.rect.x = randint(0, width - self.rect.width)
            self.rect.y = 0
            self.x = randint(-3, 3)
            self.y = randint(1, 5)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen1(screen):
    clock = pygame.time.Clock()
    intro_text = ["2250 год...",
                  "На планету Земля прилетели ПРИШЕЛЬЦЫ!!!",
                  "Твоя миссия спасти нашу планету!",
                  "НАЖМИ ЛЮБУЮ КЛАВИШУ...",
                  "...и начнется БИТВА..."
                  ]
    fon = pygame.transform.scale(load_image('nightskycolor.png'), (size))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 36)
    text_coord = 180
    for line in intro_text:
        string_rendered = font.render(line, 2, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 30
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def finish_screen(screen, win):
    pass


def main():
    pygame.display.set_caption("Космические войны!")
    clock = pygame.time.Clock()
    back = load_image('2070.jpg')
    back = pygame.transform.scale(back, (600, 600))
    back_size = back.get_rect()
    Win = False
    sh = Ship()
    all_sprites.add(sh)
    m_sh = Monster(ship_monster_im_1, 500)
    m_sh_2 = Monster(ship_monster_im_2, 1000)
    m_sh_3 = Monster(ship_monster_im_3, 3000)
    mons_sprites.add(m_sh)
    monsters = [m_sh, m_sh_2, m_sh_3]
    all_sprites.add(m_sh)
    bill = 0
    h_im = 0
    for i in range(5):
        met = Meteor()
        all_sprites.add(met)
        meteor_sprites.add(met)

    start_screen1(screen)

    running = True
    LEV = 0
    health = pygame.image.load('data\heartshealth.png')
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sh.buh()
        hits = pygame.sprite.groupcollide(meteor_sprites, patron_sprites, True, True)
        for _ in hits:
            met = Meteor()
            all_sprites.add(met)
            meteor_sprites.add(met)
            bill += 1
        hits = pygame.sprite.spritecollide(sh, meteor_sprites, False)
        if hits:
            sh.life -= 1
            h_im = (5 - sh.life // 60) * 42
            if sh.life <= 0:
                running = False

        hits = pygame.sprite.spritecollide(monsters[LEV], patron_sprites, False)
        if hits:
            monsters[LEV].life -= 1
        hits = pygame.sprite.groupcollide(patron_sprites, mons_sprites, True, False)

        screen.fill(pygame.Color("black"))
        all_sprites.draw(screen)
        all_sprites.update()
        screen.blit(back, back_size)
        all_sprites.draw(screen)
        screen.blit(health, (360, 550), (0, h_im, 283, 42))
        f1 = pygame.font.Font(None, 28)
        text1 = f1.render(f"Очки: {bill}", True, (240, 240, 0))
        screen.blit(text1, (10, 10))
        text2 = f1.render(f"Уровень: {LEV + 1}", True, (240, 240, 0))
        screen.blit(text2, (450, 10))
        if monsters[LEV].dead:
            LEV += 1
            text_w = 'Level 2'
            f3 = pygame.font.Font(None, 68)
            text3 = f3.render(text_w, True, ('white'))
            screen.blit(text3, (200, 300))
            if LEV < 3:
                all_sprites.add(monsters[LEV])
            else:
                running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

    # иконка
# icon = pygame.image.load("data/pics/icon32.png").convert()
# icon.set_colorkey(WHITE)
# pygame.display.set_icon(icon)