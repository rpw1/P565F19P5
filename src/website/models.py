from flask_login import UserMixin

from database.user_database import UserDatabase
class User:

    def __init__(self, username : str, password : str, f_name : str, l_name : str, email : str, role : int):
        super().__init__()
        self.username : str = username
        self.password : str = password
        self.f_name : str = f_name
        self.l_name : str = l_name
        self.email : str = email
        self.role : int = role
    

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
