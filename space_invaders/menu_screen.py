"""Screens shown after logging in: the menu, leaderboard, how to play and delete account."""
from tkinter import ttk

from . import game, theme
from .accounts import ClientList
from .widgets import Screen

LEADERBOARD_SIZE = 5  # how many players the leaderboard shows

_POINT_REWARDS = [reward for reward in game.MYSTERY_REWARDS if reward != game.EXTRA_LIFE]
HOW_TO_PLAY = (
    "Move with the LEFT and RIGHT arrow keys and shoot with SPACE",
    "Do NOT get hit by the enemies' bullets",
    f"You have {game.PLAYER_LIVES} lives",
    "You have infinite bullets (it works best if you hold down SPACE)",
    "Aim: destroy all the enemies",
    f"{game.ALIEN_POINTS} points for every enemy destroyed",
    f"The SPECIAL enemy gives either an extra life or {min(_POINT_REWARDS)}-{max(_POINT_REWARDS)} points",
    "The game is endless: a new wave arrives when you clear one",
    "The most points wins. Press ESC to stop playing",
)


class MenuScreen(Screen):
    """The main menu for a logged-in player."""

    def build(self):
        client = self.app.client
        self.add_title("SPACE INVADERS")
        ttk.Label(self.body, text=f"Welcome, {client.username}!", style="Heading.TLabel").pack(
            pady=(0, theme.px(theme.GAP)))
        self.add_button("Play", self.app.play_game, primary=True)
        self.add_button("Leaderboard", lambda: self.app.show("leaderboard"))
        self.add_button("How to play", lambda: self.app.show("how_to_play"))
        self.add_button("Delete account", lambda: self.app.show("delete_account"))
        self.add_message_line()


class LeaderboardScreen(Screen):
    """The top players and their best scores."""

    def build(self):
        self.add_title("Leaderboard")
        table = ttk.Frame(self.body)
        table.pack(pady=theme.px(theme.GAP))
        gap = theme.px(6)
        for row, player in enumerate(ClientList().top_players(LEADERBOARD_SIZE)):
            ttk.Label(table, text=f"{row + 1}.", style="Muted.TLabel").grid(row=row, column=0, padx=gap)
            ttk.Label(table, text=player.username).grid(row=row, column=1, sticky="w", padx=gap)
            ttk.Label(table, text=str(player.highest_score)).grid(row=row, column=2, sticky="e", padx=gap)
        self.add_back_button(lambda: self.app.show("menu"))


class HowToPlayScreen(Screen):
    """The rules of the game."""

    def build(self):
        self.add_title("How to play")
        for line in HOW_TO_PLAY:
            ttk.Label(self.body, text="•  " + line, wraplength=theme.px(theme.TEXT_WIDTH)).pack(
                fill="x", pady=theme.px(3))
        self.add_back_button(lambda: self.app.show("menu"))


class DeleteAccountScreen(Screen):
    """Permanently delete the logged-in player's account (asks for their password)."""

    def build(self):
        self.add_title("Delete account")
        ttk.Label(self.body, text="This permanently deletes your account and your scores.",
                  style="Muted.TLabel", wraplength=theme.px(theme.TEXT_WIDTH),
                  justify="center").pack(pady=(0, theme.px(theme.GAP)))
        self.password_entry = self.add_field("Enter your password to confirm", hidden=True)
        self.add_password_toggle()
        self.add_button("Delete my account", self.submit, primary=True)
        self.add_message_line()
        self.add_back_button(lambda: self.app.show("menu"))
        self.submit_command = self.submit

    def submit(self):
        clients = ClientList()
        found, index = clients.find(self.app.client)
        if not found or not clients.clients[index].check_password(self.password_entry.get()):
            self.password_entry.delete(0, "end")
            self.show_error("Wrong password")
            return
        clients.delete_client(clients.clients[index])
        self.app.log_out(message="Your account has been deleted.")
