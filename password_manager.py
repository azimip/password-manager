import sqlite3


class PMUser:
    def __init__(self, username, password, db):
        self.username = username
        self.password = password
        self.db = db
        self.db_cursor = self.db.get_cursor()
        self.persist()

    def persist(self):
        self.db_cursor.execute("INSERT INTO users VALUES (?, ?)", (self.username, self.password), )
        self.db.commit()


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

    # def update_password(self, source, password):
    #     user_pass = self.sources.get(source, None)
    #     if not user_pass:
    #         raise Exception("Source does not exist")
    #     password_object = user_pass[1].set_password(password)
    #     self.sources[source] = (user_pass[0], password_object)


class Password:
    def __init__(self):
        self._passwords = []

    def get_latest_password(self):
        return self._passwords[0]

    def set_password(self, password):
        self._passwords.append(password)


class ConsoleInterface:
    @staticmethod
    def get_input(is_int=False):
        raw_inp = input()
        if is_int:
            inp = int(raw_inp)
        else:
            inp = str(raw_inp)  # sanitize input
        return inp

    def run(self):
        print("Welcome to the Super Strong Password Manager!\nWhat can I do for you?")
        print("  1. Login\n  2. Create Account")
        choice = self.get_input(is_int=True)


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
    console_interface = ConsoleInterface()
    db = DBManager('password_manager')
    cursor = db.get_cursor()
    user = 'John'
    pm = PasswordManager(user, db)
    pm.set_new_user_pass('google', 'gagool', '12345')
    print(get_all_users(cursor))
    print(pm.get_all_available_sources())
    print(pm.get_user_pass('google'))
