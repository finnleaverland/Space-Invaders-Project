"""Draw the explosion sprites (assets/images/explosion1.png and explosion2.png).

The explosions are generated rather than downloaded, so they are original artwork
covered by this project's licence. Run from the project folder:

    python tools/make_explosions.py
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images")

SUPERSAMPLE = 4  # draw larger, then scale down for smooth edges
OUTER = (235, 90, 30)
MIDDLE = (255, 170, 40)
INNER = (255, 235, 120)
CORE = (255, 255, 235)

# (file name, size in pixels, random seed)
EXPLOSIONS = [
    ("explosion1.png", 40, 1),  # alien explosion
    ("explosion2.png", 80, 2),  # player explosion
]


def starburst(rng, centre, radius, points, spikiness):
    """Corners of a jagged star shape around a centre point."""
    corners = []
    for i in range(points * 2):
        angle = math.pi * i / points + rng.uniform(-0.12, 0.12)
        reach = radius if i % 2 == 0 else radius * (1 - spikiness)
        reach *= rng.uniform(0.85, 1.0)
        corners.append((centre + reach * math.cos(angle), centre + reach * math.sin(angle)))
    return corners


def draw_explosion(size, seed):
    """Return a transparent surface with an explosion drawn on it."""
    rng = random.Random(seed)
    big = size * SUPERSAMPLE
    centre = big / 2
    radius = big / 2 - SUPERSAMPLE
    surface = pygame.Surface((big, big), pygame.SRCALPHA)

    for _ in range(6):  # flying sparks around the edge
        angle = rng.uniform(0, 2 * math.pi)
        distance = radius * rng.uniform(0.75, 0.92)
        spark = (centre + distance * math.cos(angle), centre + distance * math.sin(angle))
        pygame.draw.circle(surface, MIDDLE, spark, radius * rng.uniform(0.05, 0.09))

    pygame.draw.polygon(surface, OUTER, starburst(rng, centre, radius * 0.85, 9, 0.45))
    pygame.draw.polygon(surface, MIDDLE, starburst(rng, centre, radius * 0.62, 8, 0.35))
    pygame.draw.polygon(surface, INNER, starburst(rng, centre, radius * 0.4, 7, 0.25))
    pygame.draw.circle(surface, CORE, (centre, centre), radius * 0.18)
    return pygame.transform.smoothscale(surface, (size, size))


def main():
    pygame.init()
    for file_name, size, seed in EXPLOSIONS:
        path = os.path.join(IMAGE_DIR, file_name)
        pygame.image.save(draw_explosion(size, seed), path)
        print(f"saved {path} ({size}x{size})")


if __name__ == "__main__":
    main()
