#Menu screen

import tkinter as tk

from . import game
from .accounts import ClientList


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
    leaderboard_window.geometry("275x225")

    names_box = tk.Text(leaderboard_window)
    scores_box = tk.Text(leaderboard_window)
    names_box.config(height=5, width=20)
    scores_box.config(height=5, width=10)
    names_box.grid(row=2, column=0, padx=5, pady=5)
    scores_box.grid(row=2, column=1, padx=5, pady=5)

    #populate a list of top 5 players and their scores
    names = ""
    scores = ""
    for player in clients.top_players(5):
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
    help_window.geometry("500x400")

    tk.Label(help_window, text="HOW TO PLAY", font=("Arial", 20), bg="light blue", width="300", height="2").pack()
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
    screen.geometry("500x400")

    tk.Label(text="MENU", font=("Arial", 20), bg="light blue", width="300", height="2").pack()
    tk.Label(text="").pack()
    tk.Label(text=f"Welcome {client.username}!").pack()
    tk.Label(text="").pack()
    tk.Label(text="").pack()
    #lambda so the game only starts when the button is pressed
    tk.Button(text="Play", bg="light blue", width="50", height="2", command=lambda: play_game(client)).pack()
    tk.Label(text="").pack()
    tk.Button(text="How to play", bg="light blue", width="50", height="2", command=how_to_play).pack()
    tk.Label(text="").pack()
    tk.Button(text="Leaderboard", bg="light blue", width="50", height="2", command=leaderboard).pack()

    screen.mainloop()
