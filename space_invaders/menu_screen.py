#Menu screen

import tkinter as tk

from . import game
from .accounts import ClientList

LEADERBOARD_SIZE = 5  #how many players the leaderboard shows

#Window sizes
MENU_WINDOW_SIZE = "500x400"
HELP_WINDOW_SIZE = "500x400"
LEADERBOARD_WINDOW_SIZE = "275x225"

#Colours, fonts and widget sizes
THEME_COLOUR = "light blue"
TITLE_FONT = ("Arial", 20)
HEADER_WIDTH = 300
HEADER_HEIGHT = 2
MENU_BUTTON_WIDTH = 50
MENU_BUTTON_HEIGHT = 2
NAME_COLUMN_WIDTH = 20
SCORE_COLUMN_WIDTH = 10
LEADERBOARD_PADDING = 5


def play_game(client):
    """plays a game then saves the score for the logged in player"""
    screen.withdraw()  #hide the menu while the game is running
    try:
        new_score = game.main()
    finally:
        screen.deiconify()  #show the menu again
    players = ClientList()
    found, index = players.find(client)
    if found:
        current_client = players.clients[index]
        current_client.score = new_score
        players.update_player_in_list(current_client)


def leaderboard():
    clients = ClientList()
    leaderboard_window = tk.Toplevel(screen)
    leaderboard_window.title("Leaderboard")
    leaderboard_window.geometry(LEADERBOARD_WINDOW_SIZE)

    names_box = tk.Text(leaderboard_window)
    scores_box = tk.Text(leaderboard_window)
    names_box.config(height=LEADERBOARD_SIZE, width=NAME_COLUMN_WIDTH)
    scores_box.config(height=LEADERBOARD_SIZE, width=SCORE_COLUMN_WIDTH)
    names_box.grid(row=2, column=0, padx=LEADERBOARD_PADDING, pady=LEADERBOARD_PADDING)
    scores_box.grid(row=2, column=1, padx=LEADERBOARD_PADDING, pady=LEADERBOARD_PADDING)

    #populate a list of top 5 players and their scores
    names = ""
    scores = ""
    for player in clients.top_players(LEADERBOARD_SIZE):
        names += f"{player.username}\n"
        scores += f"{player.highest_score}\n"
    names_box.insert(tk.END, names)
    scores_box.insert(tk.END, scores)
    #make the boxes read only
    names_box.config(state=tk.DISABLED)
    scores_box.config(state=tk.DISABLED)


def how_to_play():
    help_window = tk.Toplevel(screen)
    help_window.title("HOW TO PLAY")
    help_window.geometry(HELP_WINDOW_SIZE)

    tk.Label(help_window, text="HOW TO PLAY", font=TITLE_FONT, bg=THEME_COLOUR, width=HEADER_WIDTH, height=HEADER_HEIGHT).pack()
    tk.Label(help_window, text="").pack()
    tk.Label(help_window, text="").pack()
    tk.Label(help_window, text="1) Do NOT get hit by the enemies' bullets").pack()
    tk.Label(help_window, text="2) YOU have 5 lives").pack()
    tk.Label(help_window, text="3) YOU have infinite bullets (It works better holding down the spacebar)").pack()
    tk.Label(help_window, text="4) AIM: KILL all the enemies").pack()
    tk.Label(help_window, text="5) 10 points for every enemy killed").pack()
    tk.Label(help_window, text="6) The SPECIAL enemy rewards either an extra life or 100-200 points").pack()
    tk.Label(help_window, text="7) The game is INFINITE").pack()
    tk.Label(help_window, text="8) MOST points win").pack()


def main(client):
    global screen
    screen = tk.Tk()
    screen.title("Menu")
    screen.geometry(MENU_WINDOW_SIZE)

    tk.Label(text="MENU", font=TITLE_FONT, bg=THEME_COLOUR, width=HEADER_WIDTH, height=HEADER_HEIGHT).pack()
    tk.Label(text="").pack()
    tk.Label(text=f"Welcome {client.username}!").pack()
    tk.Label(text="").pack()
    tk.Label(text="").pack()
    #lambda so the game only starts when the button is pressed
    tk.Button(text="Play", bg=THEME_COLOUR, width=MENU_BUTTON_WIDTH, height=MENU_BUTTON_HEIGHT, command=lambda: play_game(client)).pack()
    tk.Label(text="").pack()
    tk.Button(text="How to play", bg=THEME_COLOUR, width=MENU_BUTTON_WIDTH, height=MENU_BUTTON_HEIGHT, command=how_to_play).pack()
    tk.Label(text="").pack()
    tk.Button(text="Leaderboard", bg=THEME_COLOUR, width=MENU_BUTTON_WIDTH, height=MENU_BUTTON_HEIGHT, command=leaderboard).pack()

    screen.mainloop()
