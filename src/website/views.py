from flask import Flask, Blueprint, redirect, url_for, render_template
from flask_login import login_required, current_user

views = Blueprint("views", __name__)

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