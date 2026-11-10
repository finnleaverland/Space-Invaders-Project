"""The main menu (tkinter): play the game, read how to play, or see the leaderboard."""
import tkinter as tk

from . import game
from .accounts import ClientList

LEADERBOARD_SIZE = 5  # how many players the leaderboard shows

# Window sizes
MENU_WINDOW_SIZE = "500x400"
HELP_WINDOW_SIZE = "500x400"
LEADERBOARD_WINDOW_SIZE = "275x225"

# Colours, fonts and widget sizes
THEME_COLOUR = "light blue"
TITLE_FONT = ("Arial", 20)
HEADER_WIDTH = 300
HEADER_HEIGHT = 2
MENU_BUTTON_WIDTH = 50
MENU_BUTTON_HEIGHT = 2
NAME_COLUMN_WIDTH = 20
SCORE_COLUMN_WIDTH = 10
LEADERBOARD_PADDING = 5

HOW_TO_PLAY = (
    "1) Do NOT get hit by the enemies' bullets",
    "2) YOU have 5 lives",
    "3) YOU have infinite bullets (It works better holding down the spacebar)",
    "4) AIM: KILL all the enemies",
    "5) 10 points for every enemy killed",
    "6) The SPECIAL enemy rewards either an extra life or 100-200 points",
    "7) The game is INFINITE",
    "8) MOST points win",
)


def add_spacer(window):
    """Add an empty line to a window."""
    tk.Label(window, text="").pack()


def add_header(window, text):
    """Add the big title bar used at the top of the menu windows."""
    tk.Label(window, text=text, font=TITLE_FONT, bg=THEME_COLOUR,
             width=HEADER_WIDTH, height=HEADER_HEIGHT).pack()


class MenuScreen:
    """The menu shown to a player after they log in."""

    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("Menu")
        self.root.geometry(MENU_WINDOW_SIZE)

        add_header(self.root, "MENU")
        add_spacer(self.root)
        tk.Label(self.root, text=f"Welcome {client.username}!").pack()
        add_spacer(self.root)
        add_spacer(self.root)
        self.add_button("Play", self.play_game)
        add_spacer(self.root)
        self.add_button("How to play", self.show_how_to_play)
        add_spacer(self.root)
        self.add_button("Leaderboard", self.show_leaderboard)

    def add_button(self, text, command):
        """Add one of the large menu buttons."""
        tk.Button(self.root, text=text, bg=THEME_COLOUR, width=MENU_BUTTON_WIDTH,
                  height=MENU_BUTTON_HEIGHT, command=command).pack()

    def run(self):
        """Show the menu and wait for the player."""
        self.root.mainloop()

    def play_game(self):
        """Hide the menu, play one game, then save the score for the logged-in player."""
        self.root.withdraw()
        try:
            new_score = game.main()
        finally:
            self.root.deiconify()

        players = ClientList()
        found, index = players.find(self.client)
        if found:
            current_client = players.clients[index]
            current_client.score = new_score
            players.update_player_in_list(current_client)

    def show_leaderboard(self):
        """Open a window listing the top players and their best scores."""
        window = tk.Toplevel(self.root)
        window.title("Leaderboard")
        window.geometry(LEADERBOARD_WINDOW_SIZE)

        names_box = tk.Text(window, height=LEADERBOARD_SIZE, width=NAME_COLUMN_WIDTH)
        scores_box = tk.Text(window, height=LEADERBOARD_SIZE, width=SCORE_COLUMN_WIDTH)
        names_box.grid(row=2, column=0, padx=LEADERBOARD_PADDING, pady=LEADERBOARD_PADDING)
        scores_box.grid(row=2, column=1, padx=LEADERBOARD_PADDING, pady=LEADERBOARD_PADDING)

        top_players = ClientList().top_players(LEADERBOARD_SIZE)
        names_box.insert(tk.END, "".join(f"{player.username}\n" for player in top_players))
        scores_box.insert(tk.END, "".join(f"{player.highest_score}\n" for player in top_players))
        names_box.config(state=tk.DISABLED)  # read only
        scores_box.config(state=tk.DISABLED)

    def show_how_to_play(self):
        """Open a window with the rules of the game."""
        window = tk.Toplevel(self.root)
        window.title("HOW TO PLAY")
        window.geometry(HELP_WINDOW_SIZE)

        add_header(window, "HOW TO PLAY")
        add_spacer(window)
        add_spacer(window)
        for line in HOW_TO_PLAY:
            tk.Label(window, text=line).pack()


def main(client):
    """Open the menu for a logged-in player."""
    MenuScreen(client).run()
