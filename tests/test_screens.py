"""Tests for the tkinter screens, driven through their real buttons and text boxes.

They need a display, so they are skipped automatically where tkinter can't open a window.
"""
import tkinter as tk
from tkinter import ttk

import pytest

from space_invaders import accounts, game, theme
from space_invaders import app as app_module
from space_invaders.accounts import Client, ClientList


@pytest.fixture(scope="session")
def root():
    """One hidden main window shared by every test (Tk is slow and flaky to recreate)."""
    try:
        window = theme.new_root("test", app_module.WINDOW_WIDTH, app_module.WINDOW_HEIGHT)
    except tk.TclError as error:
        pytest.skip(f"tkinter can't open a window here: {error}")
    window.withdraw()
    yield window
    window.destroy()


@pytest.fixture
def accounts_file(tmp_path, monkeypatch):
    path = tmp_path / "Clientfile.txt"
    monkeypatch.setattr(accounts, "CLIENT_FILE", str(path))
    monkeypatch.setattr(accounts, "HASH_ITERATIONS", 1_000)
    clients = ClientList()
    alice = Client.new("alice", "alice-pass", "First pet?", "Rex")
    alice.highest_score = 50
    clients.add_client(alice)
    clients.add_client(Client.new("carol", "carol-pass", "Home town?", "Leeds"))
    return path


@pytest.fixture
def app(root, accounts_file):
    application = app_module.App(root)
    yield application
    application.screen.destroy()


def widgets(parent, kind):
    """Every widget of a type inside parent, in creation order."""
    found = []
    for child in parent.winfo_children():
        if isinstance(child, kind):
            found.append(child)
        found.extend(widgets(child, kind))
    return found


def click(app, text):
    """Press the button with this text on the current screen."""
    for button in widgets(app.screen, ttk.Button):
        if button.cget("text") == text:
            button.invoke()
            app.root.update()
            return
    raise AssertionError(f"no {text!r} button on {type(app.screen).__name__}")


def type_into(entry, text):
    entry.delete(0, "end")
    entry.insert(0, text)


def message(app):
    return app.screen.message.cget("text")


def screen_name(app):
    return type(app.screen).__name__


# --- Navigation -------------------------------------------------------------------

def test_starts_on_welcome_screen(app):
    assert screen_name(app) == "WelcomeScreen"


@pytest.mark.parametrize("button, screen", [
    ("Log in", "LoginScreen"),
    ("Register", "RegisterScreen"),
    ("Reset password", "ResetPasswordScreen"),
])
def test_every_form_has_a_back_button(app, button, screen):
    click(app, button)
    assert screen_name(app) == screen
    click(app, "← Back")
    assert screen_name(app) == "WelcomeScreen"


def test_everything_happens_in_one_window(app):
    click(app, "Log in")
    click(app, "← Back")
    click(app, "Register")
    assert not [w for w in app.root.winfo_children() if isinstance(w, tk.Toplevel)]


# --- Logging in -------------------------------------------------------------------

def log_in(app, username="alice", password="alice-pass"):
    click(app, "Log in")
    type_into(app.screen.username_entry, username)
    type_into(app.screen.password_entry, password)
    click(app, "Log in")


def test_log_in(app):
    log_in(app)
    assert screen_name(app) == "MenuScreen"
    assert app.client.username == "alice"


def test_log_in_with_unknown_username(app):
    log_in(app, username="nobody")
    assert screen_name(app) == "LoginScreen"
    assert message(app) == "Incorrect username"


def test_log_in_with_wrong_password(app):
    log_in(app, password="wrong")
    assert message(app) == "Incorrect password"
    assert app.screen.password_entry.get() == ""


# --- Registering ------------------------------------------------------------------

def register(app, username="bob", password="bob-pass", question="Colour?", answer="blue"):
    click(app, "Register")
    type_into(app.screen.username_entry, username)
    type_into(app.screen.password_entry, password)
    type_into(app.screen.question_entry, question)
    type_into(app.screen.answer_entry, answer)
    click(app, "Create account")


def test_register_logs_the_new_player_in(app):
    register(app)
    assert screen_name(app) == "MenuScreen"
    assert ClientList().find(Client("bob"))[0]


def test_register_rejects_taken_username(app):
    register(app, username="alice")
    assert message(app) == "That username is already taken"


# --- Resetting a password -----------------------------------------------------------

def test_reset_password(app):
    click(app, "Reset password")
    type_into(app.screen.username_entry, "alice")
    click(app, "Next")
    assert app.screen.question_label.cget("text") == "First pet?"
    type_into(app.screen.answer_entry, "  REX ")
    type_into(app.screen.password_entry, "new-password")
    click(app, "Save new password")

    assert screen_name(app) == "LoginScreen"
    assert "Password changed" in message(app)
    type_into(app.screen.username_entry, "alice")
    type_into(app.screen.password_entry, "new-password")
    click(app, "Log in")
    assert screen_name(app) == "MenuScreen"


def test_reset_password_unknown_user_and_wrong_answer(app):
    click(app, "Reset password")
    type_into(app.screen.username_entry, "nobody")
    click(app, "Next")
    assert message(app) == "That username doesn't exist"
    type_into(app.screen.username_entry, "alice")
    click(app, "Next")
    type_into(app.screen.answer_entry, "Max")
    type_into(app.screen.password_entry, "new-password")
    click(app, "Save new password")
    assert message(app) == "Wrong answer, try again"


# --- The menu -----------------------------------------------------------------------

def test_play_saves_the_score(app, monkeypatch):
    monkeypatch.setattr(game, "main", lambda *args, **kwargs: 120)
    log_in(app)
    click(app, "Play")
    assert screen_name(app) == "MenuScreen"
    alice = ClientList().clients[0]
    assert (alice.score, alice.highest_score) == (120, 120)


def test_leaderboard_and_how_to_play_have_back_buttons(app):
    log_in(app)
    for button in ("Leaderboard", "How to play"):
        click(app, button)
        assert screen_name(app) != "MenuScreen"
        click(app, "← Back")
        assert screen_name(app) == "MenuScreen"


def test_delete_account(app):
    log_in(app)
    click(app, "Delete account")
    type_into(app.screen.password_entry, "wrong")
    click(app, "Delete my account")
    assert message(app) == "Wrong password"

    type_into(app.screen.password_entry, "alice-pass")
    click(app, "Delete my account")
    assert screen_name(app) == "WelcomeScreen"
    assert "deleted" in message(app)
    assert not ClientList().find(Client("alice"))[0]
