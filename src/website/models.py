from flask_login import UserMixin

from src.database.user_database import UserDatabase
class User:

    def __init__(self, email, password, first_name, last_name, role):
        super().__init__()
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role
    

    def is_authenticated(self):
        udb = UserDatabase()
        user_values = udb.query_user(self.email)
        if 'password' in user_values:
            return user_values['password'] == self.password
        else:
            return False

    def is_active(self):
        return self.is_authenticated

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email

    def get_role(self):
        return self.role

    def get_first_name(self):
        return self.first_name

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

