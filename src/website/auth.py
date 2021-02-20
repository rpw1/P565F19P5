from flask import Blueprint, render_template, request
import sqlite3
import user_database as udb

auth = Blueprint("auth", __name__)
database = "/src/database/test_user_sqlite.db"

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
        if password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            conn = sqlite3.connect(database)
            udb.insert_user(username, password, f_name, l_name, email, 1)       
    return render_template("register.html")