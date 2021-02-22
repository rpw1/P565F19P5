from flask import Flask, Blueprint, redirect, url_for, render_template

views = Blueprint("views", __name__)

@views.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
