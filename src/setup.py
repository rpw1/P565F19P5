from website import create_app
import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

app = create_app()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app.config.from_object(os.environ.get("APP_SETTINGS"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from src.database.user_database import UserDatabase

print(os.environ.get("APP_SETTINGS"))
if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")