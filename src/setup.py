from website import create_app

app = create_app()

print("Add and argument after the file to specify which database you are using")
print("Don't an argument for production")
print("1 - Ryan's Database")
print("2 - Derek's Database")
print("3 - Ben's Database")
print("4 - Izzy's Database")

if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")