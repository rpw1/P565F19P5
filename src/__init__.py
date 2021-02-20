from website import create_app
from database.user_database import UserDatabase
import sys

print(sys.path)

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)