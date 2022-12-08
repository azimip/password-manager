from random import randint


class PMUser:
    def __init__(self, username):
        self.password = None
        self.id = randint(0, 100000000)  # change to uuid
        self.username = username

    def set_password(self, password):
        self.password = password


class PasswordManager:
    def __init__(self, user: PMUser):
        self.user = user
        self.sources = {}

    def get_user_pass(self, source):
        user_pass = self.sources.get(source, None)
        if not user_pass:
            raise Exception("Source does not exist")
        user = user_pass[0]
        password = user_pass[1].get_latest_password()
        return user, password

    def set_new_user_pass(self, source, username, password):
        if self.sources.get(source):
            raise Exception("Source already exists")
        password_object = Password()
        password_object.set_password(password)
        self.sources[source] = (username, password_object)

    def update_password(self, source, password):
        user_pass = self.sources.get(source, None)
        if not user_pass:
            raise Exception("Source does not exist")
        password_object = user_pass[1].set_password(password)
        self.sources[source] = (user_pass[0], password_object)


class Password:
    def __init__(self):
        self._passwords = []

    def get_latest_password(self):
        return self._passwords[0]

    def set_password(self, password):
        self._passwords.append(password)


if __name__ == '__main__':
    pass
