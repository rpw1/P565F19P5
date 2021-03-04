from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
import requests, json
from decouple import config
from oauthlib.oauth2 import WebApplicationClient
from src.database.user_database import UserDatabase


user_db = UserDatabase()
auth = Blueprint("login", __name__)
roles = ['client', 'fitness_professional', 'admin']

# make these an environment variable
GOOGLE_CLIENT_ID = "133654944932-7jp5imq4u3k6ng5r8k9suue3rckcsdcf.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "zSWURv4KexNnOvRRP2tDQZX2"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)



@auth.route("/google_login")
def google_login():
    google_provider_cfg = requests.get(config("GOOGLE_DISCOVERY_URL")).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    client = WebApplicationClient(config("GOOGLE_CLIENT_ID"))
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth.route("/google_login/callback")
def google_callback():
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
    if not user_db.get_user(email):
        password = generate_password_hash(str(uuid.uuid4()), method="sha256")
        user_db.insert_user(email, u_id, password, first_name, last_name, 1, picture)    
    current_user = User(email, u_id, password, first_name, last_name, 1, picture)
    login_user(current_user, remember=True)
    return redirect(url_for("views.home"))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))