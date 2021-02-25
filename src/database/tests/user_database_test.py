import pytest
from src.database.user_database import UserDatabase

user_database : UserDatabase = UserDatabase()
user_database.db_file = "src/database/sqlite/db/test_user_sqlite.db"

user_value1 : tuple = ("1", "user1", "password123", "Joe", "LAstName", "email", 1,)
user_value2 : tuple = ("1", "user1", "password", "Joe", "LAstName", "email1", 2,)
user_value3 : tuple = ("2", "user2", "password123", "Joe", "LAstName", "email2", 1,)
user_value4 : tuple = ("3", "user3", "password", "Joe", "LAstName", "email3", 2,)
user_value5 : tuple = ("4", "user4", "123", "Joe", "LAstName", "email4", 3,)
user_value6 : tuple = ("5", "user5", "1234", "Joe", "LAstName", "email5", 3,)
user_value7 : tuple = ("6", None, "1234", "Joe", "LAstName", "email6", 3,)
user_value8 : tuple = ("7", "user6", None, "Joe", "LAstName", "email7", 3,)
user_value9 : tuple = ("8", "user7", "1234", "Joe", "LAstName", "email8", None,)

def test_initial_values():
    assert user_database.db_file == "src/database/sqlite/db/test_user_sqlite.db"
    assert user_database.conn == None

def test_check_database():
    assert user_database.check_database() == True

def test_insert_user():
    assert user_database.insert_user(user_value1[0], user_value1[1], user_value1[2], user_value1[3], user_value1[4], user_value1[5], user_value1[6]) == True
    assert user_database.insert_user(user_value2[0], user_value2[1], user_value2[2], user_value2[3], user_value2[4], user_value2[5], user_value2[6]) == False
    assert user_database.insert_user(user_value3[0], user_value3[1], user_value3[2], user_value3[3], user_value3[4], user_value3[5], user_value3[6]) == True
    assert user_database.insert_user(user_value4[0], user_value4[1], user_value4[2], user_value4[3], user_value4[4], user_value4[5], user_value4[6]) == True
    assert user_database.insert_user(user_value5[0], user_value5[1], user_value5[2], user_value5[3], user_value5[4], user_value5[5], user_value5[6]) == True
    assert user_database.insert_user(user_value6[0], user_value6[1], user_value6[2], user_value6[3], user_value6[4], user_value6[5], user_value6[6]) == True
    assert user_database.insert_user(user_value7[0], user_value7[1], user_value7[2], user_value7[3], user_value7[4], user_value7[5], user_value7[6]) == False
    assert user_database.insert_user(user_value8[0], user_value8[1], user_value8[2], user_value8[3], user_value8[4], user_value8[5], user_value8[6]) == False
    assert user_database.insert_user(user_value9[0], user_value9[1], user_value9[2], user_value9[3], user_value9[4], user_value9[5], user_value9[6]) == False

def test_get_user():
    assert user_database.get_user(user_value1[1]) == ("1", "user1", "password123", "Joe", "LAstName", "email", 1,)
    assert user_database.get_user(user_value2[1]) == ("1", "user1", "password123", "Joe", "LAstName", "email", 1,)
    assert user_database.get_user(user_value3[1]) == ("2", "user2", "password123", "Joe", "LAstName", "email2", 1,)
    assert user_database.get_user(user_value4[1]) == ("3", "user3", "password", "Joe", "LAstName", "email3", 2,)
    assert user_database.get_user(user_value5[1]) == ("4", "user4", "123", "Joe", "LAstName", "email4", 3,)
    assert user_database.get_user(user_value6[1]) == ("5", "user5", "1234", "Joe", "LAstName", "email5", 3,)
    assert user_database.get_user(user_value7[1]) == None
    assert user_database.get_user(user_value8[1]) == None
    assert user_database.get_user(user_value9[1]) == None

def test_update_user():
    assert user_database.update_user(user_value1[1], "new password") == True
    assert user_database.update_user(user_value2[1], "new password2") == True
    assert user_database.update_user(user_value3[1], "new password") == True
    assert user_database.update_user(user_value4[1], "new password") == True
    assert user_database.update_user(user_value5[1], "new password") == True
    assert user_database.update_user(user_value6[2], "new password") == True

def test_remove_user():
    assert user_database.remove_user(user_value1[1]) == True
    assert user_database.remove_user(user_value3[1]) == True
    assert user_database.remove_user(user_value4[1]) == True
    assert user_database.remove_user(user_value5[1]) == True
    assert user_database.remove_user(user_value6[1]) == True