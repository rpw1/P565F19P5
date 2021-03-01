from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.dynamo_user_database import LoginDatabase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
import duo_web, json
from oauthlib.oauth2 import WebApplicationClient
import requests
import uuid
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import boto3
import secrets
import string
from decouple import config

user_db = LoginDatabase()
auth = Blueprint("auth", __name__)

GOOGLE_CLIENT_ID = "133654944932-7jp5imq4u3k6ng5r8k9suue3rckcsdcf.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "zSWURv4KexNnOvRRP2tDQZX2"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
client = WebApplicationClient(GOOGLE_CLIENT_ID)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_values = user_db.get_user(email)
        if user_values:
            current_user = User(
                user_values['email'], user_values['user_id'], user_values['password'], user_values['first_name'], user_values['last_name'], user_values['role'], user_values['image']
            )
            if check_password_hash(user_values['password'], password):
                signal_request = duo_web.sign_request(config('DUO_I_KEY'), config('DUO_S_KEY'), config('DUO_A_KEY'), email)
                return redirect(url_for("auth.duo_login", sig_request = signal_request))
            else:
                flash("Incorrect password")
        else:
            flash("No user exists with that username")
    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_id = str(uuid.uuid4())
        email = request.form.get("email")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        acc_type = int(request.form.get("type"))
        user = user_db.get_user(email)
        if user:
            flash("E-mail already in use", category="error")
        elif password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            user_db.insert_user(email, user_id, generate_password_hash(password, method="sha256"), f_name, l_name, acc_type, "image_string")    
            current_user = User(email, user_id, generate_password_hash(password, method="sha256"), f_name, l_name, acc_type, "image_string")
            login_user(current_user, remember=True)
            return redirect(url_for("views.home"))
    return render_template("register.html")

"""
@auth.route("/update_password", methods=["GET","POST"])
@login_required
def update_password():
    if request.method == "POST":
        new_password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = current_user.get_id()
        password = generate_password_hash(new_password, method="sha256")
        if password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            user_db.update_password(email, password)
    return render_template("update_password.html", user=current_user)
"""

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/reset", methods=["GET","POST"])
def reset():
    if request.method == "POST":
        recipient = request.form.get("email") 
        sender = 'thisbechildxd@gmail.com' #i should probably use the email for fitness U
        sender_name = 'Fitness U'
        user = user_db.get_user(recipient)

        if not user:
            flash("Account with this email does not exist", category="error")
            return render_template("reset.html")
        else:
            alphabet = string.ascii_letters + string.digits
            temp_password = ''.join(secrets.choice(alphabet) for i in range(20))
            password = generate_password_hash(temp_password, method="sha256")
            user_db.update_password(recipient, password)
            print(temp_password)
            body = """
                Hello this is a test

                -izzy """ + temp_password + """
            """
            try:
                s = smtplib.SMTP('email-smtp.us-east-2.amazonaws.com')
                s.connect('email-smtp.us-east-2.amazonaws.com', 587)
                s.starttls()
                s.login('AKIAUM4QIDHR43NBTQJQ','BO83F+jckoyDBHwX+/S568Wv5wJSOWQVqFXSFI7nIA+3')
                s.sendmail(sender, recipient, body)
                return render_template("password_reset.html")
            except Exception as e:
                flash("Error: unable to send email", category="error")
                print ("Error: unable to send email")
                return render_template("reset.html")
    return render_template("reset.html")

@auth.route("/reset/<key>", methods=["GET", "POST"])
def reset_key(key):
    return key

@auth.route("/duo/<sig_request>", methods=["GET","POST"])
def duo_login(sig_request):
    url_callback = url_for("auth.duo_callback")
    return render_template("duo.html", sig_request = sig_request, url_callback = url_callback)

@auth.route("/duo_callback", methods=["GET","POST"])
def duo_callback():
    if request.method == "POST":
        sig_response = request.form.get("sig_response")
        authenticated_username = duo_web.verify_response(config('DUO_I_KEY'), config('DUO_S_KEY'), config('DUO_A_KEY'), sig_response)
        if authenticated_username:
            user_values = user_db.get_user(authenticated_username)
            if user_values:
                current_user = User(
                user_values['email'], user_values['user_id'], user_values['password'], user_values['first_name'], user_values['last_name'], user_values['role'], user_values['image']
                )
                login_user(current_user, remember=True)
                flash("Logged in successfully!", category="success")
                return(redirect(url_for("views.home")))
            else:
                flash("User value was not equal to what is stored in the database")
        else:
            flash("Duo login was not successful")
    return render_template("login.html")

@auth.route("/google_login")
def google_login():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth.route("/google_login/callback")
def google_callback():
    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
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
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
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
    if not user_db.get_user(email):
        user_db.insert_user(email, u_id, str(uuid.uuid4()), first_name, last_name, 1, picture)    
    current_user = User(email, u_id, str(uuid.uuid4()), first_name, last_name, 1, picture)
    login_user(current_user, remember=True)
    return redirect(url_for("views.home"))

@auth.route("/google_login_role")
def google_role(u_id, email, first_name, last_name, unique_id):
    pass
    