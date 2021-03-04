import requests, uuid, json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from src.database.user_database import UserDatabase
from user import User
from flask_login import login_user, login_required, logout_user, current_user
from decouple import config
from oauthlib.oauth2 import WebApplicationClient

user_db = UserDatabase()
auth = Blueprint("register", __name__)
roles = ['client', 'fitness_professional', 'admin']

# make these an environment variable
admin_password = "P5F21$"
GOOGLE_CLIENT_ID = "133654944932-7jp5imq4u3k6ng5r8k9suue3rckcsdcf.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "zSWURv4KexNnOvRRP2tDQZX2"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        acc_type = int(request.form.get("type"))
        google_login = int(request.form.get("google_login"))
        role = roles[acc_type]
        if google_login == 1 and role != roles[2]:
            return redirect(url_for("register.google_login"))
        if role == roles[0]:
            return redirect(url_for("register.client_register"))
        elif role == roles[1]:
            return redirect(url_for("register.fitness_professional_register"))
        else:
            return redirect(url_for("register.admin_register"))
    return render_template('role_registration')

@auth.route("/client_register", methods=["GET", "POST"])
def client_register():
    if request.method == "POST":
        email = request.form.get("email")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        gender = request.form.get("gender")
        user = user_db.get_client(email)
        if user:
            flash("E-mail already in use", category="error")
        elif password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            user_db.insert_client(email, generate_password_hash(password, method="sha256"), f_name, l_name, gender)    
            current_user = User(email, generate_password_hash(password, method="sha256"), f_name, l_name)
            login_user(current_user, remember=True)
            return redirect(url_for("views.home"))
    return render_template("client_register.html")

@auth.route("/fitness_professional_register", methods=["GET", "POST"])
def fitness_professional_register():
    if request.method == "POST":
        email = request.form.get("email")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        gender = request.form.get("gender")
        location = request.form.get("location")
        user = user_db.get_fitness_professional(email)
        if user:
            flash("E-mail already in use", category="error")
        elif password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            user_db.insert_fitness_professional(email, generate_password_hash(password, method="sha256"), f_name, l_name, gender, location)    
            current_user = User(email, generate_password_hash(password, method="sha256"), f_name, l_name)
            login_user(current_user, remember=True)
            return redirect(url_for("views.home"))
    return render_template("fitness_professional_register.html")


@auth.route("/admin_register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        email = request.form.get("email")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        gender = request.form.get("gender")
        admin_password = request.form.get("admin_password")
        if admin_password != config("ADMIN_PASSWORD"):
            flash("Admin password is incorrect, please try again", category="error")
        user = user_db.get_admin(email)
        if user:
            flash("E-mail already in use", category="error")
        elif password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            user_db.insert_admin(email, generate_password_hash(password, method="sha256"), f_name, l_name, gender)    
            current_user = User(email, generate_password_hash(password, method="sha256"), f_name, l_name)
            login_user(current_user, remember=True)
            return redirect(url_for("views.home"))
    return render_template("admin_register.html")


@auth.route("/google_register/<role>")
def google_register(role):
    google_provider_cfg = requests.get(config("GOOGLE_DISCOVERY_URL")).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    client = WebApplicationClient(config("GOOGLE_CLIENT_ID"))
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback/" + roles[role],
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth.route("/google_register/callback/<role>")
def google_register_callback(role):
    code = request.args.get("code")
    google_provider_cfg = requests.get(config("GOOGLE_DISCOVERY_URL")).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    client = WebApplicationClient(config("GOOGLE_CLIENT_ID"))
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(config("GOOGLE_CLIENT_ID"), config("GOOGLE_CLIENT_SECRET")),
    )       
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers = headers, data = body)
    if userinfo_response.json().get("email_verified"):
        u_id = userinfo_response.json()["sub"]
        email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        first_name = userinfo_response.json()["given_name"]
        last_name = userinfo_response.json()["family_name"]
    else:
        flash("Google Login invalid", category="error")
        redirect(url_for("auth.login"))
    if len(user_db._get_user(email, role)) == 0:
        password = generate_password_hash(str(uuid.uuid4()), method="sha256")
        if role == roles[0]:
            user_db.insert_client(email, password, first_name, last_name, image = picture)
        elif role == roles[0]:
            user_db.insert_fitness_professional(email, password, first_name, last_name, image = picture)
        else:
            flash("Error: you cannot sign in with google for a admin", category="error")
            return render_template('role_registration')
    else:
        flash("Account already created, logging you in")
    current_user = User(email, password, first_name, last_name)
    login_user(current_user, remember=True)
    return redirect(url_for("views.home"))