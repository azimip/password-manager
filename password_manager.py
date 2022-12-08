import sqlite3

import pwinput
from rich import print as rprint
from rich.console import Console
from rich.prompt import Prompt
from rich.tree import Tree

console = Console()


class UserManager:
    def __init__(self, username, password, db, persist=True):
        self.username = username
        self.password = password
        self.db = db
        self.db_cursor = self.db.get_cursor()
        if persist:
            self.persist()

    def persist(self):
        self.db_cursor.execute("INSERT INTO users VALUES (?, ?)", (self.username, self.password), )
        self.db.commit()

    def check_pass(self):
        real_pass = \
            self.db_cursor.execute("SELECT password FROM users WHERE username = ?", (self.username,), ).fetchall()[0][0]
        return real_pass == self.password


class PasswordManager:
    def __init__(self, user, db):
        self.user = user
        self.db = db
        self.db_cursor = self.db.get_cursor()

    def get_all_available_sources(self):
        sources = [row[0] for row in self.db_cursor.execute("SELECT source FROM passwords WHERE user = ?",
                                                            (self.user,), ).fetchall()]
        return sources

    def get_user_pass(self, source):
        user_pass = [(row[0], row[1]) for row in
                     self.db_cursor.execute("SELECT username, password FROM passwords WHERE user = ? and source = ?",
                                            (self.user, source), ).fetchall()]
        if not user_pass:
            raise Exception("Source does not exist")
        username = user_pass[0][0]
        password = user_pass[0][1]
        return username, password

    def set_new_user_pass(self, source, username, password):
        sources = self.get_all_available_sources()
        if source in sources:
            raise Exception("Source already exists")
        self.db_cursor.execute("INSERT INTO passwords VALUES (?, ?, ?, ?)",
                               (self.user, source, username, password), )
        self.db.commit()


class Password:
    def __init__(self):
        self._passwords = []

    def get_latest_password(self):
        return self._passwords[0]

    def set_password(self, password):
        self._passwords.append(password)

    @staticmethod
    def is_strong_password(password):
        return True


class ConsoleApp:
    def __init__(self):
        self.db = DBManager('password_manager')
        self.pm = None
        self.user = None

    def run(self):
        self.welcome()
        choice = self.get_initial_choice()
        if choice == "1":
            self.user = self.login()
        if choice == "2":
            self.user = self.create_user()
        self.pm = PasswordManager(self.user, self.db)

    @staticmethod
    def welcome():
        style1 = "blink bold blue on white"
        console.rule()
        console.print(" Welcome to the Super Strong Password Manager!", style=style1, justify="center")
        console.rule()

    @staticmethod
    def get_initial_choice():
        tree = Tree("What can I do for you?")
        tree.add("1. Login")
        tree.add("2. Create Account")
        rprint(tree)
        choice = Prompt.ask(
            "Choose from",
            choices=["1", "2"],
        )
        return choice

    def create_user(self):
        username = self._new_username_prompt()
        password = self._new_password_prompt()
        UserManager(username, password, self.db)
        return username

    def login(self):
        username = None
        all_users = get_all_users(self.db.get_cursor())
        is_acceptable = False
        while not is_acceptable:
            username = Prompt.ask(
                "Please enter your username",
            )
            if username not in all_users:
                console.print("Account with this username does not exist!", style="bold red")
            else:
                is_acceptable = True
        is_acceptable = False
        while not is_acceptable:
            password = pwinput.pwinput()
            user = UserManager(username, password, self.db, persist=False)
            if user.check_pass():
                is_acceptable = True
            else:
                console.print("Password is wrong!", style="bold red")
        return username

    def _new_username_prompt(self):
        username = None
        all_users = get_all_users(self.db.get_cursor())
        is_acceptable = False
        while not is_acceptable:
            username = Prompt.ask(
                "Please enter your username",
            )
            if username in all_users:
                console.print("Username already exists!", style="bold red")
            else:
                is_acceptable = True
        return username

    @staticmethod
    def _new_password_prompt():
        is_acceptable = False
        password = None
        while not is_acceptable:
            password = pwinput.pwinput()
            if Password.is_strong_password(password):
                is_acceptable = True
            else:
                console.print("Password is too weak!", style="bold red")
        return password


class DBManager:
    def __init__(self, name):
        self.name = name
        self.db_name = f'{name}.db'
        self.connection = sqlite3.connect(self.db_name)

    def get_cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()


def get_all_users(db_cursor):
    users = [row[0] for row in db_cursor.execute("SELECT username FROM users").fetchall()]
    return users


if __name__ == '__main__':
    console_interface = ConsoleApp()
    console_interface.run()
    d = DBManager('password_manager')
    cursor = d.get_cursor()
    user = 'John'
    pm = PasswordManager(user, d)
    # pm.set_new_user_pass('google', 'gagool', '12345')
    # print(get_all_users(cursor))
    # print(pm.get_all_available_sources())
    # print(pm.get_user_pass('google'))
