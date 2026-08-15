from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Quiz Cloner Userbot is running", 200
