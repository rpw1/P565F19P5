from website import create_app
import os

app = create_app()
app.config.from_object(os.environ['APP_SETTINGS'])
print(os.environ['APP_SETTINGS'])
if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")