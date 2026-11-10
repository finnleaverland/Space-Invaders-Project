#GUI login system:

import tkinter as tk

from . import menu_screen
from .accounts import Client, ClientList


def find_client(username):
    """returns (client_list, client) or (client_list, None) if the username doesn't exist
    reads the client file fresh each time so it is never out of date
    (scores get saved by the menu screen while this file is running)"""
    clients = ClientList()
    found, index = clients.find(Client(username))
    if found:
        return clients, clients.clients[index]
    return clients, None


def answers_match(given, correct):
    """security answers ignore capital letters and extra spaces"""
    return given.strip().lower() == correct.strip().lower()


def status_label(window):
    """one label per window for messages, so messages replace each other instead of piling up"""
    label = tk.Label(window, text="")
    label.pack()
    return label


def show_message(label, text, colour="red"):
    label.config(text=text, fg=colour)


def open_menu(client):
    """closes the login window and opens the main menu"""
    screen.destroy()
    menu_screen.main(client)


##register##
def register():
    register_window = tk.Toplevel(screen)
    register_window.title("register")
    register_window.geometry("340x320")

    username = tk.StringVar()
    password = tk.StringVar()
    security_question = tk.StringVar()
    security_answer = tk.StringVar()

    tk.Label(register_window, text="Enter details below:").pack()
    tk.Label(register_window, text="").pack()
    tk.Label(register_window, text="username").pack()
    tk.Entry(register_window, textvariable=username).pack()
    tk.Label(register_window, text="password").pack()
    tk.Entry(register_window, textvariable=password, show="*").pack()
    tk.Label(register_window, text="Security Question").pack()
    tk.Entry(register_window, textvariable=security_question).pack()
    tk.Label(register_window, text="Security Answer").pack()
    tk.Entry(register_window, textvariable=security_answer).pack()
    tk.Label(register_window, text="").pack()
    message = status_label(register_window)

    def register_button():
        username_info = username.get().strip()
        password_info = password.get()
        question_info = security_question.get().strip()
        answer_info = security_answer.get().strip()

        if len(username_info) == 0 or len(username_info) > 10:
            show_message(message, "Username must be 1 to 10 characters")
        elif len(password_info) == 0 or len(question_info) == 0 or len(answer_info) == 0:
            show_message(message, "Please fill in every box")
        elif "," in username_info + password_info + question_info + answer_info:
            show_message(message, "Please don't use commas")
        else:
            clients, existing = find_client(username_info)
            if existing is not None:
                show_message(message, "That username is already taken")
                return
            new_client = Client(username_info, password_info, question_info, answer_info)
            clients.add_client(new_client)  #adds client to the list and saves it
            open_menu(new_client)

    tk.Button(register_window, text="Register", width=10, height=1, command=register_button).pack()


##Login##
def login():
    login_window = tk.Toplevel(screen)
    login_window.title("Login")
    login_window.geometry("300x230")

    username = tk.StringVar()
    password = tk.StringVar()

    tk.Label(login_window, text="Enter details below:").pack()
    tk.Label(login_window, text="").pack()
    tk.Label(login_window, text="username").pack()
    username_entry = tk.Entry(login_window, textvariable=username)
    username_entry.pack()
    tk.Label(login_window, text="password").pack()
    password_entry = tk.Entry(login_window, textvariable=password, show="*")
    password_entry.pack()
    tk.Label(login_window, text="").pack()
    message = status_label(login_window)

    def verify_login():
        clients, client = find_client(username.get().strip())
        if client is None:
            show_message(message, "Incorrect username")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
        elif password.get() != client.password:
            show_message(message, "Incorrect password")
            password_entry.delete(0, tk.END)
        else:
            open_menu(client)

    tk.Button(login_window, text="Login", width=10, height=1, command=verify_login).pack()


def ask_security_question(title, button_text, on_correct_answer):
    """Asks for a username, then that user's security question.
    If the answer is right, on_correct_answer(client_list, client) is called.
    Used by both recover password and change password."""
    username_window = tk.Toplevel(screen)
    username_window.title(title)
    username_window.geometry("300x200")

    username = tk.StringVar()

    tk.Label(username_window, text="Enter details below:").pack()
    tk.Label(username_window, text="").pack()
    tk.Label(username_window, text="username").pack()
    tk.Entry(username_window, textvariable=username).pack()
    tk.Label(username_window, text="").pack()
    message = status_label(username_window)

    def show_question():
        clients, client = find_client(username.get().strip())
        if client is None:
            show_message(message, "That username doesn't exist")
            return

        question_window = tk.Toplevel(screen)
        question_window.title(title)
        question_window.geometry("300x200")
        answer = tk.StringVar()

        tk.Label(question_window, text="Answer the security Question:").pack()
        tk.Label(question_window, text="").pack()
        tk.Label(question_window, text=client.question).pack()
        tk.Entry(question_window, textvariable=answer).pack()
        tk.Label(question_window, text="").pack()
        answer_message = status_label(question_window)

        def check_answer():
            if answers_match(answer.get(), client.answer):
                question_window.destroy()
                username_window.destroy()
                on_correct_answer(clients, client)
            else:
                show_message(answer_message, "Wrong answer, try again")

        tk.Button(question_window, text=button_text, width=15, height=1, command=check_answer).pack()

    tk.Button(username_window, text=button_text, width=15, height=1, command=show_question).pack()


##Recover password##
def show_password(clients, client):
    password_window = tk.Toplevel(screen)
    password_window.title("recover password")
    password_window.geometry("300x200")
    tk.Label(password_window, text="").pack()
    tk.Label(password_window, text="This users password is:").pack()
    tk.Label(password_window, text=client.password).pack()


def recover_password():
    ask_security_question("recover password", "Recover password", show_password)


##Change password##
def enter_new_password(clients, client):
    """Opens a new screen asking for a new password and saves it in the Client file"""
    new_password_window = tk.Toplevel(screen)
    new_password_window.title("change password")
    new_password_window.geometry("300x200")

    new_password = tk.StringVar()

    tk.Label(new_password_window, text="Enter new password:").pack()
    new_password_entry = tk.Entry(new_password_window, textvariable=new_password, show="*")
    new_password_entry.pack()
    message = status_label(new_password_window)

    def set_new_password():
        """overwrites the old password with the new password in the Client file"""
        password_info = new_password.get()
        if len(password_info) == 0 or "," in password_info:
            show_message(message, "Enter a password (no commas)")
            return
        client.password = password_info
        clients.save_list()
        show_message(message, "Password changed", "green")
        new_password_entry.delete(0, tk.END)

    tk.Button(new_password_window, text="confirm change password", command=set_new_password).pack()


def change_password():
    ask_security_question("Change password", "Change password", enter_new_password)


##delete user##
def delete_user():
    delete_window = tk.Toplevel(screen)
    delete_window.title("Delete user")
    delete_window.geometry("300x220")

    username = tk.StringVar()
    password = tk.StringVar()

    tk.Label(delete_window, text="Enter details below:").pack()
    tk.Label(delete_window, text="").pack()
    tk.Label(delete_window, text="username").pack()
    username_entry = tk.Entry(delete_window, textvariable=username)
    username_entry.pack()
    tk.Label(delete_window, text="password").pack()
    password_entry = tk.Entry(delete_window, textvariable=password, show="*")
    password_entry.pack()
    tk.Label(delete_window, text="").pack()
    message = status_label(delete_window)

    def delete_user_button():
        clients, client = find_client(username.get().strip())
        #only delete if the password is right
        if client is not None and password.get() == client.password:
            clients.delete_client(client)
            show_message(message, "Delete user success", "green")
        else:
            show_message(message, "Wrong username or password")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

    tk.Button(delete_window, text="Delete user", width=15, height=1, command=delete_user_button).pack()


##main screen##
def main():
    global screen
    screen = tk.Tk()
    screen.title("Login: Space Invaders")
    screen.geometry("300x195")

    tk.Label(text="login system:", bg="orange", width="300", height="2").pack()
    tk.Label(text="").pack()
    tk.Button(text="Login", command=login).pack()
    tk.Button(text="Register", command=register).pack()
    tk.Button(text="Recover password", command=recover_password).pack()
    tk.Button(text="Change password", command=change_password).pack()
    tk.Button(text="Delete user", command=delete_user).pack()

    screen.mainloop()
