from src.website import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc", port=33507)