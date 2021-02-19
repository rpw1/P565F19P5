import pytest
from database.user_database import UserDatabase

user_database : UserDatabase = UserDatabase()
user_database.db_file = "src/database/sqlite/db/test_user_sqlite.db"

user_value1 : tuple = ("user1", "password123", "Joe", "LAstName", 1,)
user_value2 : tuple = ("user1", "password", "Joe", "LAstName", 2,)
user_value3 : tuple = ("user2", "password123", "Joe", "LAstName", 1,)
user_value4 : tuple = ("user3", "password", "Joe", "LAstName", 2,)
user_value5 : tuple = ("user4", "123", "Joe", "LAstName", 3,)
user_value6 : tuple = ("user5", "1234", "Joe", "LAstName", 3,)
user_value7 : tuple = (None, "1234", "Joe", "LAstName", 3,)
user_value8 : tuple = ("user6", None, "Joe", "LAstName", 3,)
user_value9 : tuple = ("user7", "1234", "Joe", "LAstName", None,)

def test_initial_values():
    assert user_database.db_file == "src/database/sqlite/db/test_user_sqlite.db"
    assert user_database.conn == None

def test_check_database():
    assert user_database.check_database() == True

def test_insert_user():
    assert user_database.insert_user(user_value1[0], user_value1[1], user_value1[2], user_value1[3], user_value1[4]) == True
    assert user_database.insert_user(user_value2[0], user_value2[1], user_value2[2], user_value2[3], user_value2[4]) == False
    assert user_database.insert_user(user_value3[0], user_value3[1], user_value3[2], user_value3[3], user_value3[4]) == True
    assert user_database.insert_user(user_value4[0], user_value4[1], user_value4[2], user_value4[3], user_value4[4]) == True
    assert user_database.insert_user(user_value5[0], user_value5[1], user_value5[2], user_value5[3], user_value5[4]) == True
    assert user_database.insert_user(user_value6[0], user_value6[1], user_value6[2], user_value6[3], user_value6[4]) == True
    assert user_database.insert_user(user_value7[0], user_value7[1], user_value7[2], user_value7[3], user_value7[4]) == False
    assert user_database.insert_user(user_value8[0], user_value8[1], user_value8[2], user_value8[3], user_value8[4]) == False
    assert user_database.insert_user(user_value9[0], user_value9[1], user_value9[2], user_value9[3], user_value9[4]) == False

def test_get_user():
    assert user_database.get_user(user_value1[0]) == ("user1", "password123", "Joe", "LAstName", 1,)
    assert user_database.get_user(user_value2[0]) == ("user1", "password123", "Joe", "LAstName", 1,)
    assert user_database.get_user(user_value3[0]) == ("user2", "password123", "Joe", "LAstName", 1,)
    assert user_database.get_user(user_value4[0]) == ("user3", "password", "Joe", "LAstName", 2,)
    assert user_database.get_user(user_value5[0]) == ("user4", "123", "Joe", "LAstName", 3,)
    assert user_database.get_user(user_value6[0]) == ("user5", "1234", "Joe", "LAstName", 3,)
    assert user_database.get_user(user_value7[0]) == None
    assert user_database.get_user(user_value8[0]) == None
    assert user_database.get_user(user_value9[0]) == None

def test_update_user():
    assert user_database.update_user(user_value1[0], "new password") == True
    assert user_database.update_user(user_value2[0], "new password2") == True
    assert user_database.update_user(user_value3[0], "new password") == True
    assert user_database.update_user(user_value4[0], "new password") == True
    assert user_database.update_user(user_value5[0], "new password") == True
    assert user_database.update_user(user_value6[0], "new password") == True
    # assert user_database.update_user(user_value7[0], "new password") == False
    # assert user_database.update_user(user_value8[0], "new password") == False
    # assert user_database.update_user(user_value9[0], "new password") == False

def test_remove_user():
    assert user_database.remove_user(user_value1[0]) == True
    #assert user_database.remove_user(user_value2[0]) == False
    assert user_database.remove_user(user_value3[0]) == True
    assert user_database.remove_user(user_value4[0]) == True
    assert user_database.remove_user(user_value5[0]) == True
    assert user_database.remove_user(user_value6[0]) == True
    # assert user_database.remove_user(user_value7[0]) == False
    # assert user_database.remove_user(user_value8[0]) == False
    # assert user_database.remove_user(user_value9[0]) == False