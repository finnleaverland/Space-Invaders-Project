#Client system login

import csv
import os

#Store the client file in the project folder so it works whatever folder you run from
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_FILE = os.path.join(PROJECT_ROOT, "Clientfile.txt")


def to_int(value):
    """turns a score read from the file into an int (blank or bad values become 0)"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


class Client:
    """initialises the client class"""

    def __init__(self, username="", password="", question="", answer="", score=0, highest_score=0):
        self.username = username
        self.password = password
        self.question = question
        self.answer = answer
        self.score = to_int(score)
        self.highest_score = to_int(highest_score)

    #comparison operators (clients are compared by username)
    def __eq__(self, other):
        return self.username == other.username

    def __lt__(self, other):
        """less than"""
        return self.username < other.username

    def __gt__(self, other):
        """greater than"""
        return self.username > other.username

    def to_row(self):
        """the client as a list of fields, ready to be written to the file"""
        return [self.username, self.password, self.question, self.answer,
                str(self.score), str(self.highest_score)]

    def __str__(self):
        """How the class is presented / printed as"""
        return ", ".join(self.to_row())


class ClientList:
    """read clients from a file / validation
    The list is always kept sorted by username so the binary search works."""

    def __init__(self, path=None):
        self.path = path or CLIENT_FILE
        self.clients = []
        if not os.path.exists(self.path):
            #first run: create an empty client file
            open(self.path, "w").close()
        with open(self.path, "r", newline="") as f:
            #skipinitialspace lets this read the old "a, b, c" format too
            for fields in csv.reader(f, skipinitialspace=True):
                if len(fields) < 4:
                    continue  #skip blank or broken lines
                while len(fields) < 6:
                    fields.append("0")  #missing scores count as 0
                self.clients.append(Client(*fields[:6]))
        self.sort_list()

    def __len__(self):
        """returns the number of clients in the client list"""
        return len(self.clients)

    def sort_list(self):
        """insertion sort to sort based on username"""
        for i in range(1, len(self.clients)):
            current_item = self.clients[i]
            index = i
            while index > 0 and current_item < self.clients[index - 1]:
                self.clients[index] = self.clients[index - 1]
                index -= 1
            self.clients[index] = current_item

    def find(self, client):
        """returning a tuple: 1st True or false, 2nd: index value"""
        index = self.binary_search(client, 0, len(self.clients) - 1)
        if index >= 0:
            return (True, index)
        return (False, -1)

    def binary_search(self, searched_client, lower, upper):
        """binary search to search for a client based on username"""
        if lower > upper:
            return -1
        mid = (upper + lower) // 2
        if searched_client > self.clients[mid]:
            return self.binary_search(searched_client, mid + 1, upper)
        elif searched_client < self.clients[mid]:
            return self.binary_search(searched_client, lower, mid - 1)
        else:
            return mid

    def save_list(self):
        """overwrites the client file so changes are stored in the file"""
        with open(self.path, "w", newline="") as f:
            writer = csv.writer(f)
            for client in self.clients:
                writer.writerow(client.to_row())

    def __str__(self):
        return "".join(str(client) + "\n" for client in self.clients)

    def add_client(self, client):
        """adds a client to the list that gets added to the textfile"""
        self.clients.append(client)
        self.sort_list()
        self.save_list()

    def delete_client(self, client):
        """deletes a client, returns True if they were found"""
        found, index = self.find(client)
        if not found:
            return False
        self.clients.pop(index)
        self.save_list()
        return True

    def sorted_by_score(self):
        """Returns a copy of the list in descending order by top score.
        It is a copy so the main list stays sorted by username for the binary search."""
        players = list(self.clients)
        #uses Bubble sort algorithm to sort by highest score
        for iteration in range(len(players) - 1, 0, -1):
            for index in range(iteration):
                if players[index].highest_score < players[index + 1].highest_score:
                    players[index], players[index + 1] = players[index + 1], players[index]
        return players

    def top_players(self, amount=5):
        """returns the players with the best scores (up to amount)"""
        return self.sorted_by_score()[:amount]

    def update_player_in_list(self, player):
        """updates the score and topscore values for an existing player"""
        found, index = self.find(player)
        if not found:
            return False
        stored = self.clients[index]
        stored.score = to_int(player.score)
        if stored.score > stored.highest_score:
            stored.highest_score = stored.score
        self.save_list()
        return True
