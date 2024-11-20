from flask import Flask, render_template, request, redirect, session
import tomli
from datetime import timedelta
from models import db
from tools import logged_in, get_visit_count, check_account, check_login, create_account, if_session

app = Flask(__name__)

with open("config.toml", "rb") as file:
    config_secrets = tomli.load(file)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = config_secrets['SECRET_KEY']
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE']=True
app.config['SESSION_COOKIE_HTTPONLY']=True
app.config['SESSION_COOKIE_SAMESITE']='Lax'

db.init_app(app)

app.app_context().push()
with app.app_context():
    db.create_all()


@app.route("/", methods=["GET","POST"])
@if_session
def mainpage():
    if request.method == "POST":
        check_account()
        create_account()
        return redirect("/")
    else:
        try:
            username=session["username"]
            email=session["email"]
            visit_count=get_visit_count(username)
            return render_template("index.html", username=username, email=email, visit_count=visit_count)
        except:
            return render_template("index.html")

@app.route("/login", methods=["POST"])
def login_page():
    if request.method == "POST":
        check_login()
        return redirect("/")
    else:
        return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
	app.run(debug=True)
