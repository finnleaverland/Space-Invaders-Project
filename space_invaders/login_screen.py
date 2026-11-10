"""Screens shown before logging in: welcome, log in, register and reset password."""
from tkinter import ttk

from . import theme
from .accounts import Client, ClientList
from .widgets import Screen

MAX_USERNAME_LENGTH = 10


def find_client(username):
    """Look up a username in a freshly loaded client list.

    The file is re-read every time because scores are saved to it after each game.
    Returns (client_list, client), with client None if the username doesn't exist.
    """
    clients = ClientList()
    found, index = clients.find(Client(username))
    return clients, clients.clients[index] if found else None


class WelcomeScreen(Screen):
    """The first screen: choose to log in, register or reset a password."""

    def build(self):
        self.add_title("SPACE INVADERS", "Defend the planet. Beat the high score.")
        self.add_button("Log in", lambda: self.app.show("login"), primary=True)
        self.add_button("Register", lambda: self.app.show("register"))
        self.add_button("Reset password", lambda: self.app.show("reset_password"))
        self.add_message_line()
        self.add_back_button(self.app.quit, text="Quit")


class LoginScreen(Screen):
    """Log in with a username and password."""

    def build(self):
        self.add_title("Log in")
        self.username_entry = self.add_field("Username")
        self.password_entry = self.add_field("Password", hidden=True)
        self.add_button("Log in", self.submit, primary=True)
        self.add_message_line()
        self.add_back_button(lambda: self.app.show("welcome"))

    def submit(self):
        clients, client = find_client(self.username_entry.get().strip())
        if client is None:
            self.show_error("Incorrect username")
        elif not client.check_password(self.password_entry.get()):
            self.show_error("Incorrect password")
            self.password_entry.delete(0, "end")
        else:
            self.app.log_in(client)


class RegisterScreen(Screen):
    """Create a new account."""

    def build(self):
        self.add_title("Create account")
        self.username_entry = self.add_field(f"Username (up to {MAX_USERNAME_LENGTH} characters)")
        self.password_entry = self.add_field("Password", hidden=True)
        self.question_entry = self.add_field("Security question")
        self.answer_entry = self.add_field("Security answer")
        self.add_button("Create account", self.submit, primary=True)
        self.add_message_line()
        self.add_back_button(lambda: self.app.show("welcome"))

    def submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        question = self.question_entry.get().strip()
        answer = self.answer_entry.get().strip()

        if len(username) == 0 or len(username) > MAX_USERNAME_LENGTH:
            self.show_error(f"Username must be 1 to {MAX_USERNAME_LENGTH} characters")
        elif len(password) == 0 or len(question) == 0 or len(answer) == 0:
            self.show_error("Please fill in every box")
        elif "," in username + password + question + answer:
            self.show_error("Please don't use commas")
        else:
            clients, existing = find_client(username)
            if existing is not None:
                self.show_error("That username is already taken")
                return
            new_client = Client.new(username, password, question, answer)
            clients.add_client(new_client)
            self.app.log_in(new_client)


class ResetPasswordScreen(Screen):
    """Reset a forgotten password by answering the account's security question.

    Step 1 asks for the username; step 2 shows the question and asks for the answer
    and a new password.
    """

    def build(self):
        self.client = None
        self.clients = None
        self.add_title("Reset password")
        self.username_entry = self.add_field("Username")
        self.next_button = self.add_button("Next", self.find_account, primary=True)

        # Step 2, shown once the username is found
        self.step_two = ttk.Frame(self.body)
        self.question_label = ttk.Label(self.step_two, text="", wraplength=theme.px(theme.TEXT_WIDTH),
                                        justify="center")
        self.question_label.pack(pady=(theme.px(theme.GAP), theme.px(theme.FIELD_GAP)))
        ttk.Label(self.step_two, text="Answer", style="Muted.TLabel").pack(fill="x")
        self.answer_entry = ttk.Entry(self.step_two)
        self.answer_entry.pack(fill="x", pady=theme.px(theme.FIELD_GAP))
        ttk.Label(self.step_two, text="New password", style="Muted.TLabel").pack(fill="x")
        self.password_entry = ttk.Entry(self.step_two, show="•")
        self.password_entry.pack(fill="x", pady=theme.px(theme.FIELD_GAP))
        ttk.Button(self.step_two, text="Save new password", command=self.submit,
                   style="Accent.TButton").pack(fill="x", pady=(theme.px(theme.GAP // 2), 0))

        self.add_message_line()
        self.add_back_button(lambda: self.app.show("welcome"))

    def find_account(self):
        self.clients, self.client = find_client(self.username_entry.get().strip())
        if self.client is None:
            self.show_error("That username doesn't exist")
            return
        self.clear_message()
        self.username_entry.state(["disabled"])
        self.next_button.pack_forget()
        self.question_label.configure(text=self.client.question)
        self.step_two.pack(fill="x", after=self.username_entry)

    def submit(self):
        new_password = self.password_entry.get()
        if not self.client.check_answer(self.answer_entry.get()):
            self.show_error("Wrong answer, try again")
        elif len(new_password) == 0 or "," in new_password:
            self.show_error("Enter a password (no commas)")
        else:
            self.client.set_password(new_password)
            self.clients.save_list()
            self.app.show("login", message="Password changed. Log in with your new password.")
