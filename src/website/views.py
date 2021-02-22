from flask import Flask, Blueprint, redirect, url_for, render_template
from flask_login import login_required

views = Blueprint("views", __name__)

@views.route("/")
@login_required
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
