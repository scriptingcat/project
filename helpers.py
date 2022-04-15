# helpers for main app.py
import os
import requests
import urllib.parse
from flask import redirect, render_template, request, session
from functools import wraps

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