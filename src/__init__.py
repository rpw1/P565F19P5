from website import create_app
from database.user_database import UserDatabase

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')