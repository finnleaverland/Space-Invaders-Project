"""Player accounts: the Client record, and the ClientList that stores clients in a CSV file.

Each line of the file is: username, password, security question, security answer,
last score, highest score.
"""
import csv
import os

# The client file lives in the project folder, so it works whatever folder you run from
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_FILE = os.path.join(PROJECT_ROOT, "Clientfile.txt")

FIELD_COUNT = 6  # username, password, question, answer, score, highest score
REQUIRED_FIELDS = 4  # lines without the two score columns are still accepted


def to_int(value):
    """Convert a score read from the file to an int. Blank or invalid values become 0."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


class Client:
    """One player account. Clients are compared and sorted by username."""

    def __init__(self, username="", password="", question="", answer="", score=0, highest_score=0):
        self.username = username
        self.password = password
        self.question = question
        self.answer = answer
        self.score = to_int(score)
        self.highest_score = to_int(highest_score)

    def __eq__(self, other):
        return self.username == other.username

    def __lt__(self, other):
        return self.username < other.username

    def __gt__(self, other):
        return self.username > other.username

    def to_row(self):
        """Return the client's fields as a list of strings, ready to be written to the file."""
        return [self.username, self.password, self.question, self.answer,
                str(self.score), str(self.highest_score)]

    def __str__(self):
        return ", ".join(self.to_row())


class ClientList:
    """All the player accounts, loaded from and saved to the client file.

    The list is always kept sorted by username so that the binary search works.
    """

    def __init__(self, path=None):
        self.path = path or CLIENT_FILE
        self.clients = []
        if not os.path.exists(self.path):
            open(self.path, "w").close()  # first run: create an empty client file
        with open(self.path, "r", newline="") as f:
            # skipinitialspace also reads the older "a, b, c" style of file
            for fields in csv.reader(f, skipinitialspace=True):
                if len(fields) < REQUIRED_FIELDS:
                    continue  # skip blank or broken lines
                fields += ["0"] * (FIELD_COUNT - len(fields))  # missing scores count as 0
                self.clients.append(Client(*fields[:FIELD_COUNT]))
        self.sort_list()

    def __len__(self):
        return len(self.clients)

    def __str__(self):
        return "".join(str(client) + "\n" for client in self.clients)

    def sort_list(self):
        """Sort the clients by username using an insertion sort."""
        for i in range(1, len(self.clients)):
            current_item = self.clients[i]
            index = i
            while index > 0 and current_item < self.clients[index - 1]:
                self.clients[index] = self.clients[index - 1]
                index -= 1
            self.clients[index] = current_item

    def find(self, client):
        """Look for a client with the same username.

        Returns (True, index) if they are found, otherwise (False, -1).
        """
        index = self.binary_search(client, 0, len(self.clients) - 1)
        if index >= 0:
            return (True, index)
        return (False, -1)

    def binary_search(self, searched_client, lower, upper):
        """Recursive binary search for a client by username between two indexes.

        Returns the client's index, or -1 if they aren't in the list.
        """
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
        """Overwrite the client file with the current list."""
        with open(self.path, "w", newline="") as f:
            writer = csv.writer(f)
            for client in self.clients:
                writer.writerow(client.to_row())

    def add_client(self, client):
        """Add a new client, keep the list sorted, and save it."""
        self.clients.append(client)
        self.sort_list()
        self.save_list()

    def delete_client(self, client):
        """Delete a client and save the list. Returns True if they were found."""
        found, index = self.find(client)
        if not found:
            return False
        self.clients.pop(index)
        self.save_list()
        return True

    def sorted_by_score(self):
        """Return a copy of the list sorted by highest score (best first) using a bubble sort.

        It is a copy so the main list stays sorted by username for the binary search.
        Players with the same score stay in alphabetical order.
        """
        players = list(self.clients)
        for iteration in range(len(players) - 1, 0, -1):
            for index in range(iteration):
                if players[index].highest_score < players[index + 1].highest_score:
                    players[index], players[index + 1] = players[index + 1], players[index]
        return players

    def top_players(self, amount=5):
        """Return up to `amount` players with the best highest scores."""
        return self.sorted_by_score()[:amount]

    def update_player_in_list(self, player):
        """Save a player's latest score, and their highest score if they beat it.

        Returns False if the player isn't in the list.
        """
        found, index = self.find(player)
        if not found:
            return False
        stored = self.clients[index]
        stored.score = to_int(player.score)
        if stored.score > stored.highest_score:
            stored.highest_score = stored.score
        self.save_list()
        return True
