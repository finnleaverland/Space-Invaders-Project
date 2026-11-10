"""Tests for the game logic, run frame by frame without opening a real window."""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"  # no window
os.environ["SDL_AUDIODRIVER"] = "dummy"  # no sound

import pygame  # noqa: E402
import pytest  # noqa: E402

from space_invaders import game as game_module  # noqa: E402
from space_invaders.game import GAME_OVER, PAUSED, PLAYING, READY, Game  # noqa: E402


class Keys(set):
    """Stands in for pygame.key.get_pressed(): Keys({pygame.K_LEFT}) means LEFT is held."""

    def __getitem__(self, key):
        return key in self


NO_KEYS = Keys()


@pytest.fixture
def game():
    test_game = Game(high_score=100)
    yield test_game
    pygame.quit()


def run_frames(game, frames, keys=NO_KEYS):
    for _ in range(frames):
        game.step(keys)


def start(game):
    game.handle_key(pygame.K_SPACE)
    game.step(NO_KEYS)


def kill_player(game):
    game.player.lives = 1
    game.player.hit()
    game.step(NO_KEYS)


# --- Start screen -------------------------------------------------------------------

def test_game_waits_on_the_start_screen(game):
    run_frames(game, 120)
    assert game.state == READY
    assert game.time == 0
    assert not game.alien_group


def test_space_starts_the_first_wave(game):
    start(game)
    assert game.state == PLAYING
    assert game.wave == 1
    assert len(game.alien_group) == game_module.ALIEN_ROWS * game_module.ALIEN_COLUMNS


# --- Pausing ------------------------------------------------------------------------

def test_p_pauses_and_nothing_moves(game):
    start(game)
    run_frames(game, 30)
    game.handle_key(pygame.K_p)
    assert game.state == PAUSED
    positions = sorted(tuple(alien.rect) for alien in game.alien_group)
    time = game.time
    run_frames(game, 300, Keys({pygame.K_LEFT, pygame.K_SPACE}))
    assert game.time == time
    assert sorted(tuple(alien.rect) for alien in game.alien_group) == positions
    assert not game.bullet_group


def test_p_again_carries_on(game):
    start(game)
    game.handle_key(pygame.K_p)
    game.handle_key(pygame.K_p)
    assert game.state == PLAYING
    time = game.time
    run_frames(game, 10)
    assert game.time > time


def test_aliens_do_not_fire_straight_after_a_long_pause(game):
    start(game)
    run_frames(game, 30)
    game.handle_key(pygame.K_p)
    run_frames(game, 600)
    game.handle_key(pygame.K_p)
    shots_before = len(game.alien_bullet_group)
    game.step(NO_KEYS)
    assert len(game.alien_bullet_group) == shots_before


def test_pause_does_nothing_on_the_start_screen(game):
    game.handle_key(pygame.K_p)
    assert game.state == READY


# --- Game over ----------------------------------------------------------------------

def test_losing_the_last_life_ends_the_game(game):
    start(game)
    kill_player(game)
    assert game.state == GAME_OVER


def test_space_is_ignored_until_the_explosion_has_played(game):
    start(game)
    kill_player(game)
    game.handle_key(pygame.K_SPACE)
    assert game.running
    run_frames(game, int(game_module.GAME_OVER_DELAY / game_module.FRAME_MS) + 1)
    game.handle_key(pygame.K_SPACE)
    assert not game.running


def test_new_high_score(game):
    start(game)
    game.player.score = 100
    assert not game.new_high_score  # equalling it isn't beating it
    game.player.score = 110
    assert game.new_high_score


def test_escape_leaves_from_any_state(game):
    game.handle_key(pygame.K_ESCAPE)
    assert not game.running


def test_main_returns_the_score(monkeypatch):
    def play(self):
        self.player.score = 340
        return self.player.score
    monkeypatch.setattr(Game, "run", play)
    assert game_module.main(high_score=50) == 340


# --- Drawing ------------------------------------------------------------------------

@pytest.mark.parametrize("state", [READY, PLAYING, PAUSED, GAME_OVER])
def test_every_state_draws(game, state):
    start(game)
    if state == GAME_OVER:
        kill_player(game)
        run_frames(game, 200)
    else:
        game.state = state
    game.draw()


def test_lives_above_five_are_shown_as_a_number(game):
    start(game)
    game.player.lives = 8
    game.draw()  # must not draw eight icons over the wave number


# --- Waves and the alien formation -----------------------------------------------------

def alien_positions(game):
    return sorted((alien.x, alien.rect.y) for alien in game.alien_group)


def test_the_aliens_move_together(game):
    start(game)
    before = alien_positions(game)
    game.move_formation()
    after = alien_positions(game)
    moves = {round(a[0] - b[0], 6) for a, b in zip(after, before)}
    assert moves == {game.alien_speed}
    assert [a[1] for a in after] == [b[1] for b in before]


def test_at_the_edge_the_formation_steps_down_and_turns_round(game):
    start(game)
    rightmost = max(alien.rect.right for alien in game.alien_group)
    for alien in game.alien_group:  # push the formation right up to the edge
        alien.move(game_module.SCREEN_WIDTH - game_module.FORMATION_EDGE - rightmost)
    before = alien_positions(game)
    game.move_formation()
    after = alien_positions(game)
    assert game.formation_direction == -1
    assert [a[1] - b[1] for a, b in zip(after, before)] == [game_module.ALIEN_STEP_DOWN] * len(before)
    assert [a[0] for a in after] == [b[0] for b in before]


def test_aliens_reaching_the_player_end_the_game(game):
    start(game)
    lowest = max(alien.rect.bottom for alien in game.alien_group)
    for alien in game.alien_group:
        alien.move(0, game.player.rect.top - lowest)
    game.step(NO_KEYS)
    assert game.player.lives == 0
    assert game.state == GAME_OVER


def test_clearing_a_wave_brings_a_faster_one(game):
    start(game)
    speed, cooldown = game.alien_speed, game.alien_shot_cooldown
    score = game.player.score
    game.alien_group.empty()
    game.step(NO_KEYS)
    assert game.wave == 2
    assert game.player.score == score + game_module.WAVE_BONUS
    assert game.alien_speed == pytest.approx(speed * 1.15)
    assert game.alien_shot_cooldown == pytest.approx(cooldown * 0.9)
    assert len(game.alien_group) == game_module.ALIEN_ROWS * game_module.ALIEN_COLUMNS


def test_wave_speed_ups_are_capped(game):
    game.wave = 100
    assert game.alien_speed == game_module.ALIEN_MAX_SPEED
    assert game.alien_shot_cooldown == game_module.ALIEN_MIN_SHOT_COOLDOWN


def test_new_waves_start_at_the_top(game):
    start(game)
    first_wave = alien_positions(game)
    run_frames(game, 400)  # long enough to step down a few times
    assert max(y for _, y in alien_positions(game)) > max(y for _, y in first_wave)
    game.alien_group.empty()
    game.step(NO_KEYS)
    assert min(y for _, y in alien_positions(game)) == min(y for _, y in first_wave)
