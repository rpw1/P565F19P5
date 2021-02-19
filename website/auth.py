from flask import Blueprint, render_template, request

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            #add
            pass
    return render_template("register.html")