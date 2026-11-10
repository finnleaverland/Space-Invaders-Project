import os
import random

import pygame
from pygame.locals import K_ESCAPE, K_LEFT, K_RIGHT, K_SPACE, KEYDOWN, QUIT

#Asset folders, so the images and sounds load whatever folder you run from
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(PROJECT_ROOT, "assets", "images")
SOUND_DIR = os.path.join(PROJECT_ROOT, "assets", "sounds")

#Window
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60
WINDOW_TITLE = "Space Invaders"

#Colours and fonts
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FONT_NAME = "arial"
FONT_SIZE = 32
BIG_FONT_SIZE = 60

#Text positions
SCORE_LABEL_POS = (1, 1)
SCORE_VALUE_POS = (130, 1)
LIVES_LABEL_POS = (450, 1)
LIVES_VALUE_POS = (560, 1)
GAME_OVER_POS = (SCREEN_WIDTH / 2 - 130, SCREEN_HEIGHT / 2 + 100)
RETURN_HINT_POS = (SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 + 170)

#Player
PLAYER_START_POS = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70)
PLAYER_SPEED = 4  #pixels per frame
PLAYER_LIVES = 5
PLAYER_SHOT_COOLDOWN = 30  #frames between shots
PLAYER_BULLET_X_OFFSET = 10  #bullets leave the ship slightly right of centre
FRAME_COUNTER_LIMIT = 1_000_000  #the shot counter wraps back to 0 after this
BULLET_SPEED = 4  #pixels per frame, upwards

#Aliens
ALIEN_IMAGES = ("alien1.png", "alien2.png", "alien3.png", "alien4.png")
ALIEN_ROWS = 5
ALIEN_COLUMNS = 5
ALIEN_GRID_LEFT = 100
ALIEN_GRID_TOP = 150
ALIEN_SPACING_X = 100
ALIEN_SPACING_Y = 70
ALIEN_MOVE_RANGE = 70  #pixels either side of where each alien starts
ALIEN_SHOT_COOLDOWN = 1000  #milliseconds between alien shots
ALIEN_BULLET_SPEED = 3  #pixels per frame, downwards
ALIEN_POINTS = 10
WAVE_BONUS = 100  #points for clearing a wave (not given for the first wave)

#Mystery alien
MYSTERY_START_POS = (100, 80)
MYSTERY_MOVE_RANGE = 400  #pixels it travels before turning round
MYSTERY_SPAWN_DELAY = 1050  #milliseconds after the last one before a new one appears
EXTRA_LIFE = "extra life"
MYSTERY_REWARDS = (EXTRA_LIFE, 100, 150, 200)  #one is picked at random

#Explosions (how many frames they stay on screen)
ALIEN_EXPLOSION_FRAMES = 10
PLAYER_EXPLOSION_FRAMES = 5


def image_path(filename):
    """full path to an image file"""
    return os.path.join(IMAGE_DIR, filename)


def sound_path(filename):
    """full path to a sound file"""
    return os.path.join(SOUND_DIR, filename)


#These are set up in setup_game() when a game starts, not when the file is imported,
#so the game window only opens once the player presses Play
screen = None
clock = None
background = None
font = None
big_font = None
explosion1_sound = None
explosion2_sound = None
laser_sound = None
player = None


def draw_background():
    screen.blit(background, (0, 0))


def draw_text(surface, text, text_font, text_colour, position):
    text_image = text_font.render(text, True, text_colour)
    surface.blit(text_image, position)


####Player Class####
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path("spaceship.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.count = 0
        self.cooldown = PLAYER_SHOT_COOLDOWN
        self.score = 0
        self.lives = PLAYER_LIVES

    #Move the sprite based on user keypresses
    def update(self, pressed_keys):
        #a dead player can't move or shoot
        if self.lives <= 0:
            return

        self.count += 1
        if self.count > FRAME_COUNTER_LIMIT:
            self.count = 0
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-PLAYER_SPEED, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(PLAYER_SPEED, 0)

        #Does the player want too shoot?
        if pressed_keys[K_SPACE] and self.count % self.cooldown == 0:
            laser_sound.play()
            bullet = Bullet(self.rect.centerx + PLAYER_BULLET_X_OFFSET, self.rect.top)
            bullet_group.add(bullet)

        #Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def hit(self):
        """called when an alien bullet hits the player"""
        if self.lives <= 0:
            return
        self.lives -= 1
        #Does the player die?
        if self.lives <= 0:
            self.lives = 0
            explosion2_sound.play()
            player_explosion_group.add(PlayerExplosion(self.rect.centerx, self.rect.centery))
            self.kill()


####Player bullets Class####
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path("bullet.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        """move the bullet up the screen every loop"""
        self.rect.y -= BULLET_SPEED
        #has the bullet left the screen if so delete the bullet
        if self.rect.bottom < 0:
            self.kill()
        #Is it True that a bullet itself has hit an alien from the alien_group
        if pygame.sprite.spritecollide(self, alien_group, True):
            player.score += ALIEN_POINTS
            self.kill()
            explosion1_sound.play()
            alien_explosion_group.add(AlienExplosion(self.rect.centerx, self.rect.centery))


####Aliens Class####
class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path(random.choice(ALIEN_IMAGES))).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0  #how far the alien is from where it started
        self.move_direction = 1

    def update(self):
        """moves the aliens left and right, up to ALIEN_MOVE_RANGE pixels either side of where they started"""
        #move in x direction by 1 pixel every update
        self.rect.x += self.move_direction
        self.move_counter += self.move_direction
        if abs(self.move_counter) >= ALIEN_MOVE_RANGE:
            self.move_direction *= -1  #change direction


def create_aliens():
    """creates the rows of aliens"""
    for row in range(ALIEN_ROWS):
        for column in range(ALIEN_COLUMNS):
            x = ALIEN_GRID_LEFT + column * ALIEN_SPACING_X
            y = ALIEN_GRID_TOP + row * ALIEN_SPACING_Y
            alien_group.add(Alien(x, y))


####Alien bullets Class####
class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path("alien_bullet.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        #move the bullet down every loop
        self.rect.y += ALIEN_BULLET_SPEED
        #has the bullet left the screen if so delete the bullet
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
        #Is it True that an alien bullet itself has hit the player
        if pygame.sprite.spritecollide(self, player_group, False):
            self.kill()
            player.hit()


####Mystery alien####
class MysteryAlien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path("mysteryalien.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0  #how far it has moved from where it started
        self.move_direction = 1

    def update(self):
        """moves the mystery alien left and right across the top of the screen"""
        #move in x direction by 1 pixel every update
        self.rect.x += self.move_direction
        self.move_counter += self.move_direction
        if self.move_counter >= MYSTERY_MOVE_RANGE or self.move_counter <= 0:
            self.move_direction *= -1  #change direction
        if pygame.sprite.spritecollide(self, bullet_group, True):
            explosion1_sound.play()
            alien_explosion_group.add(AlienExplosion(self.rect.centerx, self.rect.centery))
            reward = random.choice(MYSTERY_REWARDS)
            if reward == EXTRA_LIFE:
                player.lives += 1
            else:
                player.score += reward
            self.kill()


def create_mystery_alien():
    mystery_alien_group.add(MysteryAlien(*MYSTERY_START_POS))


####Alien_explosion class####
class AlienExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path("explosion1.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= ALIEN_EXPLOSION_FRAMES:
            self.kill()


####Player_explosion class####
class PlayerExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path("explosion2.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= PLAYER_EXPLOSION_FRAMES:
            self.kill()


#set up groups
player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
mystery_alien_group = pygame.sprite.Group()
alien_explosion_group = pygame.sprite.Group()
player_explosion_group = pygame.sprite.Group()

all_groups = [player_group, bullet_group, alien_group, alien_bullet_group,
              mystery_alien_group, alien_explosion_group, player_explosion_group]


def setup_game():
    """starts pygame, opens the window, loads everything and resets the game
    so you can play more than once without restarting the program"""
    global screen, clock, background, font, big_font
    global explosion1_sound, explosion2_sound, laser_sound, player

    pygame.init()
    pygame.mixer.init()

    #Create the screen object
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    background = pygame.image.load(image_path("background.png")).convert()

    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    big_font = pygame.font.SysFont(FONT_NAME, BIG_FONT_SIZE)

    #load sounds:
    explosion1_sound = pygame.mixer.Sound(sound_path("explosion.wav"))
    explosion2_sound = pygame.mixer.Sound(sound_path("explosion2.wav"))
    laser_sound = pygame.mixer.Sound(sound_path("laser.wav"))

    #clear anything left over from the last game
    for group in all_groups:
        group.empty()

    #create an instance of the Player class
    player = Player(*PLAYER_START_POS)
    player_group.add(player)


#Main loop:
def main():
    """plays one game and returns the score"""
    setup_game()

    #timer as soon as the game starts
    last_alien_shot = pygame.time.get_ticks()
    last_mystery_spawn = pygame.time.get_ticks()

    running = True
    while running:
        #sets the clock speed
        clock.tick(FPS)

        #current time within the game
        now = pygame.time.get_ticks()

        # for loop through the event queue
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                #once the game is over, space goes back to the menu
                elif event.key == K_SPACE and player.lives <= 0:
                    running = False

        #gets the keys pressed
        pressed_keys = pygame.key.get_pressed()

        #create the mystery alien
        if not mystery_alien_group and now - last_mystery_spawn > MYSTERY_SPAWN_DELAY:
            create_mystery_alien()
            last_mystery_spawn = now

        #create the aliens when there are no aliens left
        if not alien_group:
            #no bonus for the very first wave
            if player.score > 0:
                player.score += WAVE_BONUS
            create_aliens()

        #Alien shooting: after a certain amount of time the enemy shoots
        if player.lives > 0 and now - last_alien_shot > ALIEN_SHOT_COOLDOWN:
            shooter = random.choice(alien_group.sprites())
            alien_bullet_group.add(AlienBullet(shooter.rect.centerx, shooter.rect.bottom))
            laser_sound.play()
            last_alien_shot = now

        #update player
        player.update(pressed_keys)

        #update groups
        bullet_group.update()
        alien_group.update()
        alien_bullet_group.update()
        alien_explosion_group.update()
        player_explosion_group.update()
        mystery_alien_group.update()

        #draw the background
        draw_background()

        # Draw the player on the screen
        player_group.draw(screen)

        #draw groups onto the screen
        bullet_group.draw(screen)
        alien_group.draw(screen)
        alien_bullet_group.draw(screen)
        alien_explosion_group.draw(screen)
        player_explosion_group.draw(screen)
        mystery_alien_group.draw(screen)

        #draw score
        draw_text(screen, "SCORE", font, GREEN, SCORE_LABEL_POS)
        draw_text(screen, str(player.score), font, GREEN, SCORE_VALUE_POS)

        #draw lives
        draw_text(screen, "LIVES", font, GREEN, LIVES_LABEL_POS)
        draw_text(screen, str(player.lives), font, GREEN, LIVES_VALUE_POS)

        if player.lives <= 0:
            draw_text(screen, "GAME OVER", big_font, RED, GAME_OVER_POS)
            draw_text(screen, "SPACE TO GO BACK TO MAIN SCREEN", font, RED, RETURN_HINT_POS)

        # Update the display
        pygame.display.flip()

    score = player.score
    #close the game window and go back to the menu
    pygame.quit()
    return score


if __name__ == "__main__":
    print("Score:", main())
