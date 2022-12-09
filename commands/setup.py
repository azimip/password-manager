import sqlite3


def setup(name):
    connection = sqlite3.connect(f'../{name}.db')
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE users (username TEXT PRIMARY KEY, password TEXT, old_passwords TEXT)")
    cursor.execute("CREATE TABLE passwords (user TEXT, source TEXT, username TEXT, password TEXT)")


if __name__ == "__main__":
    setup('password_manager')
