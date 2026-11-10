import os
import random

import pygame

from pygame.locals import (
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

#Asset folders, so the images and sounds load whatever folder you run from
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(PROJECT_ROOT, "assets", "images")
SOUND_DIR = os.path.join(PROJECT_ROOT, "assets", "sounds")

def image_path(filename):
    """full path to an image file"""
    return os.path.join(IMAGE_DIR, filename)

def sound_path(filename):
    """full path to a sound file"""
    return os.path.join(SOUND_DIR, filename)

#Define constants for the screen width and height
screen_width = 600
screen_height = 800

#define the fps:
fps = 60

green = (0,255,0)
red = (255,0,0)

#These are set up in setup_game() when a game starts, not when the file is imported,
#so the game window only opens once the player presses Play
screen = None
clock = None
background = None
font = None
font2 = None
explosion1_sound = None
explosion2_sound = None
laser_sound = None
player = None


def draw_background():
    screen.blit(background, (0,0))


def draw_text(screen, text, font, text_colour, x, y):
    image = font.render(text, True, text_colour)
    screen.blit(image, (x,y))


####Player Class####
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Player, self).__init__()
        self.image = pygame.image.load(image_path("spaceship.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.count = 0
        self.cooldown = 30
        self.score = 0
        self.lives = 5

    #Move the sprite based on user keypresses
    def update(self, pressed_keys):
        #a dead player can't move or shoot
        if self.lives <= 0:
            return

        self.count += 1
        if self.count > 1000000:
            self.count = 0
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-4, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(4, 0)

    #Does the player want too shoot?
        if pressed_keys[K_SPACE] and self.count % self.cooldown == 0:
            laser_sound.play()
            bullet = Bullet(self.rect.centerx +10, self.rect.top)
            bullet_group.add(bullet)

    #Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height

    def hit(self):
        """called when an alien bullet hits the player"""
        if self.lives <= 0:
            return
        self.lives -= 1
        #Does the player die?
        if self.lives <= 0:
            self.lives = 0
            explosion2_sound.play()
            explosion2 = Player_explosion(self.rect.centerx, self.rect.centery)
            player_explosion_group.add(explosion2)
            self.kill()


####Player bullets Class####
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Bullet, self).__init__()
        self.image = pygame.image.load(image_path("bullet.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        """move the bullet up the screen by 4 pixels every loop"""
        self.rect.y -=4
        #has the bullet left the screen if so delete the bullet
        if self.rect.bottom < 0:
            self.kill()
        #Is it True that a bullet itself has hit an alien from the alien_group
        if pygame.sprite.spritecollide(self, alien_group, True):
            player.score += 10
            self.kill()
            explosion1_sound.play()
            explosion = Alien_explosion(self.rect.centerx, self.rect.centery)
            alien_explosion_group.add(explosion)


####Aliens Class####
#Alien variables
rows = 5
colums = 5
alien_cooldown = 1000 #1 second

class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Aliens, self).__init__()
        self.image = pygame.image.load(image_path("alien" + str(random.randint(1, 4)) + ".png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.move_counter = 0 #how far the alien is from where it started
        self.move_direction = 1

    def update(self):
        """moves the aliens left and right, up to 70 pixels either side of where they started"""
        #move in x direction by 1 pixel every update
        self.rect.x += self.move_direction
        self.move_counter += self.move_direction
        if abs(self.move_counter) >= 70:
            self.move_direction *= -1    #change direction

def create_aliens():
    """creates the rows of aliens"""
    for row in range(rows):
        for item in range(colums):
            #creates an instance for the Aliens class
            alien = Aliens(100 + item * 100, 150 + row * 70)
            alien_group.add(alien)


####Alien bullets Class####
class Alien_bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Alien_bullets, self).__init__()
        self.image = pygame.image.load(image_path("alien_bullet.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
    #move the bullet down by 3 pixels every loop
        self.rect.y +=3
        #has the bullet left the screen if so delete the bullet
        if self.rect.top > screen_height:
            self.kill()
        #Is it True that an alien bullet itself has hit the player
        if pygame.sprite.spritecollide(self, player_group, False):
            self.kill()
            player.hit()


####Mystery alien####
class Mystery_alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Mystery_alien, self).__init__()
        self.image = pygame.image.load(image_path("mysteryalien.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.move_counter = 0 #how far it has moved from where it started
        self.move_direction = 1

    def update(self):
        """moves the mystery alien left and right across the top of the screen"""
        #move in x direction by 1 pixel every update
        self.rect.x += self.move_direction
        self.move_counter += self.move_direction
        if self.move_counter >= 400 or self.move_counter <= 0:
            self.move_direction *= -1    #change direction
        if pygame.sprite.spritecollide(self, bullet_group, True):
            explosion1_sound.play()
            explosion = Alien_explosion(self.rect.centerx, self.rect.centery)
            alien_explosion_group.add(explosion)
            reward = random.randint(1,4)
            if reward == 1:
                player.lives +=1
            elif reward == 2:
                player.score += 100
            elif reward == 3:
                player.score += 150
            else:
                player.score += 200
            self.kill()


def create_mystery_alien():
    mystery_alien = Mystery_alien(100, 80)
    mystery_alien_group.add(mystery_alien)

####Alien_explosion class####
class Alien_explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Alien_explosion, self).__init__()
        self.image = pygame.image.load(image_path("explosion1.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.counter = 0

    def update(self):
        explosion_speed = 10
        self.counter += 1
        if self.counter >= explosion_speed:
            self.kill()


####Player_explosion class####
class Player_explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Player_explosion, self).__init__()
        self.image = pygame.image.load(image_path("explosion2.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.counter = 0

    def update(self):
        explosion_speed = 5
        self.counter += 1
        if self.counter >= explosion_speed:
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
    global screen, clock, background, font, font2
    global explosion1_sound, explosion2_sound, laser_sound, player

    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    #Create the screen object
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()

    background = pygame.image.load(image_path("background.png")).convert()

    #define the font type, size and text colours
    font = pygame.font.SysFont("arial", 32)
    font2 = pygame.font.SysFont("arial", 60)

    #load sounds:
    explosion1_sound = pygame.mixer.Sound(sound_path("explosion.wav"))
    explosion2_sound = pygame.mixer.Sound(sound_path("explosion2.wav"))
    laser_sound = pygame.mixer.Sound(sound_path("laser.wav"))

    #clear anything left over from the last game
    for group in all_groups:
        group.empty()

    #create an instance of the Player class
    player = Player(int(screen_width/2), screen_height - 70)
    player_group.add(player)


#Main loop:
def main(dclient = None):
    """plays one game and returns the score"""
    setup_game()

    #timer as soon as the game starts
    ticks = pygame.time.get_ticks()
    ticking = pygame.time.get_ticks()

    running = True
    while running:
        #sets the clock speed
        clock.tick(fps)

        #current time within the game
        time = pygame.time.get_ticks()

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
        if len(mystery_alien_group.sprites()) == 0 and time - ticking > 1050:
            create_mystery_alien()
            ticking = time

        #create the aliens when there are no aliens left
        if len(alien_group.sprites()) == 0:
            #no bonus for the very first wave
            if player.score > 0:
                player.score += 100
            create_aliens()

        #Alien shooting
        if player.lives > 0 and time - ticks > alien_cooldown: #after a certain amount of time the enemy shoots
            shooter = random.choice(alien_group.sprites())
            alien_bullet = Alien_bullets(shooter.rect.centerx, shooter.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            laser_sound.play()
            ticks = time

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
        draw_text(screen, "SCORE", font, green, 1, 1)
        draw_text(screen, str(player.score) , font, green, 130, 1)

        #draw lives
        draw_text(screen, "LIVES", font, green, 450, 1)
        draw_text(screen, str(player.lives), font, green, 560, 1)

        if player.lives <= 0:
            draw_text(screen, "GAME OVER", font2, red, screen_width/2 - 130 , screen_height/2 + 100)
            draw_text(screen, "SPACE TO GO BACK TO MAIN SCREEN", font, red, screen_width/2 - 250 , screen_height/2 + 170)

        # Update the display
        pygame.display.flip()

    score = player.score
    #close the game window and go back to the menu
    pygame.quit()
    return score

if __name__ == "__main__":
    print("Score:", main())