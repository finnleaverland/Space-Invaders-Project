#Client system login

import csv
import os

#Store the client file next to this script so it works whatever folder you run from
DEFAULT_CLIENT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Clientfile.txt")


def to_int(value):
    """turns a score read from the file into an int (blank or bad values become 0)"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


class Client():
    """initialises the client class"""
    def __init__(self, username = "", password= "", question= "", answer= "", score = 0, highest_score = 0):
        self.username = username
        self.password = password
        self.question = question
        self.answer = answer
        self.score = to_int(score)
        self.highest_score = to_int(highest_score)

    #modifier methods
    def set_username(self, newusername):
        self.username = newusername
    def set_password(self, newpassword):
        self.password = newpassword
    def set_question(self, newquestion):
        self.question = newquestion
    def set_answer(self, newanswer):
        self.answer = newanswer
    def set_score(self, newscore):
        self.score = to_int(newscore)
    def set_highest_score(self, new_highest_score):
        self.highest_score = to_int(new_highest_score)

    #accessor methods
    def get_username(self):
        return self.username
    def get_password(self):
        return self.password
    def get_question(self):
        return self.question
    def get_answer(self):
        return self.answer
    def get_score(self):
        return self.score
    def get_highest_score(self):
        return self.highest_score

    #comparison operators (clients are compared by username)
    def __eq__(self, arg):
        return self.username == arg.get_username()

    def __lt__(self, arg):
        """less than"""
        return self.username < arg.get_username()

    def __gt__(self, arg):
        """greater than"""
        return self.username > arg.get_username()

    def to_row(self):
        """the client as a list of fields, ready to be written to the file"""
        return [self.username, self.password, self.question, self.answer, str(self.score), str(self.highest_score)]

    def __str__(self):
        """How the class is presented / printed as"""
        return ", ".join(self.to_row())


class client_list():
    """read clients from a file / validation
    The list is always kept sorted by username so the binary search works."""
    def __init__(self, textfile = DEFAULT_CLIENT_FILE):
        self.list = []
        self.count = 0
        self.textfile = textfile
        if not os.path.exists(self.textfile):
            #first run: create an empty client file
            open(self.textfile, 'w').close()
        with open(self.textfile, 'r', newline='') as f:
            #skipinitialspace lets this read the old "a, b, c" format too
            for fields in csv.reader(f, skipinitialspace=True):
                if len(fields) < 4:
                    continue #skip blank or broken lines
                while len(fields) < 6:
                    fields.append("0") #missing scores count as 0
                username, password, question, answer, score, highest_score = fields[:6]
                next_client = Client(username, password, question, answer, score, highest_score)
                self.list.append(next_client)
                self.count +=1
        self.sort_list()

    def get_num_clients(self):
        """returns the number of clients in the client list"""
        return self.count

    def sort_list(self):
        """insertion sort to sort based on username"""
        for i in range(1, self.count):
            current_item = self.list[i]
            index = i
            while index > 0 and current_item < self.list[index - 1]:
                self.list[index] = self.list[index - 1]
                index = index - 1
            self.list[index] = current_item

    def find(self, dclient):
        """returning a tuple: 1st True or false, 2nd: index value"""
        index = self.search(dclient, 0, self.count - 1)
        if index >= 0:
            return (True, index)
        else:
            return (False, -1)

    def search(self, searched_client, lower, upper):
        """binary search to search for a client based on username"""
        if lower > upper:
            return -1
        mid = (upper + lower)//2
        if searched_client > self.list[mid]:
            return self.search(searched_client, mid + 1, upper)
        elif searched_client < self.list[mid]:
            return self.search(searched_client, lower, mid - 1)
        else:
            return mid

    def get_client(self, index):
        """Gets the client at an index"""
        return self.list[index]

    def save_list(self):
        """overwrites the client file so changes are stored in the file"""
        with open(self.textfile, 'w', newline='') as f:
            writer = csv.writer(f)
            for index in range(0, self.count):
                writer.writerow(self.list[index].to_row())

    def __str__(self):
        temp = ""
        for client in self.list:
            temp += (str(client)+"\n")
        return temp

    def add_client(self, dclient):
        """adds a client to the list that gets added to the textfile"""
        self.list.append(dclient)
        self.count +=1
        self.sort_list()
        self.save_list()

    def delete_client(self, dclient):
        """deletes a client, returns True if they were found"""
        index = self.search(dclient, 0, self.count-1)
        if index < 0:
            return False
        self.list.pop(index)
        self.count -= 1
        self.save_list()
        return True

    def sorted_by_score(self):
        """Returns a copy of the list in descending order by top score.
        It is a copy so the main list stays sorted by username for the binary search."""
        players = list(self.list)
        #uses Bubble sort algorithm to sort by highest score
        for iteration in range(len(players)-1, 0, -1):
            for index in range(iteration):
                if players[index].get_highest_score() < players[index+1].get_highest_score():
                    temp = players[index]
                    players[index] = players[index+1]
                    players[index+1] = temp
        return players

    def top_players(self, amount = 5):
        """returns the players with the best scores (up to amount)"""
        return self.sorted_by_score()[:amount]

    def update_player_in_list(self, player):
        """updates the score and topscore values for an existing player"""
        found, index = self.find(player)
        if not found:
            return False
        stored = self.list[index]
        stored.set_score(player.get_score())
        if stored.get_score() > stored.get_highest_score():
            stored.set_highest_score(stored.get_score())
        self.save_list()
        return True


#driving code
if __name__ == "__main__":
    c_list = client_list()
    print(c_list)
    for player in c_list.top_players():
        print(player.get_username(), player.get_highest_score())