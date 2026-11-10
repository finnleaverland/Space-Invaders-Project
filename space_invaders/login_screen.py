"""The login window (tkinter): log in, register, recover or change a password, or delete an account."""
import tkinter as tk

from . import menu_screen
from .accounts import Client, ClientList

MAX_USERNAME_LENGTH = 10

# Window sizes
MAIN_WINDOW_SIZE = "300x195"
REGISTER_WINDOW_SIZE = "340x320"
LOGIN_WINDOW_SIZE = "300x230"
DELETE_WINDOW_SIZE = "300x220"
SMALL_WINDOW_SIZE = "300x200"

# Colours and widget sizes
HEADER_COLOUR = "orange"
HEADER_WIDTH = 300
HEADER_HEIGHT = 2
ERROR_COLOUR = "red"
SUCCESS_COLOUR = "green"
SHORT_BUTTON_WIDTH = 10
WIDE_BUTTON_WIDTH = 15


def find_client(username):
    """Look up a username in a freshly loaded client list.

    The file is re-read every time because the menu saves new scores to it while
    this window is open. Returns (client_list, client), with client None if the
    username doesn't exist.
    """
    clients = ClientList()
    found, index = clients.find(Client(username))
    return clients, clients.clients[index] if found else None


def answers_match(given, correct):
    """Compare security answers, ignoring capital letters and surrounding spaces."""
    return given.strip().lower() == correct.strip().lower()


def new_window(parent, title, size):
    """Open a pop-up window on top of the login screen."""
    window = tk.Toplevel(parent)
    window.title(title)
    window.geometry(size)
    return window


def add_spacer(window):
    """Add an empty line to a window."""
    tk.Label(window, text="").pack()


def add_entry(window, label_text, hidden=False):
    """Add a labelled text box to a window and return the box."""
    tk.Label(window, text=label_text).pack()
    entry = tk.Entry(window, show="*" if hidden else "")
    entry.pack()
    return entry


def add_status_label(window):
    """Add one label for messages, so new messages replace old ones instead of piling up."""
    label = tk.Label(window, text="")
    label.pack()
    return label


def show_message(label, text, colour=ERROR_COLOUR):
    """Show a message (red for errors by default) in a status label."""
    label.config(text=text, fg=colour)


def clear(*entries):
    """Empty one or more text boxes."""
    for entry in entries:
        entry.delete(0, tk.END)


class LoginScreen:
    """The first window the player sees, with a button for each account action."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login: Space Invaders")
        self.root.geometry(MAIN_WINDOW_SIZE)

        tk.Label(self.root, text="login system:", bg=HEADER_COLOUR,
                 width=HEADER_WIDTH, height=HEADER_HEIGHT).pack()
        add_spacer(self.root)
        tk.Button(self.root, text="Login", command=self.open_login).pack()
        tk.Button(self.root, text="Register", command=self.open_register).pack()
        tk.Button(self.root, text="Recover password", command=self.open_recover_password).pack()
        tk.Button(self.root, text="Change password", command=self.open_change_password).pack()
        tk.Button(self.root, text="Delete user", command=self.open_delete_user).pack()

    def run(self):
        """Show the window and wait for the player."""
        self.root.mainloop()

    def open_menu(self, client):
        """Close the login window and open the main menu for a logged-in player."""
        self.root.destroy()
        menu_screen.main(client)

    def open_register(self):
        """Open the form for creating a new account."""
        window = new_window(self.root, "register", REGISTER_WINDOW_SIZE)
        tk.Label(window, text="Enter details below:").pack()
        add_spacer(window)
        username_entry = add_entry(window, "username")
        password_entry = add_entry(window, "password", hidden=True)
        question_entry = add_entry(window, "Security Question")
        answer_entry = add_entry(window, "Security Answer")
        add_spacer(window)
        message = add_status_label(window)

        def register():
            username = username_entry.get().strip()
            password = password_entry.get()
            question = question_entry.get().strip()
            answer = answer_entry.get().strip()

            if len(username) == 0 or len(username) > MAX_USERNAME_LENGTH:
                show_message(message, f"Username must be 1 to {MAX_USERNAME_LENGTH} characters")
            elif len(password) == 0 or len(question) == 0 or len(answer) == 0:
                show_message(message, "Please fill in every box")
            elif "," in username + password + question + answer:
                show_message(message, "Please don't use commas")
            else:
                clients, existing = find_client(username)
                if existing is not None:
                    show_message(message, "That username is already taken")
                    return
                new_client = Client(username, password, question, answer)
                clients.add_client(new_client)  # adds the client to the list and saves it
                self.open_menu(new_client)

        tk.Button(window, text="Register", width=SHORT_BUTTON_WIDTH, height=1, command=register).pack()

    def open_login(self):
        """Open the form for logging in."""
        window = new_window(self.root, "Login", LOGIN_WINDOW_SIZE)
        tk.Label(window, text="Enter details below:").pack()
        add_spacer(window)
        username_entry = add_entry(window, "username")
        password_entry = add_entry(window, "password", hidden=True)
        add_spacer(window)
        message = add_status_label(window)

        def log_in():
            clients, client = find_client(username_entry.get().strip())
            if client is None:
                show_message(message, "Incorrect username")
                clear(username_entry, password_entry)
            elif password_entry.get() != client.password:
                show_message(message, "Incorrect password")
                clear(password_entry)
            else:
                self.open_menu(client)

        tk.Button(window, text="Login", width=SHORT_BUTTON_WIDTH, height=1, command=log_in).pack()

    def ask_security_question(self, title, button_text, on_correct_answer):
        """Ask for a username, then ask that user's security question.

        If the answer is right, both windows close and on_correct_answer(client_list, client)
        is called. Used by both recover password and change password.
        """
        username_window = new_window(self.root, title, SMALL_WINDOW_SIZE)
        tk.Label(username_window, text="Enter details below:").pack()
        add_spacer(username_window)
        username_entry = add_entry(username_window, "username")
        add_spacer(username_window)
        message = add_status_label(username_window)

        def show_question():
            clients, client = find_client(username_entry.get().strip())
            if client is None:
                show_message(message, "That username doesn't exist")
                return

            question_window = new_window(self.root, title, SMALL_WINDOW_SIZE)
            tk.Label(question_window, text="Answer the security Question:").pack()
            add_spacer(question_window)
            tk.Label(question_window, text=client.question).pack()
            answer_entry = tk.Entry(question_window)
            answer_entry.pack()
            add_spacer(question_window)
            answer_message = add_status_label(question_window)

            def check_answer():
                if answers_match(answer_entry.get(), client.answer):
                    question_window.destroy()
                    username_window.destroy()
                    on_correct_answer(clients, client)
                else:
                    show_message(answer_message, "Wrong answer, try again")

            tk.Button(question_window, text=button_text, width=WIDE_BUTTON_WIDTH, height=1,
                      command=check_answer).pack()

        tk.Button(username_window, text=button_text, width=WIDE_BUTTON_WIDTH, height=1,
                  command=show_question).pack()

    def open_recover_password(self):
        """Show a user's password once they answer their security question."""
        self.ask_security_question("recover password", "Recover password", self.show_password)

    def show_password(self, clients, client):
        """Open a window showing the user's password."""
        window = new_window(self.root, "recover password", SMALL_WINDOW_SIZE)
        add_spacer(window)
        tk.Label(window, text="This users password is:").pack()
        tk.Label(window, text=client.password).pack()

    def open_change_password(self):
        """Let a user set a new password once they answer their security question."""
        self.ask_security_question("Change password", "Change password", self.enter_new_password)

    def enter_new_password(self, clients, client):
        """Open a window asking for a new password and save it to the client file."""
        window = new_window(self.root, "change password", SMALL_WINDOW_SIZE)
        password_entry = add_entry(window, "Enter new password:", hidden=True)
        message = add_status_label(window)

        def set_new_password():
            new_password = password_entry.get()
            if len(new_password) == 0 or "," in new_password:
                show_message(message, "Enter a password (no commas)")
                return
            client.password = new_password
            clients.save_list()
            show_message(message, "Password changed", SUCCESS_COLOUR)
            clear(password_entry)

        tk.Button(window, text="confirm change password", command=set_new_password).pack()

    def open_delete_user(self):
        """Open the form for deleting an account (needs the right password)."""
        window = new_window(self.root, "Delete user", DELETE_WINDOW_SIZE)
        tk.Label(window, text="Enter details below:").pack()
        add_spacer(window)
        username_entry = add_entry(window, "username")
        password_entry = add_entry(window, "password", hidden=True)
        add_spacer(window)
        message = add_status_label(window)

        def delete_user():
            clients, client = find_client(username_entry.get().strip())
            if client is not None and password_entry.get() == client.password:
                clients.delete_client(client)
                show_message(message, "Delete user success", SUCCESS_COLOUR)
            else:
                show_message(message, "Wrong username or password")
            clear(username_entry, password_entry)

        tk.Button(window, text="Delete user", width=WIDE_BUTTON_WIDTH, height=1, command=delete_user).pack()


def main():
    """Open the login screen."""
    LoginScreen().run()
