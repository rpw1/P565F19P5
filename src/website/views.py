from flask import Flask, Blueprint, redirect, url_for, render_template, request, flash
from flask_login import login_required, current_user
from database.user_database import UserDatabase
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
import uuid

views = Blueprint("views", __name__)
user_db = UserDatabase()

@views.route("/")
#@login_required
def home():
    if current_user.is_authenticated:
        return render_template("dashboard.html", user=current_user)
    else: 
        return redirect(url_for("auth.login"))

if __name__ == "__main__":
    app.run(debug=True)

@views.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@views.route("/user/<id>")
@login_required
def user_page(id):
    user_values = user_db.query_user(id)
    if user_values:
        profile_user = User(
                user_values['email'], user_values['password'], user_values['first_name'], user_values['last_name'], user_values['role']
                )
        return render_template("profile.html", user=profile_user)
    else:
        flash("That user does not exist!", category="error")
        return redirect(url_for("views.home"))

@views.route("/content/<id>")
@login_required
def content(id):
    return render_template("content.html", id=id)

@views.route("/upload")
def upload():
    return render_template("upload.html")

@views.route("/update_password", methods=["GET","POST"])
@login_required
def update_password():
    if request.method == "POST":
        new_password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = current_user.get_id()
        password = generate_password_hash(new_password, method="sha256")
        if new_password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            user_db.update_password(email, password)
            flash("Password successfully changed!", category="success")
    return render_template("update_password.html", user=current_user)