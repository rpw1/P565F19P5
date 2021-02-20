import sqlite3
from sqlite3 import Error

class UserDatabase:
    """
    This classes manages the user database

    ...
    
    Attributes
    ---------
    db_file : str ->
        a constant variable for the path to the database \n
    conn : sqlite3.Connection
        a connection object to the user database
    
    Methods
    -------
    check_database() -> bool
        checks if the user database is created \n
    insert_user(username : str, password : str, role : int) -> bool
        adds the given user to the user database from their given username, encrypted password, and role \n
    get_user(username : str) -> tuple
        grabs the user from the user database from the given username \n
    remove_user(username : str) -> bool
        removes the user from the user database from the given username \n
    update_user(username : str, password : str) -> bool
        updates the user's password from their username

    """

    def __init__(self):
        self.db_file = "src/database/sqlite/db/user_sqlite.db"
        self.conn = sqlite3.Connection = None

    def check_database(self) -> bool:
        """
        Returns:
        ------------
        bool ->
            represents a successful(true) or an unsuccessful(false) connection to the database
        """
        successful_connection = True
        try:
            self.conn = sqlite3.connect(self.db_file)
            c = sqlite3.Cursor = self.conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS users (username text UNIQUE NOT NULL, password text NOT NULL, first_name text NOT NULL, last_name text NOT NULL, email text NOT NULL, role int NOT NULL)')
            self.conn.commit()
        except Error as e:
            print(e)
            successful_connection = False
        finally:
            c.close()
            return successful_connection

    def insert_user(self, username : str, password : str, f_name : str, l_name : str, email : str, role : int) -> bool:
        """
        Parameters
        ----------
        username : str ->
            username of the user \n
        password : str ->
            encrypted password of the user \n
        f_name : str -> 
            first name of the user \n
        l_name : str ->
            last name of the user \n
        email : str ->
            email of the user \n
        role: int ->
            role of the user either Client(1), Fitness Professional(2), Admin(3)

        Returns:
        --------
        bool ->
            represents a successful(true) or an unsuccessful(false) insertion to the database
        """

        if not self.check_database(): return False
        successful_insert = True
        try:
            c = sqlite3.Cursor = self.conn.cursor()
            user_values = (username, password, f_name, l_name, email, role,)
            c.execute("INSERT INTO users VALUES (?,?,?,?,?,?)", user_values)
            self.conn.commit()
        except Error as e:
            print(e)
            successful_insert = False
        finally:
            c.close()
            self.conn.close()
            return successful_insert

    def get_user(self, username : str) -> tuple:
        """
        Parameters
        ----------
        username : str ->
            username of the user
        
        Returns
        -------
        tuple ->
            user information from the database (returns None if not found)
        """
        if not self.check_database(): return tuple()
        c = sqlite3.Cursor = self.conn.cursor()
        search_parameters = (username,)
        c.execute('SELECT * FROM users WHERE username=?', search_parameters)
        fetched_user = c.fetchone()
        c.close()
        self.conn.close()
        return fetched_user

    def get_password(self, username : str) -> str:
        if not self.check_database(): return str()
        c = sqlite3.Cursor = self.conn.cursor()
        search_parameters = (username,)
        c.execute('SELECT password FROM users WHERE username=?', search_parameters)
        fetched_user = c.fetchone()
        c.close()
        self.conn.close()
        return fetched_user[0]

    def remove_user(self, username : str) -> bool:
        """
        Parameters
        ----------
        username : str ->
            username of the user
        
        Returns
        -------
        bool ->
            true if user successfully removed false otherwise
        """
        if not self.check_database(): return False
        successful_delete = True
        try:
            c = sqlite3.Cursor = self.conn.cursor()
            search_parameters = (username,)
            c.execute('DELETE FROM users WHERE username=?', search_parameters)
            self.conn.commit()
        except Error as e:
            print(e)
            successful_delete = False
        finally:
            c.close()
            self.conn.close()
            return successful_delete

    def update_user(self, username : str, password : str) -> bool:
        """
        Parameters
        ----------
        username : str ->
            username of the user \n
        password : str ->
            the updated encrypted password of the user
        
        Returns
        -------
        bool ->
            true if user's password successfully updated false otherwise
        """
        if not self.check_database(): return False
        successful_delete = True
        try:
            c = sqlite3.Cursor = self.conn.cursor()
            search_parameters = (password, username,)
            c.execute('UPDATE users SET password=? WHERE username=?', search_parameters)
            self.conn.commit()
        except Error as e:
            print(e)
            successful_delete = False
        finally:
            c.close()
            self.conn.close()
            return successful_delete