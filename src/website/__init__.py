from flask import Flask
from flask_login import LoginManager
from database.user_database import UserDatabase
from .models import User

user_db = UserDatabase = UserDatabase()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "jfkldfj"
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(username):
        user_values = user_db.get_user(username)
        current_user = User(user_values[0], user_values[1], user_values[2], user_values[3], user_values[4], user_values[5])
        return current_user
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    return app
