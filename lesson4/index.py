from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Hello, flask!</h1><p> firsit page</p>"


@app.route("user")
def user():
    return "<h1>user!</h1><p> second page</p>"

@app.route("product")
def product():
    return "<h1>product!</h1><p> third page</p>"

