from flask import Flask
from flask_login import LoginManager
from database.user_database import UserDatabase
from .models import User
from flask_mail import Mail, Message
from oauthlib.oauth2 import WebApplicationClient

user_db = UserDatabase = UserDatabase()
GOOGLE_CLIENT_ID = "133654944932-7jp5imq4u3k6ng5r8k9suue3rckcsdcf.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "zSWURv4KexNnOvRRP2tDQZX2"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

def create_app():
    app = Flask(__name__)
    client = WebApplicationClient(GOOGLE_CLIENT_ID)
    mail = Mail(app)
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'fitnessu.app@gmail.com'
    app.config['MAIL_PASSWORD'] = 'fitnessyass'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)
    msg = Message('Hello', sender = 'fitnessu.app@gmail.com', recipients = ['iamderekr@gmail.com'])
    msg.body = "Hello Flask message sent from Flask-Mail"
    #mail.send(msg)
    app.config['SECRET_KEY'] = "jfkldfj"
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(username):
        user_values = user_db.get_user(username)
        current_user = User(user_values[0], user_values[1], user_values[2], user_values[3], user_values[4], user_values[5], user_values[6])
        return current_user
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    return app
