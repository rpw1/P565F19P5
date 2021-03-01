from flask import Flask, Blueprint, redirect, url_for, render_template, request, flash
from flask_login import login_required, current_user
from database.dynamo_user_database import LoginDatabase
from werkzeug.security import generate_password_hash, check_password_hash

views = Blueprint("views", __name__)
user_db = LoginDatabase()

@views.route("/")
@login_required
def home():
    return render_template("index.html", user=current_user)

if __name__ == "__main__":
    app.run(debug=True)

@views.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

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
    return render_template("update_password.html", user=current_user)