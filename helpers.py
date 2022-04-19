# helpers for main app.py
import os
import requests
import urllib.parse
from flask import redirect, render_template, request, session
from flask_mail import Mail, Message
from functools import wraps
# library to create token
from itsdangerous import Serializer


# from finance pset9
# ensure user is already logged in
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# check password is 8 digits min
def validLenPass(password):
    if len(password) > 7:
        return True
    return False

# check password contains at least 1 letter, 1 capital letter, 1 digit, 1 special char
def validCharPass (password):
    specialchar = ["@","!", "#", "$", "%","^", "&", "*", "?", "|", ":"]
    alpha= 0
    capital = 0
    digit = 0
    special = 0
    for char in password:
        if char.isalpha():
            alpha += 1
        if char.isupper():
            capital += 1
        if char.isdigit():
            digit += 1
        if char in specialchar:
            special += 1
        if alpha >= 1 and capital >= 1 and digit >= 1 and special >= 1:
            return True
    return False

# func to generate a token
def  generate_token(id, valid_sec=1800):
    serialized = Serializer(app.config['SECRET_KEY'], expires_in=valid_sec)
    return serialized.dump({'user_id': id}).decode('utf-8')

# func to verify token validation
def verify_token(token):
    serialized = Serializer(app.config['SECRET_KEY'], expires_in=1800)
    user_id = serialized.loads(token)['user_id']
    if user_id <= 0:
        return None
    return user_id

# func to send email
def send_reset_email(id, email):
    # create a token
    token = generate_token(id)
    # create an email object, sender and recipient 
    msg = Message('Reset Your Password', sender = 'appkeeptrack@gmail.com, recipients=[email]')
    # create body of email
    msg.body = '''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)} 
    If you did not make this request, please ignore this message.
    '''
    # send email
    mail.send(msg)
    return