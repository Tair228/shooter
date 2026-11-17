import pygame
from random import *
from time import *
SCREENRECT = pygame.Rect(0, 0, 700, 500)
SCORE = 0
LOST = 0
class Sprite(pygame.sprite.Sprite):
    def __init__(self, file_name, x, y, width, height):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(file_name), (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(Sprite):
    num_fire = 0
    rel_time = False
    last_shot = 0
    def __init__(self, speed=10, x=102, y=399):
        super().__init__("rocket.png", x , y, 80, 100)
        self.speed = speed
    def update(self):
        x_before, y_before = self.rect.x, self.rect.y  # а где мы стоим до движения?
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_a] and SCREENRECT.left < self.rect.left:
            self.rect.x -=self.speed
        if key_pressed[pygame.K_d] and SCREENRECT.right > self.rect.right:
            self.rect.x += self.speed
        if self.rel_time:
            new_time = time()
            if new_time - self.last_shot >= 3:
                self.rel_time = False
                self.num_fire = 0
    def shot(self, shop):
        if not self.rel_time:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            shop.add(bullet)
            self.num_fire += 1
            if self.num_fire >= 5:
                self.rel_time = True
                self.last_shot = time()
    
    
        
class Monster(Sprite):
    def __init__(self, speed=5):
        super().__init__('ufo.png', 0, 0, 100, 80)
        self.speed = speed
        self.respawn()
    def update(self):
        self.rect.y += self.speed
        if self.rect.top >= SCREENRECT.bottom:
            self.respawn()
            global LOST
            LOST += 1
    def kill(self):
        global SCORE
        SCORE += 1
        return self.respawn()
    def respawn(self):
        self.rect.x = randint(SCREENRECT.left, SCREENRECT.right - self.rect.width)
        self.rect.y = randint(-SCREENRECT.bottom, SCREENRECT.top - self.rect.height)
class Bullet(Sprite):
    def __init__(self, x, y, speed=7):
        super().__init__('bullet.png', x-7, y, 15, 25)
        self.speed = speed
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom <= SCREENRECT.top:
            self.kill()
class Asteroid(Sprite):
    def __init__(self,speed=3):
        super().__init__('asteroid.png', 0, 0, 100, 80)
        self.speed = speed
        self.respawn()
    def update(self):
        self.rect.y += self.speed
        if self.rect.top >= SCREENRECT.bottom:
            self.respawn()
    def respawn(self):
        self.rect.x = randint(SCREENRECT.left, SCREENRECT.right - self.rect.width)
        self.rect.y = randint(-SCREENRECT.bottom, SCREENRECT.top - self.rect.height)
    def kill(self):
        self.respawn()

def main ():
    pygame.init()
    FPS = 60
    screen = pygame.display.set_mode(SCREENRECT.size)
    pygame.mixer.init()
    pygame.mixer.music.load('space.ogg')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    pygame.font.init()
    main_font = pygame.font.SysFont('candara', 60)
    bonus_font = pygame.font.SysFont('candara', 30)
    you_win = main_font.render('YOU WON', True,(255, 255, 255))
    you_lose = main_font.render("GAME OVER", True,(255, 255, 255))
    you_lost = bonus_font.render(f'Пропущено {LOST}', True,(255, 255, 255))
    you_score = bonus_font.render(f'Убито {SCORE}', True,  (255, 255, 255))
    you_wait = main_font.render("wait,reload...", True,(200, 100, 100))
    you_wait_rect = you_wait.get_rect(midbottom = SCREENRECT.midbottom)
    clock = pygame.time.Clock()  # счетчик кадров в секунду
    fon = pygame.transform.scale(pygame.image.load('galaxy.jpg'), (SCREENRECT.width, SCREENRECT.height))
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_monster = pygame.sprite.Group()
    all_bullet = pygame.sprite.Group()
    all_asteroid = pygame.sprite.Group()

    all_sprites.add(player)
    for i in range(4):
        monster = Monster()
        all_monster.add(monster)
        all_sprites.add(monster)
    for i  in range(2):
        asteroid = Asteroid()
        all_asteroid.add(asteroid)
        all_sprites.add(asteroid)


    game = True
    finish = False
    while game:
        for event in pygame.event.get():  # а что произошло?
            if event.type == pygame.QUIT:
                game = False

            elif event.type == pygame.KEYDOWN:  # нажали на какую-то клавишу
                if event.key == pygame.K_SPACE:
                    player.shot(all_bullet)

                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # где-то кликнули мышкой (левая кнопка)
                x, y = event.pos  # точка где кликнули
                print(x, y)
        if not finish:
            all_sprites.update()
            all_bullet.update()
            screen.fill((0, 0, 250))
            screen.blit(fon, (0, 0))
            you_lost = bonus_font.render(f'Пропущено {LOST}', True,(255, 255, 255))
            you_score = bonus_font.render(f'Убито {SCORE}', True,(255, 255, 255))
            screen.blit(you_lost, (0,0))
            screen.blit(you_score, (224,0))
            if player.rel_time:
                screen.blit(you_wait, you_wait_rect)

            all_bullet.draw(screen)
            all_sprites.draw(screen)
            pygame.sprite.groupcollide(all_monster, all_bullet, True, True)
            if SCORE >= 10:
                screen.blit(you_win, (174, 241))
                finish = True
            elif LOST >= 20:
                screen.blit(you_lose, (174, 241))
                finish = True
            if pygame.sprite.spritecollide(player, all_monster, True) or pygame.sprite.spritecollide(player, all_asteroid, True):
                screen.blit(you_lose, (174, 241))
                finish = True
        
        
        pygame.display.flip()  # pygame.display.update()
        clock.tick(FPS)  # обновляемся не чаще чем FPS
if __name__ == '__main__':
    main()
    pygame.quit()


    pygame.key.get_pressed()