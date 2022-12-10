import json
import sqlite3

import pwinput
from rich import print as rprint
from rich.console import Console
from rich.prompt import Prompt
from rich.tree import Tree

from utils.aes import encrypt, decrypt
from utils.common_checker import is_common
from utils.hash import get_hash
from utils.similarity_checker import is_similar
from utils.strength_checker import is_strong

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
        self.db_cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (self.username, password_hash, json.dumps([])), )
        self.db.commit()

    def check_pass(self, password):
        real_pass_hash = \
            self.db_cursor.execute("SELECT password FROM users WHERE username = ?", (self.username,), ).fetchall()[0][0]
        return real_pass_hash == get_hash(password)

    def set_new_password(self, current_password, new_password):
        row = self.db_cursor.execute("SELECT password, old_passwords FROM users WHERE username = ?",
                                     (self.username,), ).fetchall()[0]
        current_password_hash = row[0]
        if current_password_hash != get_hash(current_password):
            raise Exception("Current password is wrong")

        old_password_hashes = json.loads(row[1])
        all_hashes = old_password_hashes + [current_password_hash]

        if is_common(new_password):
            raise Exception("New master password is a common password!")

        if is_similar(new_password, all_hashes):
            raise Exception("New master password is similar to one of the old master passwords!")

        if is_strong(new_password, all_hashes):
            raise Exception("New master password is not secure! The password must be at least 8 characters long"
            " and must have at least 1 special character and 1 number.")

        new_password_hash = get_hash(new_password)
        self.db_cursor.execute("UPDATE users SET password = ?, old_passwords = ? WHERE username = ?",
                               (new_password_hash, json.dumps(all_hashes), self.username), )
        self.db.commit()
        self.password = new_password


class PasswordManager:
    def __init__(self, um, db):
        self.um = um
        self.db = db
        self.db_cursor = self.db.get_cursor()

    def get_all_available_sources(self):
        sources = [row[0] for row in self.db_cursor.execute("SELECT source FROM passwords WHERE user = ?",
                                                            (self.um.username,), ).fetchall()]
        return sources

    def get_user_pass(self, source):
        user_pass = [(row[0], row[1]) for row in
                     self.db_cursor.execute("SELECT username, password FROM passwords WHERE user = ? and source = ?",
                                            (self.um.username, source), ).fetchall()]
        if not user_pass:
            raise Exception("Source does not exist")
        username = user_pass[0][0]
        password = decrypt(self.um.password, user_pass[0][1])
        return username, password

    def set_new_user_pass(self, source, username, password):
        sources = self.get_all_available_sources()
        if source in sources:
            raise Exception("Source already exists")
        encrypted_password = encrypt(self.um.password, password)
        self.db_cursor.execute("INSERT INTO passwords VALUES (?, ?, ?, ?)",
                               (self.um.username, source, username, encrypted_password), )
        self.db.commit()

    def update_previous_password(self, source, username, password):
        sources = self.get_all_available_sources()
        if source not in sources:
            raise Exception("Source is not available")
        encrypted_password = encrypt(self.um.password, password)
        self.db_cursor.execute("UPDATE passwords SET password = ?, username = ? WHERE user = ? and source = ?",
                               (encrypted_password, username, self.um.username, source), )
        self.db.commit()

    def update_password_encryptions(self, old_master_password, new_master_passwsord):
        sources = self.get_all_available_sources()
        for source in sources:
            password = self.db_cursor.execute("SELECT password FROM passwords WHERE user = ? and source = ?",
                                              (self.um.username, source), ).fetchall()[0][0]
            new_password = encrypt(new_master_passwsord, decrypt(old_master_password, password))
            self.db_cursor.execute("UPDATE passwords SET password = ? WHERE user = ? and source = ?",
                                   (new_password, self.um.username, source), )
            self.db.commit()


class ConsoleApp:
    def __init__(self):
        self.db = DBManager('password_manager')
        self.pm = None
        self.user = None
        self.um = None

    def run(self):
        self.welcome()
        choice = self.get_initial_choice()
        if choice == "1":
            self.user = self.login()
        if choice == "2":
            self.user = self.create_user()
        self.pm = PasswordManager(self.um, self.db)
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
        style1 = "blink bold yellow"
        console.rule(style="yellow")
        console.print("Welcome to the Super Strong Password Manager!", style=style1, justify="center")
        console.rule(style="yellow")

    @staticmethod
    def goodbye():
        style1 = "bold yellow"
        console.rule(style="yellow")
        console.print("Have a safe day!", style=style1, justify="center")
        console.rule(style="yellow")

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

        if is_common(password):
            raise Exception("The master password is a common password!")

        if not is_strong(password):
            raise Exception("The master password is not secure! The password must be at least 8 characters long"
            " and must have at least 1 special character and 1 number.")

        um = UserManager(username, password, self.db)
        self.um = um
        return username

    def login(self):
        username = None
        um = None
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
            um = UserManager(username, password, self.db, persist=False)
            if um.check_pass(password):
                is_acceptable = True
            else:
                console.print("Password is wrong!", style="bold red")
        self.um = um
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
            if len(password) > 1:
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
        console.print(f'Your username for {source} is:', style="yellow")
        console.print(username)
        console.print(f'Your password for {source} is:', style="yellow")
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
        console.print(f'New username and password set!', style="yellow")

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
        console.print(f'Username and password for source {source} updated successfully!', style="yellow")

    def change_master_password(self):
        is_acceptable = False
        old_password = None
        while not is_acceptable:
            old_password = pwinput.pwinput(prompt="Enter your current password: ")
            if self.um.check_pass(old_password):
                is_acceptable = True
            else:
                console.print("Password is wrong!", style="bold red")

        is_acceptable = False
        while not is_acceptable:
            new_password = self._new_password_prompt("Enter your new Master Password: ")
            try:
                self.um.set_new_password(old_password, new_password)
                is_acceptable = True
                self.pm.update_password_encryptions(old_password, new_password)
            except Exception as e:
                console.print(e, style="bold red")
        console.print(f'Master password updated successfully!', style="yellow")


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
