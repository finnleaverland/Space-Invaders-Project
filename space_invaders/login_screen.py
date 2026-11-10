#GUI login system:

from tkinter import *

from . import accounts as LS
from . import menu_screen as mainscreen


def load_clients():
    """reads the client file fresh each time so it is never out of date
    (scores get saved by the menu screen while this file is running)"""
    return LS.client_list()


def find_client(username):
    """returns (client_list, client) or (client_list, None) if the username doesn't exist"""
    clist = load_clients()
    found, index = clist.find(LS.Client(username))
    if found:
        return clist, clist.get_client(index)
    return clist, None


def answers_match(given, correct):
    """security answers ignore capital letters and extra spaces"""
    return given.strip().lower() == correct.strip().lower()


def status_label(window):
    """one label per window for messages, so messages replace each other instead of piling up"""
    label = Label(window, text = "")
    label.pack()
    return label


def show_message(label, text, colour = "red"):
    label.config(text = text, fg = colour)


def open_menu(client):
    """closes the login window and opens the main menu"""
    screen.destroy()
    mainscreen.menu_screen(client)


##register##
def register():
    screen1 = Toplevel(screen)
    screen1.title("register")
    screen1.geometry("340x320")

    username = StringVar()
    password = StringVar()
    security_question = StringVar()
    security_answer = StringVar()

    Label(screen1, text = "Enter details below:").pack()
    Label(screen1, text = "").pack()
    Label(screen1, text = "username").pack()
    Entry(screen1, textvariable = username).pack()
    Label(screen1, text = "password").pack()
    Entry(screen1, textvariable = password, show = "*").pack()
    Label(screen1, text = "Security Question").pack()
    Entry(screen1, textvariable = security_question).pack()
    Label(screen1, text = "Security Answer").pack()
    Entry(screen1, textvariable = security_answer).pack()
    Label(screen1, text = "").pack()
    message = status_label(screen1)

    def register_button():
        username_info = username.get().strip()
        password_info = password.get()
        security_question_info = security_question.get().strip()
        security_answer_info = security_answer.get().strip() #returns them as strings

        if len(username_info) == 0 or len(username_info) > 10:
            show_message(message, "Username must be 1 to 10 characters")
        elif len(password_info) == 0 or len(security_question_info) == 0 or len(security_answer_info) == 0:
            show_message(message, "Please fill in every box")
        elif "," in username_info + password_info + security_question_info + security_answer_info:
            show_message(message, "Please don't use commas")
        else:
            clist, existing = find_client(username_info)
            if existing is not None:
                show_message(message, "That username is already taken")
                return
            dclient = LS.Client(username_info, password_info, security_question_info, security_answer_info)
            clist.add_client(dclient) #adds client to the list and saves it
            open_menu(dclient)

    Button(screen1, text = "Register", width = 10, height = 1, command = register_button).pack()


##Login##
def Login():
    screen2 = Toplevel(screen)
    screen2.title("Login")
    screen2.geometry("300x230")

    username_verify = StringVar()
    password_verify = StringVar()

    Label(screen2, text = "Enter details below:").pack()
    Label(screen2, text = "").pack()
    Label(screen2, text = "username").pack()
    username_entry = Entry(screen2, textvariable = username_verify)
    username_entry.pack()
    Label(screen2, text = "password").pack()
    password_entry = Entry(screen2, textvariable = password_verify, show = "*")
    password_entry.pack()
    Label(screen2, text = "").pack()
    message = status_label(screen2)

    def Login_verify():
        username_info = username_verify.get().strip()
        password_info = password_verify.get()

        clist, fclient = find_client(username_info)
        if fclient is None:
            show_message(message, "Incorrect username")
            username_entry.delete(0, END)
            password_entry.delete(0, END)
        elif password_info != fclient.get_password():
            show_message(message, "Incorrect password")
            password_entry.delete(0, END)
        else:
            open_menu(fclient)

    Button(screen2, text = "Login", width= 10, height= 1, command= Login_verify).pack()


def ask_security_question(title, button_text, on_correct_answer):
    """Asks for a username, then that user's security question.
    If the answer is right, on_correct_answer(client_list, client) is called.
    Used by both recover password and change password."""
    username_screen = Toplevel(screen)
    username_screen.title(title)
    username_screen.geometry("300x200")

    username_verify = StringVar()

    Label(username_screen, text = "Enter details below:").pack()
    Label(username_screen, text = "").pack()
    Label(username_screen, text = "username").pack()
    Entry(username_screen, textvariable = username_verify).pack()
    Label(username_screen, text = "").pack()
    message = status_label(username_screen)

    def Question():
        clist, dclient = find_client(username_verify.get().strip())
        if dclient is None:
            show_message(message, "That username doesn't exist")
            return

        question_screen = Toplevel(screen)
        question_screen.title(title)
        question_screen.geometry("300x200")
        security_answer_verify = StringVar()

        Label(question_screen, text = "Answer the security Question:").pack()
        Label(question_screen, text = "").pack()
        Label(question_screen, text = dclient.get_question()).pack()
        Entry(question_screen, textvariable = security_answer_verify).pack()
        Label(question_screen, text = "").pack()
        answer_message = status_label(question_screen)

        def check_answer():
            if answers_match(security_answer_verify.get(), dclient.get_answer()):
                question_screen.destroy()
                username_screen.destroy()
                on_correct_answer(clist, dclient)
            else:
                show_message(answer_message, "Wrong answer, try again")

        Button(question_screen, text = button_text, width = 15, height = 1, command = check_answer).pack()

    Button(username_screen, text = button_text, width= 15, height= 1, command = Question).pack()


##Recover password##
def show_password(clist, dclient):
    screen7 = Toplevel(screen)
    screen7.title("recover password")
    screen7.geometry("300x200")
    Label(screen7, text = "").pack()
    Label(screen7, text = "This users password is:").pack()
    Label(screen7, text = dclient.get_password()).pack()

def recover_password():
    ask_security_question("recover password", "Recover password", show_password)


##Change password##
def enter_new_password(clist, dclient):
    """Opens a new screen asking for a new password and saves it in the Client file"""
    screen9 = Toplevel(screen)
    screen9.title("change password")
    screen9.geometry("300x200")

    newpassword_verify = StringVar()

    Label(screen9, text = "Enter new password:").pack()
    newpassword = Entry(screen9, textvariable = newpassword_verify, show = "*")
    newpassword.pack()
    message = status_label(screen9)

    def set_new_password():
        """overwrites the old password with the new password in the Client file"""
        newpassword_info = newpassword_verify.get()
        if len(newpassword_info) == 0 or "," in newpassword_info:
            show_message(message, "Enter a password (no commas)")
            return
        dclient.set_password(newpassword_info)
        clist.save_list()
        show_message(message, "Password changed", "green")
        newpassword.delete(0, END)

    Button(screen9, text= "confirm change password", command = set_new_password).pack()

def change_password():
    ask_security_question("Change password", "Change password", enter_new_password)


##delete user##
def delete_user():
    screen5 = Toplevel(screen)
    screen5.title("Delete user")
    screen5.geometry("300x220")

    username_verify = StringVar()
    password_verify = StringVar()

    Label(screen5, text = "Enter details below:").pack()
    Label(screen5, text = "").pack()
    Label(screen5, text = "username").pack()
    username_entry = Entry(screen5, textvariable = username_verify)
    username_entry.pack()
    Label(screen5, text = "password").pack()
    password_entry = Entry(screen5, textvariable = password_verify, show = "*")
    password_entry.pack()
    Label(screen5, text = "").pack()
    message = status_label(screen5)

    def delete_user_button():
        clist, dclient = find_client(username_verify.get().strip())
        #only delete if the password is right
        if dclient is not None and password_verify.get() == dclient.get_password():
            clist.delete_client(dclient)
            show_message(message, "Delete user success", "green")
        else:
            show_message(message, "Wrong username or password")
        username_entry.delete(0, END)
        password_entry.delete(0, END)

    Button(screen5, text = "Delete user", width= 15, height= 1, command= delete_user_button).pack()


##main screen##
def main_screen():
    global screen
    screen = Tk()
    screen.title('Login: Space Invaders')
    screen.geometry("300x195")

    Label(text = "login system:", bg = "orange", width = "300", height = "2").pack()
    Label(text = "").pack()
    Button(text = "Login", command = Login).pack()
    Button(text = "Register", command = register).pack()
    Button(text = "Recover password", command = recover_password).pack()
    Button(text = "Change password", command = change_password).pack()
    Button(text = "Delete user", command = delete_user).pack()

    screen.mainloop()

if __name__ == "__main__":
    main_screen()