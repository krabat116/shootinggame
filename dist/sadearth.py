import random
import sys
from time import sleep
import pygame
from pygame.locals import *

# 게임창 크기, 프레임 속도 설정 설정
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 640
FPS = 60

#색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_GRAY = (211, 211, 211)


class Fighter(pygame.sprite.Sprite):
    def __init__(self):
        super(Fighter, self).__init__()
        self.image = pygame.image.load('happytearth_100.png')
        self.rect = self.image.get_rect()
        self.rect.x = int(WINDOW_WIDTH / 2)
        self.rect.y = WINDOW_HEIGHT - self.rect.height
        self.dx = 0
        self.dy = 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.x < 0 or self.rect.x + self.rect.width > WINDOW_WIDTH:
            self.rect.x -= self.dx

        if self.rect.y < 0 or self.rect.y + self.rect.height > WINDOW_HEIGHT:
            self.rect.y -= self.dy

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self,sprite):
                return sprite


class Missile(pygame.sprite.Sprite):
    global mis_di

    def __init__(self, xpos, ypos, speed):
        super(Missile, self).__init__()
        tear_image = ['눈물_1.png', '눈물_2.png', '눈물_3.png']
        self.image = pygame.image.load(tear_image[mis_di])
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.speed = speed
        self.sound = pygame.mixer.Sound('lasershoot.wav')

    def launch(self):
        self.sound.play()

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y + self.rect.height < 0:
            self.kill()

    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                return sprite


class Rock(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, speed):
        super(Rock, self).__init__()
        rock_image = ['factory_b.png', 'co2_01.png', 'co2_02.png', 'co2_03.png', 'co2_04.png', 'radioactive.png']
        self.image = pygame.image.load(random.choice(rock_image))
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def out_of_screen(self):
        if self.rect.y > WINDOW_HEIGHT:
            return True

    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                return sprite


class Potion(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, speed):
        super(Potion, self).__init__()
        potion_image = ['organization01.png', 'organization02.png', 'animal01.png', 'animal02.png', ]
        self.image = pygame.image.load(random.choice(potion_image))
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def out_of_screen(self):
        if self.rect.y > WINDOW_HEIGHT:
            return True

    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                return sprite


class Ugrade(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, speed):
        super(Ugrade, self).__init__()
        upgrade_image = ('번개_1.png','번개_2.png')
        self.image = pygame.image.load(random.choice(upgrade_image))
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def out_of_screen(self):
        if self.rect.y > WINDOW_HEIGHT:
            return True

    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                return sprite


# 화면 텍스트 구성
def draw_text(text, font, surface, x, y, main_color):
    text_obj = font.render(text, True, main_color)
    text_rect = text_obj.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surface.blit(text_obj, text_rect)

# 폭발 발생 이미지 및 발생 함수
def occur_explosion(surface, x, y):
    explosion_image = pygame.image.load('heart02.png')
    explosion_rect = explosion_image.get_rect()
    explosion_rect.x = x
    explosion_rect.y = y
    surface.blit(explosion_image, explosion_rect)
    #소리
    explosion_sounds = ('kick-bass-drum.wav', 'yamaha-kick-soft.wav', 'bodacious.wav')
    explosion_sound = pygame.mixer.Sound(random.choice(explosion_sounds))
    explosion_sound.play()  # 재생


# 포션 먹었을 떄 이미지 및 소리 발생 함수
def occur_potion(surface, x, y):
    potion_image = pygame.image.load('heart01.png')
    potion_rect = potion_image.get_rect()
    potion_rect.x = x
    potion_rect.y = y
    potion_sounds = ('coin01.wav', 'coin02.wav', 'retro_heal.wav')
    potion_sound = pygame.mixer.Sound(random.choice(potion_sounds))
    potion_sound.play()
    surface.blit(potion_image, potion_rect)

# 게임 루프
def game_loop():
    global difficulty, mis_di, stage
    stage = 1
    default_font1 = pygame.font.Font('theboldfont.ttf', 20)
    background_image1 = ['background01.png', 'background_02 .png']
    background_image = pygame.image.load(background_image1[difficulty - 1])
    boom_sound = pygame.mixer.Sound('explosion01.wav')
    gameover_sound = pygame.mixer.Sound('die.wav')
    pygame.mixer.music.load('background_light.wav')
    pygame.mixer.music.play(-1)
    fps_clock = pygame.time.Clock()
    fighter = Fighter()
    missiles = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    potions = pygame.sprite.Group()
    upgrades = pygame.sprite.Group()

    occur_prob = 100   # 부정 이미지 발생 관련
    occur_prob2 = 300  # 긍정 이미지 발생 관련
    occur_prob3 = 500  # 번개 이미지 발생 관련
    energy = [200,100]       # 난이도 초기화
    damage = 0          # 데미지 초기화
    mis_di = 0          # 눈물 증가 변수 초기화
    shot_count = 0      # 맞춘 갯수
    count_missed = 0    # 놓친 갯수

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    fighter.dx -= 5
                elif event.key == pygame.K_RIGHT:
                    fighter.dx += 5
                elif event.key == pygame.K_UP:
                    fighter.dy -= 5
                elif event.key == pygame.K_DOWN:
                    fighter.dy += 5
                elif event.key == pygame.K_SPACE:
                    missile = Missile(fighter.rect.centerx, fighter.rect.y, 10)
                    missile.launch()
                    missiles.add(missile)
                elif event.key == pygame.K_DELETE:   # DELETE 키를 누르면 모든 부정이미지 제거
                    boom_sound.play()                # 폭탄이지만 미구현...
                    for rock in rocks:
                        rock.kill()
                elif event.key == pygame.K_ESCAPE:
                    pygame.mixer_music.stop()
                    done = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    fighter.dx = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    fighter.dy = 0

        screen.blit(background_image, background_image.get_rect())

        # 긍정적 이미지 발생 및 스피드
        occor_of_potions = 1 + int(shot_count / 2500)
        min_potion_speed = 1 + int(shot_count / 600)
        max_potion_speed = 1 + int(shot_count / 400)
        # 번개 발생 및 스피드
        occur_of_upgrades = 1 + int(shot_count / 5000)
        min_upgrade_speed = 1 + int(shot_count / 600)
        max_upgrade_speed = 1 + int(shot_count / 400)

        #난이도에 따른 부벙적 이미지 발생 및 스피드
        if difficulty == 1:
            occur_of_rocks = 1 + int(shot_count / 800)
            min_rock_speed = 1 + int(shot_count / 800)
            max_rock_speed = 1 + int(shot_count / 300)
        elif difficulty == 2:
            occur_of_rocks = (1 + int(shot_count / 800)) * 2
            min_rock_speed = (1 + int(shot_count / 800)) * 2
            max_rock_speed = (1 + int(shot_count / 400)) * 2

        # 부정 이미지 생성
        if random.randint(1, occur_prob) == 1:
            for i in range(occur_of_rocks):
                speed = random.randint(min_rock_speed, max_rock_speed) * 2
                rock = Rock(random.randint(0, WINDOW_WIDTH - 40), 0, speed)
                rocks.add(rock)

        # 긍긍 이미지 생생
        if random.randint(1, occur_prob2) == 1:
            for i in range(occor_of_potions):
                speed = random.randint(min_potion_speed, max_potion_speed)
                potion = Potion(random.randint(0, WINDOW_WIDTH - 40), 0, speed)
                potions.add(potion)

        # 번개 생성
        if random.randint(1, occur_prob3) == 1:
            for i in range(occur_of_upgrades):
                speed = random.randint(min_upgrade_speed, max_upgrade_speed)
                upgrade = Ugrade(random.randint(0, WINDOW_WIDTH - 40), 0, speed)
                upgrades.add(upgrade)

        draw_text('HP : {}'.format(energy[difficulty - 1] + shot_count - count_missed - damage),
                  default_font1,screen, 50, 20, GREEN)
        draw_text('stage {}'.format(stage), default_font1, screen, 240, 20, BLACK)

        # 스테이지 미구현
        if energy[difficulty - 1] + shot_count - count_missed - damage > 500:
            stage = 3
        elif energy[difficulty - 1] + shot_count - count_missed - damage > 300:
            stage = 2
        else:
            stage = 1

        # 눈물 충돌 처리
        for missile in missiles:
            rock = missile.collide(rocks)
            potion = missile.collide(potions)
            upgrade = missile.collide(upgrades)
            if rock:
                missile.kill()
                rock.kill()
                occur_explosion(screen, rock.rect.x, rock.rect.y)
                shot_count += 10
            elif potion:
                potion.kill()
                missile.kill()
                occur_explosion(screen, potion.rect.x, potion.rect.y)
            elif upgrade:
                upgrade.kill()
                missile.kill()
                occur_explosion(screen, upgrade.rect.x, upgrade.rect.y)

        # 긍정 이미지 처리
        for potion in potions:
            if fighter.collide(potions):
                potion.kill()
                occur_potion(screen, potion.rect.x, potion.rect.y)
                energy[difficulty - 1] += 100  # 이부분은 각 포션에 맞춰 매칭해야될듯
            elif potion.out_of_screen():
                potion.kill()

        # 눈물 upgrade
        for upgrade in upgrades:
            if fighter.collide(upgrades):
                upgrade.kill()
                occur_potion(screen, upgrade.rect.x, upgrade.rect.y)
                if mis_di == 2:
                    mis_di = 2
                elif mis_di < 2:
                    mis_di += 1

        # 부정적 이미지 처리
        for rock in rocks:
            if rock.out_of_screen():
                rock.kill()
                count_missed += 20
            elif fighter.collide(rocks):
                rock.kill()
                damage += 50 * difficulty
                occur_explosion(screen, fighter.rect.x, fighter.rect.y)
                pygame.display.update()

        upgrades.update()
        upgrades.draw(screen)
        potions.update()
        potions.draw(screen)
        rocks.update()
        rocks.draw(screen)
        missiles.update()
        missiles.draw(screen)
        fighter.update()
        fighter.draw(screen)
        pygame.display.flip()


        # 게임이 끝나는 조건
        if energy[difficulty - 1] + shot_count - count_missed - damage <= 0:
            pygame.mixer_music.stop()
            occur_explosion(screen, fighter.rect.x, fighter.rect.y)
            gameover_image = pygame.image.load('gameover.png')
            screen.blit(gameover_image, [0, 0])
            gameover_sound.play()
            pygame.display.update()
            sleep(2)
            done = True

        fps_clock.tick(FPS)  # 반복문의 프레임=60
    return 'game_menu'

def game_menu():
    global difficulty, mis_di
    start_image = pygame.image.load('sadearth_480x640.png')
    screen.blit(start_image, [0, 0])
    draw_x = int(WINDOW_WIDTH / 2)
    draw_y = int(WINDOW_HEIGHT / 2)
    font_90 = pygame.font.Font('theboldfont.ttf', 90)
    font_40_1 = pygame.font.Font('theboldfont.ttf', 40)

    draw_text(" EARTH LIFE ", font_90, screen, draw_x, draw_y - 180, BLACK)
    draw_text("METTER", font_90, screen, draw_x, draw_y + 220, BLACK)
    draw_text("MODE1     MODE2", font_40_1, screen, draw_x, draw_y + 280, WHITE)

    pygame.display.update()

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                difficulty = 1
                screen.fill(BLACK)
                loading_image = pygame.image.load('happyearth_main.png')
                screen.blit(loading_image, [0, 0])
                draw_text("LEVEL_01", font_40_1, screen, draw_x, draw_y + 300, WHITE)
                pygame.display.update()
                sleep(2)
                return 'play'
            elif event.key == pygame.K_2:
                difficulty = 2
                screen.fill(BLACK)
                loading_image = pygame.image.load('happyearth_main.png')
                screen.blit(loading_image, [0, 0])
                draw_text("LEVEL_02", font_40_1, screen, draw_x, draw_y + 300, WHITE)
                pygame.display.update()
                sleep(2)
                return 'play'
        if event.type == QUIT:
            difficulty = 0
            return 'quit'
    return 'game_menu'

# 메뉴 들가기전 메인
def main():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('지구가 아파요')
    pygame.display.update()

    action = 'game_menu'
    while action != 'quit':
        if action == 'game_menu':
            action = game_menu()
        elif action == 'play':
            action = game_loop()

    pygame.quit()

if __name__ == "__main__":
    main()