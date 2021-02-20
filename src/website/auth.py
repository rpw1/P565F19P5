from flask import Blueprint, render_template, request
from database.user_database import UserDatabase
from cryptography.fernet import Fernet

auth = Blueprint("auth", __name__)
user_db = UserDatabase = UserDatabase()

@auth.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        acc_type = int(request.form.get("type"))
        if password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            pass
            user_db.insert_user(username, password, f_name, l_name, email, acc_type)    
            print(user_db.get_user(username))
    return render_template("register.html")