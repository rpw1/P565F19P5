from flask_login import UserMixin

from database.user_database import UserDatabase
class User:

    def __init__(self, username : str, password : str, f_name : str, l_name : str, email : str, role : int):
        super().__init__()
        self.username = username
        self.password = password
        self.f_name = f_name
        self.l_name = l_name
        self.email = email
        self.role = role
    

    def is_authenticated(self):
        udb = UserDatabase()
        user_values = udb.get_user(self.username)
        return user_values[1] == self.password

    def is_active(self):
        return self.is_authenticated

    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.username

    def get_email(self):
        return self.email
