#app

import os
from flask import Flask,redirect, request, render_template, session
from flask_session import Session
from tempfile import mkdtemp

from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import login_required, validCharPass, validLenPass, validEmail
from email_validator import validate_email

# configure application
app = Flask(__name__)

# make templates auto-reload
app.config["TEMPLATES_AUTO_RELOAD"] = True

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///keeptrack.db")

@app.after_request
def after_request(response):
    # ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # log user in

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return ("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return ("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    # log user out

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        # get input from user
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmationpassword")

        # check input is not null
        # create an apology message for each and render it
        apologymsg = ""
        if not username and not email and not password and not confirmation:
            apologymsg = "all fields are required"
            return render_template("signup.html", apologymsg=apologymsg.capitalize())
        if not username:
            apologymsg = "must provide username"
            return render_template("signup.html", apologymsg=apologymsg.capitalize())
        if not email:
            apologymsg = "must provide email"
            return render_template("signup.html", apologymsg=apologymsg.capitalize())
        if not validate_email(email):
            apologymsg = "invalid email format"
            return render_template("signup.html", apologymsg=apologymsg.capitalize())
        if not password:
            apologymsg = "must provide password"
            return render_template("signup.html", apologymsg=apologymsg.capitalize())
        # check pass lenght and char
        if not validLenPass(password) or not validCharPass(password):
            apologymsg = "password must be at least 8 char long and include at least 1 digits, 1 letter, 1 capital letter and 1 special char among @!#$%^&*?,:"
            return render_template("signup.html", apologymsg=apologymsg.capitalize())
        if not confirmation:
            apologymsg = "must provide confirmation"
            return render_template("signup.html", apologymsg=apologymsg.capitalize())
        if not password == confirmation:
            apologymsg = "password and confirmation must match"
            return render_template("signup.html", apologymsg=apologymsg.capitalize())
        
        # check username and email are not already used
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) >= 1:
            apologymsg = "username not available"
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(rows) >= 1:
            apologymsg = "email already used"
        
        # create the account
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", username, email, hash)  

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("signup.html")