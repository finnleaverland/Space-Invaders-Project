"""Tests for the tkinter screens, driven through their real buttons and text boxes.

They need a display, so they are skipped automatically where tkinter can't open a window.
"""
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace

import pytest

from space_invaders import accounts, game, theme
from space_invaders import app as app_module
from space_invaders.accounts import Client, ClientList


@pytest.fixture(scope="session")
def root():
    """One main window shared by every test (Tk is slow and flaky to recreate).

    It stays mapped, so keyboard focus and Tab order work as they do for a player,
    but it is fully transparent and off-screen so nothing flashes up.
    """
    try:
        window = theme.new_root("test", app_module.WINDOW_WIDTH, app_module.WINDOW_HEIGHT)
    except tk.TclError as error:
        pytest.skip(f"tkinter can't open a window here: {error}")
    window.attributes("-alpha", 0.0)
    window.geometry("+-4000+-4000")
    window.update()
    # Tk loads its keyboard-traversal commands from library files the first time they're
    # used. On some Windows machines that read occasionally fails, so load them up front.
    for _attempt in range(3):
        try:
            window.tk.call("auto_load", "tk_focusNext")
            break
        except tk.TclError:
            pass
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


# --- Keyboard and usability ----------------------------------------------------------

def press(app, widget, key, char=""):
    """Send a key press on a widget to the same handlers the window's key bindings call.

    Real key events only arrive while the window has keyboard focus, which Windows won't
    give a background test window, so the bindings themselves are checked separately.
    """
    event = SimpleNamespace(widget=widget, keysym=key, char=char)
    if key == "Return":
        app.screen.handle_return(event)
    elif key == "Escape":
        app.screen.handle_escape(event)
    else:
        app.screen.on_typing(event)
    app.root.update()


def test_keys_are_bound_to_the_screen_handlers(app):
    bound = app.root.bind()
    assert {"<Key-Return>", "<Key-KP_Enter>", "<Key-Escape>"} <= set(bound)
    click(app, "Register")
    for entry in app.screen.fields:
        assert "<Key>" in entry.bind()


def test_cursor_starts_in_the_first_box(app):
    click(app, "Log in")
    assert app.root.focus_lastfor() == app.screen.username_entry


def test_tab_goes_from_box_to_box_then_to_the_button(app):
    click(app, "Log in")
    screen = app.screen
    assert screen.username_entry.tk_focusNext() == screen.password_entry
    next_widget = screen.password_entry.tk_focusNext()
    assert isinstance(next_widget, ttk.Button) and next_widget.cget("text") == "Log in"


def test_return_submits_the_form(app):
    click(app, "Log in")
    type_into(app.screen.username_entry, "alice")
    type_into(app.screen.password_entry, "alice-pass")
    press(app, app.screen.password_entry, "Return")
    assert screen_name(app) == "MenuScreen"


def test_return_presses_the_focused_button(app):
    register_button = [b for b in app.screen.buttons if b.cget("text") == "Register"][0]
    press(app, register_button, "Return")
    assert screen_name(app) == "RegisterScreen"


def test_escape_goes_back(app):
    click(app, "Register")
    press(app, app.screen.username_entry, "Escape")
    assert screen_name(app) == "WelcomeScreen"


def test_escape_does_not_quit_from_the_welcome_screen(app):
    press(app, app.screen.buttons[0], "Escape")
    assert screen_name(app) == "WelcomeScreen"


def test_show_password_toggle(app):
    click(app, "Log in")
    toggle = widgets(app.screen, ttk.Checkbutton)[0]
    assert app.screen.password_entry.cget("show") != ""
    toggle.invoke()
    assert app.screen.password_entry.cget("show") == ""
    toggle.invoke()
    assert app.screen.password_entry.cget("show") != ""


def test_error_clears_when_the_player_edits_a_box(app):
    log_in(app, password="wrong")
    assert message(app) == "Incorrect password"
    press(app, app.screen.username_entry, "Tab")  # moving between boxes keeps the message
    assert message(app) == "Incorrect password"
    press(app, app.screen.username_entry, "BackSpace")
    assert message(app) == ""


def test_typing_a_letter_clears_the_error(app):
    log_in(app, username="nobody")
    assert message(app) == "Incorrect username"
    press(app, app.screen.username_entry, "a", char="a")
    assert message(app) == ""


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
