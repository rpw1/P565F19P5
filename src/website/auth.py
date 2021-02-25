from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.user_database import UserDatabase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
import duo_web, json

auth = Blueprint("auth", __name__)
user_db = UserDatabase = UserDatabase()
i_key = ""
s_key = ""
a_key = ""

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_values = user_db.get_user(username)
        if user_values:
            current_user = User(user_values[0], user_values[1], user_values[2], user_values[3], user_values[4], user_values[5])
            if check_password_hash(user_db.get_password(username), password):
                # login_user(current_user, remember=True)
                keys = json.load(open("duo_keys.json"))
                i_key = keys["i-key"]
                s_key = keys["s-key"]
                a_key = keys["a-key"]
                signal_request = duo_web.sign_request(i_key, s_key, a_key, username)
                # if authenticated_username:
                #     flash("Logged in successfully!", category="success")
                # return(redirect(url_for("views.home")))
                # else:
                #     flash("Duo login was not successful")
                return redirect(url_for("auth.duo_login", sig_request = signal_request))
            else:
                print(user_db.get_password(username))
                flash("Incorrect password")
        else:
            flash("No user exists with that username")
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
        user = user_db.get_user(username)
        if user:
            flash("Username already in use", category="error")
        elif password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            user_db.insert_user(username, generate_password_hash(password, method="sha256"), f_name, l_name, email, acc_type)    
            print(user_db.get_user(username))
            current_user = User(username, generate_password_hash(password, method="sha256"), f_name, l_name, email, acc_type)
            login_user(current_user, remember=True)
            return redirect(url_for("views.home"))
    return render_template("register.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/reset", methods=["GET","POST"])
def reset():
    return render_template("reset.html")

@auth.route("/reset/<key>", methods=["GET", "POST"])
def reset_key(key):
    return key

@auth.route("/duo/<sig_request>", methods=["GET","POST"])
def duo_login(sig_request):
    return render_template("duo.html", sig_request = sig_request)