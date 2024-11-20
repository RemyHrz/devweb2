from functools import wraps
from flask import request, session, redirect, flash
from models import db, User
import uuid

def flash_error(txt):
    return flash_message(txt, "alert-danger")

def flash_success(txt):
    return flash_message(txt, "alert-success")

def flash_message(txt, alert_type):
    return """<div class="d-inline-block alert """ + alert_type + """ alert-dismissible fade show" role="alert">
  """+txt+"""<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>"""

def logged_in(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if 'username' in session:
            username = session['username']
            user = User.query.filter(User.username==username).first()
            if user:
                return f(*args, **kwargs)
            else:
                return redirect("/logout")
        else:
            return redirect("/")
    return decorated_func

def if_session(f):
    @wraps(f)
    def decorated_func(*args,**kwargs):
        if session:
            return f(*args,**kwargs)
        else:
            session["session_id"]=uuid.uuid1()
            session.permanent=True
            return f(*args,**kwargs)
    return decorated_func

def get_visit_count(username):
    user = User.query.filter(User.username==username).first()
    visit = user.visits
    return visit

def visit_counter(username):
    user = User.query.filter(User.username==username).first()
    user.visits+=1
    db.session.commit()

def process_form():
    username = request.form["username"].strip()
    try:
        email = request.form["email"].strip()
    except:
        password = request.form["password"]
        return username, password
    try:
        password = request.form["password"]
    except:
        return username, email
    return username, password, email

def create_account():
    username, password, email = process_form()
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(flash_success("Votre compte a été créé"))

def check_account():
    username, email, none = process_form()
    user = User.query.filter(User.username==username).first()
    mail = User.query.filter(User.email==email).first()
    if user or mail:
        flash(flash_error("Ce nom d'utilisateur ou cette adresse mail est déja utilisée!"))
        return redirect("/")

def check_login():
    username, password = process_form()
    user = User.query.filter(User.username==username).first()
    if user and user.check_password(password):
        session["username"]=username
        session["email"]=user.email
        visit_counter(username)
        session.permanent=True
        flash(flash_success("connexion réussie"))
    else:
        flash(flash_error("Le mot de passe est incorrect"))