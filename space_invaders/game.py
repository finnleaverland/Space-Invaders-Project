"""The Space Invaders game itself, written with pygame.

Call main() to play one game in its own window. It returns the final score.
"""
import os
import random

import pygame
from pygame.locals import K_ESCAPE, K_LEFT, K_RIGHT, K_SPACE, KEYDOWN, QUIT

# Asset folders, so the images and sounds load whatever folder you run from
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(PROJECT_ROOT, "assets", "images")
SOUND_DIR = os.path.join(PROJECT_ROOT, "assets", "sounds")

# Window
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60
WINDOW_TITLE = "Space Invaders"

# Colours and fonts
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FONT_NAME = "arial"
FONT_SIZE = 32
BIG_FONT_SIZE = 60

# Text positions
SCORE_LABEL_POS = (1, 1)
SCORE_VALUE_POS = (130, 1)
LIVES_LABEL_POS = (450, 1)
LIVES_VALUE_POS = (560, 1)
GAME_OVER_POS = (SCREEN_WIDTH / 2 - 130, SCREEN_HEIGHT / 2 + 100)
RETURN_HINT_POS = (SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 + 170)

# Player
PLAYER_START_POS = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70)
PLAYER_SPEED = 4  # pixels per frame
PLAYER_LIVES = 5
PLAYER_SHOT_COOLDOWN = 30  # frames between shots
PLAYER_BULLET_X_OFFSET = 10  # bullets leave the ship slightly right of centre
FRAME_COUNTER_LIMIT = 1_000_000  # the shot counter wraps back to 0 after this
BULLET_SPEED = 4  # pixels per frame, upwards

# Aliens
ALIEN_IMAGES = ("alien1.png", "alien2.png", "alien3.png", "alien4.png")
ALIEN_ROWS = 5
ALIEN_COLUMNS = 5
ALIEN_GRID_LEFT = 100
ALIEN_GRID_TOP = 150
ALIEN_SPACING_X = 100
ALIEN_SPACING_Y = 70
ALIEN_MOVE_RANGE = 70  # pixels either side of where each alien starts
ALIEN_SHOT_COOLDOWN = 1000  # milliseconds between alien shots
ALIEN_BULLET_SPEED = 3  # pixels per frame, downwards
ALIEN_POINTS = 10
WAVE_BONUS = 100  # points for clearing a wave (not given for the first wave)

# Mystery alien
MYSTERY_START_POS = (100, 80)
MYSTERY_MOVE_RANGE = 400  # pixels it travels before turning round
MYSTERY_SPAWN_DELAY = 1050  # milliseconds after the last one before a new one appears
EXTRA_LIFE = "extra life"
MYSTERY_REWARDS = (EXTRA_LIFE, 100, 150, 200)  # one is picked at random

# Explosions: which image to show and for how many frames
ALIEN_EXPLOSION = ("explosion1.png", 10)
PLAYER_EXPLOSION = ("explosion2.png", 5)

SPRITE_IMAGES = ALIEN_IMAGES + (
    "spaceship.png", "bullet.png", "alien_bullet.png", "mysteryalien.png",
    ALIEN_EXPLOSION[0], PLAYER_EXPLOSION[0],
)


def image_path(filename):
    """Return the full path to an image in assets/images."""
    return os.path.join(IMAGE_DIR, filename)


def sound_path(filename):
    """Return the full path to a sound in assets/sounds."""
    return os.path.join(SOUND_DIR, filename)


class Player(pygame.sprite.Sprite):
    """The player's ship. It moves left and right, shoots, and keeps the score and lives."""

    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = game.images["spaceship.png"]
        self.rect = self.image.get_rect(center=(x, y))
        self.frame_count = 0
        self.score = 0
        self.lives = PLAYER_LIVES

    def update(self, pressed_keys):
        """Move and shoot based on the keys being held down."""
        if self.lives <= 0:
            return  # a dead player can't move or shoot

        self.frame_count += 1
        if self.frame_count > FRAME_COUNTER_LIMIT:
            self.frame_count = 0
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-PLAYER_SPEED, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(PLAYER_SPEED, 0)

        if pressed_keys[K_SPACE] and self.frame_count % PLAYER_SHOT_COOLDOWN == 0:
            self.game.laser_sound.play()
            bullet = Bullet(self.game, self.rect.centerx + PLAYER_BULLET_X_OFFSET, self.rect.top)
            self.game.bullet_group.add(bullet)

        # Keep the player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def hit(self):
        """Lose a life after being hit by an alien bullet, and explode on the last one."""
        if self.lives <= 0:
            return
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.game.player_death_sound.play()
            explosion = Explosion(self.game, self.rect.center, *PLAYER_EXPLOSION)
            self.game.player_explosion_group.add(explosion)
            self.kill()


class Bullet(pygame.sprite.Sprite):
    """A bullet fired upwards by the player."""

    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = game.images["bullet.png"]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        """Move up, disappear off the top of the screen, and destroy any alien it hits."""
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, self.game.alien_group, True):
            self.game.player.score += ALIEN_POINTS
            self.kill()
            self.game.explosion_sound.play()
            explosion = Explosion(self.game, self.rect.center, *ALIEN_EXPLOSION)
            self.game.alien_explosion_group.add(explosion)


class Alien(pygame.sprite.Sprite):
    """An ordinary alien. It sways left and right around where it started."""

    def __init__(self, game, x, y):
        super().__init__()
        self.image = game.images[random.choice(ALIEN_IMAGES)]
        self.rect = self.image.get_rect(center=(x, y))
        self.move_counter = 0  # how far the alien is from where it started
        self.move_direction = 1

    def update(self):
        """Move 1 pixel, turning round ALIEN_MOVE_RANGE pixels either side of the start."""
        self.rect.x += self.move_direction
        self.move_counter += self.move_direction
        if abs(self.move_counter) >= ALIEN_MOVE_RANGE:
            self.move_direction *= -1


class AlienBullet(pygame.sprite.Sprite):
    """A bullet fired downwards by an alien."""

    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = game.images["alien_bullet.png"]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        """Move down, disappear off the bottom of the screen, and hurt the player on contact."""
        self.rect.y += ALIEN_BULLET_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
        if pygame.sprite.spritecollide(self, self.game.player_group, False):
            self.kill()
            self.game.player.hit()


class MysteryAlien(pygame.sprite.Sprite):
    """The special alien that crosses the top of the screen and gives a random reward."""

    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = game.images["mysteryalien.png"]
        self.rect = self.image.get_rect(center=(x, y))
        self.move_counter = 0  # how far it has moved from where it started
        self.move_direction = 1

    def update(self):
        """Move 1 pixel, and if a bullet hits it, give the player a random reward."""
        self.rect.x += self.move_direction
        self.move_counter += self.move_direction
        if self.move_counter >= MYSTERY_MOVE_RANGE or self.move_counter <= 0:
            self.move_direction *= -1
        if pygame.sprite.spritecollide(self, self.game.bullet_group, True):
            self.game.explosion_sound.play()
            explosion = Explosion(self.game, self.rect.center, *ALIEN_EXPLOSION)
            self.game.alien_explosion_group.add(explosion)
            reward = random.choice(MYSTERY_REWARDS)
            if reward == EXTRA_LIFE:
                self.game.player.lives += 1
            else:
                self.game.player.score += reward
            self.kill()


class Explosion(pygame.sprite.Sprite):
    """An explosion image that stays on screen for a set number of frames."""

    def __init__(self, game, center, image_name, frames):
        super().__init__()
        self.image = game.images[image_name]
        self.rect = self.image.get_rect(center=center)
        self.frames_left = frames

    def update(self):
        """Count down and remove the explosion when its time is up."""
        self.frames_left -= 1
        if self.frames_left <= 0:
            self.kill()


class Game:
    """One game of Space Invaders: the window, the loaded assets, every sprite and the timers."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        # Load every image and sound once, rather than each time a sprite is made
        self.background = pygame.image.load(image_path("background.png")).convert()
        self.images = {name: pygame.image.load(image_path(name)).convert_alpha()
                       for name in SPRITE_IMAGES}
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.big_font = pygame.font.SysFont(FONT_NAME, BIG_FONT_SIZE)
        self.explosion_sound = pygame.mixer.Sound(sound_path("explosion.wav"))
        self.player_death_sound = pygame.mixer.Sound(sound_path("explosion2.wav"))
        self.laser_sound = pygame.mixer.Sound(sound_path("laser.wav"))

        self.player_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.alien_group = pygame.sprite.Group()
        self.alien_bullet_group = pygame.sprite.Group()
        self.mystery_alien_group = pygame.sprite.Group()
        self.alien_explosion_group = pygame.sprite.Group()
        self.player_explosion_group = pygame.sprite.Group()

        self.player = Player(self, *PLAYER_START_POS)
        self.player_group.add(self.player)

        self.last_alien_shot = 0
        self.last_mystery_spawn = 0

    def run(self):
        """Run the game loop and return the final score.

        The game ends when the window is closed, ESC is pressed, or SPACE is pressed
        after game over.
        """
        self.last_alien_shot = pygame.time.get_ticks()
        self.last_mystery_spawn = pygame.time.get_ticks()

        running = True
        while running:
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            # The rest of the frame still runs after quitting, so the last frame is drawn
            running = self.handle_events()
            pressed_keys = pygame.key.get_pressed()
            self.spawn_enemies(now)
            self.update(pressed_keys)
            self.draw()
            pygame.display.flip()

        return self.player.score

    def handle_events(self):
        """Process window and key events. Returns False when the game should end."""
        running = True
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE and self.player.lives <= 0:
                    running = False  # once the game is over, SPACE goes back to the menu
        return running

    def spawn_enemies(self, now):
        """Bring in the mystery alien and new waves, and let a random alien shoot."""
        if not self.mystery_alien_group and now - self.last_mystery_spawn > MYSTERY_SPAWN_DELAY:
            self.mystery_alien_group.add(MysteryAlien(self, *MYSTERY_START_POS))
            self.last_mystery_spawn = now

        if not self.alien_group:
            if self.player.score > 0:  # no bonus for the very first wave
                self.player.score += WAVE_BONUS
            self.create_aliens()

        if self.player.lives > 0 and now - self.last_alien_shot > ALIEN_SHOT_COOLDOWN:
            shooter = random.choice(self.alien_group.sprites())
            self.alien_bullet_group.add(AlienBullet(self, shooter.rect.centerx, shooter.rect.bottom))
            self.laser_sound.play()
            self.last_alien_shot = now

    def create_aliens(self):
        """Fill the grid with a new wave of aliens."""
        for row in range(ALIEN_ROWS):
            for column in range(ALIEN_COLUMNS):
                x = ALIEN_GRID_LEFT + column * ALIEN_SPACING_X
                y = ALIEN_GRID_TOP + row * ALIEN_SPACING_Y
                self.alien_group.add(Alien(self, x, y))

    def update(self, pressed_keys):
        """Move every sprite one frame."""
        self.player.update(pressed_keys)
        self.bullet_group.update()
        self.alien_group.update()
        self.alien_bullet_group.update()
        self.alien_explosion_group.update()
        self.player_explosion_group.update()
        self.mystery_alien_group.update()

    def draw(self):
        """Draw the background, every sprite, the score and lives, and the game over text."""
        self.screen.blit(self.background, (0, 0))
        for group in (self.player_group, self.bullet_group, self.alien_group,
                      self.alien_bullet_group, self.alien_explosion_group,
                      self.player_explosion_group, self.mystery_alien_group):
            group.draw(self.screen)

        self.draw_text("SCORE", self.font, GREEN, SCORE_LABEL_POS)
        self.draw_text(str(self.player.score), self.font, GREEN, SCORE_VALUE_POS)
        self.draw_text("LIVES", self.font, GREEN, LIVES_LABEL_POS)
        self.draw_text(str(self.player.lives), self.font, GREEN, LIVES_VALUE_POS)

        if self.player.lives <= 0:
            self.draw_text("GAME OVER", self.big_font, RED, GAME_OVER_POS)
            self.draw_text("SPACE TO GO BACK TO MAIN SCREEN", self.font, RED, RETURN_HINT_POS)

    def draw_text(self, text, font, colour, position):
        """Draw text onto the game window."""
        self.screen.blit(font.render(text, True, colour), position)


def main():
    """Play one game in a new window, close the window, and return the final score."""
    try:
        return Game().run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    print("Score:", main())
