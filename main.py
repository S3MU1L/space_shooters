import pygame
import os
import time
import random

pygame.init()
pygame.font.init()
pygame.display.set_caption("Random shooter game")
run = True
WHITE = (255,255,255)
RED = (255,0,0)
GREEN =  (0,255,0)
FPS = 60
WIDTH = 700
HEIGHT = 800
LEVEL = 0
LIVES = 5
SPEED = 10
LASER_VEL = 10
main_font = pygame.font.SysFont("comicsans",30)
lost_font = pygame.font.SysFont("comicsans",60)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
#we are going to import our pictures here:
#we have to transform the background to fit the canvas
background = pygame.transform.scale(pygame.image.load("background-black.png"),(WIDTH,HEIGHT))
#importing the ships :
player_img = pygame.image.load("pixel_ship_yellow.png")
blue_enemy = pygame.image.load("pixel_ship_blue_small.png")
green_enemy = pygame.image.load("pixel_ship_green_small.png")
red_enemy = pygame.image.load("pixel_ship_red_small.png")
#importing the projectiles:
player_bullet = pygame.image.load("pixel_laser_yellow.png")
blue_bullet = pygame.image.load("pixel_laser_blue.png")
green_bullet = pygame.image.load("pixel_laser_green.png")
red_bullet = pygame.image.load("pixel_laser_red.png")
#we will generate the x-coordinate of the player(y-coordinate will be set to HEIGHT-200)
x_player = random.randint(0,WIDTH-player_img.get_width())
y_player = HEIGHT-200
Sound_of_projectile = pygame.mixer.Sound("zvuk_hraca2.wav")
Sound_of_hit = pygame.mixer.Sound("zvuk_narazu.wav")
Sound_of_end = pygame.mixer.Sound("zvuk_konca.wav")
#at the beggining we haven't lost yet so we set this to False.
lost = False
lost_count = 0
PLAYING = False
enemies =  []
wave_lenght = 5
enemy_vel = 2

class Laser:
    def __init__(self,x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,screen):
        screen.blit(self.img,(self.x,self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self,height):
        return not(self.y <= height and self.y >= 0)

    def collision(self,object):
        return collide(object,self)


class Ship:
    #We want to shoot every half a second and the
    #way we do that is this
    COOLDOWN = FPS//2

    def __init__(self,x,y,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self,screen):
        screen.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(screen)

    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
                Sound_of_hit.play()


    def cooldown(self):
        if self.cool_down_counter>=self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter+=1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Player(Ship):

    def __init__(self,x,y,health = 100):
        super().__init__(x,y,health)
        self.ship_img = player_img
        self.laser_img = player_bullet
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            Sound_of_projectile.play()
            pygame.mixer.music.stop()

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        Sound_of_hit.play()
    def reset_health(self):
        self.health = self.max_health
    def healthbar(self,screen):
        pygame.draw.rect(screen, RED,(self.x, self.y+self.laser_img.get_height()+10, self.ship_img.get_width(), 10))
        pygame.draw.rect(screen, GREEN, (self.x, self.y + self.laser_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
        "red":(red_enemy,red_bullet),
        "green": (green_enemy,green_bullet),
        "blue": (blue_enemy,blue_bullet)
    }
    def __init__(self,x,y,color,health = 100):
        super().__init__(x,y,health)
        self.ship_img,self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self,vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1



player  = Player(x_player,y_player)

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def draw_window():
    screen.blit(background,(0,0))

    #draw text
    level_label = main_font.render(f'LEVEL:{LEVEL}',1,WHITE)
    lives_label = main_font.render(f'LIVES:{LIVES}',1,WHITE)
    screen.blit(lives_label,(10,10))
    screen.blit(level_label,(WIDTH-lives_label.get_width(),10))

    for enemy in enemies:
        enemy.draw(screen)

    player.draw(screen)
    player.healthbar(screen)
    if lost:
        lost_label = lost_font.render("You lost!",1,RED)
        screen.blit(lost_label,((WIDTH-lost_label.get_width())//2,HEIGHT//2))


    pygame.display.update()

def move_player(keys_pressed):
    if keys_pressed[pygame.K_LEFT]:
        if player.x - SPEED >= 0:
            player.x -= SPEED
    if keys_pressed[pygame.K_RIGHT]:
        if player.x + player_img.get_width() + SPEED <= WIDTH:
            player.x += SPEED
    if keys_pressed[pygame.K_DOWN]:
        if player.y + player_img.get_height() + SPEED <= HEIGHT:
            player.y += SPEED
    if keys_pressed[pygame.K_UP]:
        if player.y - SPEED >= 0:
            player.y -= SPEED
    if keys_pressed[pygame.K_SPACE]:
        player.shoot()

while run:
    clock.tick(FPS)
    draw_window()

    if LIVES <= 0 or player.health <= 0:
        lost = True
        lost_count += 1
        if PLAYING == False:
            Sound_of_end.play()
            PLAYING = True

    if lost:
        if lost_count > FPS*3:

            run = False
        else:
            continue

    if len(enemies)==0:
        LEVEL += 1
        wave_lenght += 5
        player.reset_health()
        enemy_vel = LEVEL//3 + 1
        for i in range(wave_lenght):
            enemy = Enemy(random.randrange(50,WIDTH-100),random.randrange(-1500,-100),random.choice(["red","blue","green"]))
            enemies.append(enemy)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys_pressed = pygame.key.get_pressed()
    #movement of the player ship
    move_player(keys_pressed)


    for enemy in enemies[:]:

        enemy.move(enemy_vel)
        enemy.move_lasers(LASER_VEL,player)
        if random.randrange(0, 4 * FPS) == 1:
            enemy.shoot()
        if enemy.y>HEIGHT:
            LIVES-=1
            enemies.remove(enemy)

        elif collide(enemy,player):
            player.health-=10
            enemies.remove(enemy)
            Sound_of_hit.play()
    player.move_lasers(-LASER_VEL, enemies)


