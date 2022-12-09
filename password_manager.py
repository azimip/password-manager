import sqlite3

import pwinput
from rich import print as rprint
from rich.console import Console
from rich.prompt import Prompt
from rich.tree import Tree

from utils.hash import get_hash

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
        password_hash = get_hash(self.password)
        self.db_cursor.execute("INSERT INTO users VALUES (?, ?)", (self.username, password_hash), )
        self.db.commit()

    def check_pass(self):
        real_pass_hash = \
            self.db_cursor.execute("SELECT password FROM users WHERE username = ?", (self.username,), ).fetchall()[0][0]
        return real_pass_hash == get_hash(self.password)

    def set_new_password(self, old_password, new_password):
        current_pass_hash = \
            self.db_cursor.execute("SELECT password FROM users WHERE username = ?", (self.username,), ).fetchall()[0][0]
        if current_pass_hash != get_hash(old_password):
            raise Exception("Old password is wrong")
        new_password_hash = get_hash(new_password)
        self.db_cursor.execute("UPDATE users SET password = ? WHERE username = ?",
                               (new_password_hash, self.username), )
        self.db.commit()
        self.password = new_password


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

    def update_previous_password(self, source, username, password):
        sources = self.get_all_available_sources()
        if source not in sources:
            raise Exception("Source is not available")
        self.db_cursor.execute("UPDATE passwords SET password = ?, username = ? WHERE user = ? and source = ?",
                               (password, username, self.user, source), )
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
        goodbye = False
        while not goodbye:
            choice = self.get_main_action()
            if choice == "1":
                self.get_previous_passwords()
            if choice == "2":
                self.add_new_password()
            if choice == "3":
                self.change_password_of_source()
            if choice == "4":
                self.change_master_password()
            if choice == "5":
                self.goodbye()
                goodbye = True

    @staticmethod
    def welcome():
        style1 = "blink bold blue"
        console.rule(style="blue")
        console.print("Welcome to the Super Strong Password Manager!", style=style1, justify="center")
        console.rule(style="blue")

    @staticmethod
    def goodbye():
        style1 = "bold blue"
        console.rule(style="blue")
        console.print("Have a safe day!", style=style1, justify="center")
        console.rule(style="blue")

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

    @staticmethod
    def get_main_action():
        tree = Tree("\nWhat is your next step?")
        tree.add("1. Get a list of previously set passwords")
        tree.add("2. Add a new password")
        tree.add("3. Change password of a source")
        tree.add("4. Change my Master Password")
        tree.add("5. Exit")
        rprint(tree)
        choice = Prompt.ask(
            "Choose from",
            choices=["1", "2", "3", "4", "5"],
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
    def _new_password_prompt(prompt="Password: "):
        is_acceptable = False
        password = None
        while not is_acceptable:
            password = pwinput.pwinput(prompt=prompt)
            if Password.is_strong_password(password):
                is_acceptable = True
            else:
                console.print("Password is too weak!", style="bold red")
        return password

    def get_previous_passwords(self):
        all_sources = self.pm.get_all_available_sources()
        if not all_sources:
            console.print("There is no previously set password!", style="bold red")
            return
        source = Prompt.ask(
            "Available sources",
            choices=all_sources,
        )
        username, password = self.pm.get_user_pass(source)
        console.print(f'Your username for {source} is:', style="blue")
        console.print(username)
        console.print(f'Your password for {source} is:', style="blue")
        console.print(password)

    def add_new_password(self):
        all_sources = self.pm.get_all_available_sources()
        is_acceptable = False
        source = None
        while not is_acceptable:
            source = Prompt.ask("Enter the source name")
            if source in all_sources:
                console.print("Source already exists!", style="bold red")
            else:
                is_acceptable = True
        username = Prompt.ask("Username")
        password = self._new_password_prompt()
        self.pm.set_new_user_pass(source, username, password)
        console.print(f'New username and password set!', style="blue")

    def change_password_of_source(self):
        all_sources = self.pm.get_all_available_sources()
        if not all_sources:
            console.print("There is no previously set password!", style="bold red")
            return
        source = Prompt.ask(
            "Choose a source",
            choices=all_sources,
        )
        username = Prompt.ask("New username")
        password = self._new_password_prompt()
        self.pm.update_previous_password(source, username, password)
        console.print(f'Username and password for source {source} updated successfully!', style="blue")

    def change_master_password(self):
        is_acceptable = False
        user_manager = None
        old_password = None
        while not is_acceptable:
            old_password = pwinput.pwinput(prompt="Enter your current password: ")
            user_manager = UserManager(self.user, old_password, self.db, persist=False)
            if user_manager.check_pass():
                is_acceptable = True
            else:
                console.print("Password is wrong!", style="bold red")
        new_password = self._new_password_prompt("Enter your new Master Password: ")
        user_manager.set_new_password(old_password, new_password)
        console.print(f'Master password updated successfully!', style="blue")


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
    console_app = ConsoleApp()
    console_app.run()
