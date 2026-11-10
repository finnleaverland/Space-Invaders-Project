#Menu screen

from tkinter import *

import prototype3
import Loginsystem as LS


def play_game(dclient):
    """plays a game then saves the score for the logged in player"""
    screen.withdraw() #hide the menu while the game is running
    try:
        newscore = prototype3.main(dclient)
    finally:
        screen.deiconify() #show the menu again
    players = LS.client_list()
    found, index = players.find(dclient)
    if found:
        currentclient = players.get_client(index)
        currentclient.set_score(newscore)
        players.update_player_in_list(currentclient)


def leaderboard():
    theClients = LS.client_list()
    screen3 = Toplevel(screen)
    screen3.title('Leaderboard')
    screen3.geometry("275x225")

    listbox1 = Text(screen3)
    listbox2 = Text(screen3)
    listbox1.config(height = 5, width = 20)
    listbox2.config(height = 5, width = 10)
    listbox1.grid(row = 2, column=0, padx = 5, pady = 5)
    listbox2.grid(row = 2, column=1, padx = 5, pady = 5)

    #populate a list of top 5 players and their scores
    listofplayers = ""
    listofscores = ""
    for player in theClients.top_players(5):
        listofplayers += f"{player.get_username()}\n"
        listofscores += f"{player.get_highest_score()}\n"
    listbox1.insert(END, listofplayers)
    listbox2.insert(END, listofscores)
    #make the boxes read only
    listbox1.config(state = DISABLED)
    listbox2.config(state = DISABLED)


def how_to_play():
    screen2 = Toplevel(screen)
    screen2.title('HOW TO PLAY')
    screen2.geometry("500x400")

    Label(screen2, text = "HOW TO PLAY", font= ("Arial", 20), bg = "light blue", width = "300", height = "2").pack()
    Label(screen2, text = "").pack()
    Label(screen2, text = "").pack()
    Label(screen2, text = "1) Do NOT get hit by the enemies' bullets").pack()
    Label(screen2, text = "2) YOU have 5 lives").pack()
    Label(screen2, text = "3) YOU have infinite bullets (It works better holding down the spacebar)").pack()
    Label(screen2, text = "4) AIM: KILL all the enemies").pack()
    Label(screen2, text = "5) 10 points for every enemy killed").pack()
    Label(screen2, text = "6) The SPECIAL enemy rewards either an extra life or 100-200 points").pack()
    Label(screen2, text = "7) The game is INFINITE").pack()
    Label(screen2, text = "8) MOST points win").pack()


def menu_screen(dclient):
    global screen
    screen = Tk()
    screen.title('Menu')
    screen.geometry("500x400")

    Label(text = "MENU", font= ("Arial", 20), bg = "light blue", width = "300", height = "2").pack()
    Label(text = "").pack()
    Label(text = f"Welcome {dclient.get_username()}!").pack()
    Label(text = "").pack()
    Label(text = "").pack()
    #lambda so the game only starts when the button is pressed
    Button(text = "Play", bg = "light blue", width = "50", height = "2", command = lambda: play_game(dclient)).pack()
    Label(text = "").pack()
    Button(text = "How to play", bg = "light blue", width = "50", height = "2", command = how_to_play).pack()
    Label(text = "").pack()
    Button(text = "Leaderboard", bg = "light blue", width = "50", height = "2", command = leaderboard).pack()

    screen.mainloop()

if __name__ == "__main__":
    #the menu needs a logged in player, so start from the login screen
    import Login1
    Login1.main_screen()