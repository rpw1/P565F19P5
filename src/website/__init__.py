from flask import Flask
from flask_login import LoginManager
from database.dynamo_user_database import LoginDatabase
from .models import User
from flask_mail import Mail, Message
from oauthlib.oauth2 import WebApplicationClient
from flask_dynamo import Dynamo

user_db = LoginDatabase()
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
    def load_user(user_id):
        user_values = user_db.get_user(user_id)
        current_user = User(
            user_values['email'], user_values['user_id'], user_values['password'], user_values['first_name'], user_values['last_name'], user_values['role'], user_values['image']
            )
        return current_user
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    return app
