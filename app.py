#app

import os
from flask import Flask,redirect, request, render_template, session
from flask_session import Session
from tempfile import mkdtemp
from flask_mail import Mail, Message


from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import login_required, validCharPass, validLenPass, generate_token, verify_token, send_reset_email, insert_token_in_db, expire_token_status_in_db, check_token_status
from email_validator import validate_email


# library to create jwt token 
import jwt

# configure application
app = Flask(__name__)

# make templates auto-reload
app.config["TEMPLATES_AUTO_RELOAD"] = True

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure session to use filesystem to send email
app.config['MAIL_DEFAULT_SENDER'] = os.environ["MAIL_DEFAULT_SENDER"]
app.config['MAIL_PASSWORD'] = os.environ["MAIL_PASSWORD"]
app.config['MAIL_PORT'] = 587
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ["MAIL_USERNAME"]
mail=Mail(app)


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
            apologymsg = "must provide username"
            return render_template("login.html", apologymsg=apologymsg.capitalize())


        # Ensure password was submitted
        elif not request.form.get("password"):
            apologymsg = "must provide username"
            return render_template("login.html", apologymsg=apologymsg.capitalize())

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            apologymsg = "invalid username and/or password"
            return render_template("login.html", apologymsg=apologymsg.capitalize())

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
        if len(rows) > 0:
            apologymsg = "username not available"
            return render_template("signup.html", apologymsg=apologymsg.capitalize())
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(rows) > 0:
            apologymsg = "email already used"
            return render_template("signup.html", apologymsg=apologymsg.capitalize())
        
        # create the account
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", username, email, hash)  
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        # remember which user has logged in
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("signup.html")

@app.route("/changepassword", methods=["GET","POST"])
@login_required
def changepassword():
    if request.method == "POST":
        currentpassword = request.form.get("currentpassword")
        newpassword = request.form.get("newpassword")
        confirmationpassword = request.form.get("confirmationpassword")

        # check input is not null
        # create an apology message for each and render it
        if not currentpassword and not newpassword and not confirmationpassword:
            apologymsg = "all fields are required"
            return render_template("changepassword.html", apologymsg=apologymsg.capitalize())
        if not currentpassword:
            apologymsg = "must insert your current password to be able to change it"
            return render_template("changepassword.html", apologymsg=apologymsg.capitalize())
        if not newpassword:
            apologymsg = "must provide a new password"
            return render_template("changepassword.html", apologymsg=apologymsg.capitalize())
        # check pass lenght and char
        if not validLenPass(newpassword) or not validCharPass(newpassword):
            apologymsg = "password must be at least 8 char long and include at least 1 digits, 1 letter, 1 capital letter and 1 special char among @!#$%^&*?,:"
            return render_template("changepassword.html", apologymsg=apologymsg.capitalize())
        if not confirmationpassword:
            apologymsg = "must provide confirmation"
            return render_template("changepassword.html", apologymsg=apologymsg.capitalize())
        if not newpassword == confirmationpassword:
            apologymsg = "new password and confirmation must match"
            return render_template("changepassword.html", apologymsg=apologymsg.capitalize())
        
        # select id info
        rows = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])
        # check it exists and current password is valid
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], currentpassword):
            apologymsg = "Invalid Current Password"
            return render_template("changepassword.html", apologymsg=apologymsg.capitalize())
        # change password
        hash = generate_password_hash(newpassword, method='pbkdf2:sha256', salt_length=8)
        db.execute("UPDATE users SET hash=? WHERE id=?", hash, session['user_id'])
        apologymsg = "Password successfully changed!"
        return render_template("changepassword.html", apologymsg=apologymsg)
    else:
        return render_template("changepassword.html")

@app.route("/forgotpassword", methods=["GET","POST"])
def requesttoken():
    # this is the route by which user requests token to change password
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")

        # check at least one field has been post
        if not username and not email:
            apologymsg = "must provide username or email"
            return render_template("forgotpassword.html", apologymsg=apologymsg)
        if not username:
            # handle exception from validate_email
            try:
                validate_email(email)
            except:
                apologymsg = "Invalid email"
                return render_template("forgotpassword.html", apologymsg=apologymsg)

            rows = db.execute("SELECT * FROM users WHERE email=?", email)
            if len(rows) <= 0:
                apologymsg = "email not found"
                return render_template("forgotpassword.html", apologymsg=apologymsg)
            id = rows[0]["id"]
            email = rows[0]["email"]
        else:
            rows = db.execute("SELECT * FROM users WHERE username=?", username)
            if len(rows) <= 0:
                apologymsg = "username not found"
                return render_template("forgotpassword.html", apologymsg=apologymsg)
            id = rows[0]["id"]
            email = rows[0]["email"]

        # send by email the token
        # func send_reset_email geneates token and sends via email
        # changes on db have to be commited together with sending email
        db.execute("BEGIN TRANSACTION")
        token = send_reset_email(id, email)
        tokentype = "resetpassword"
        insert_token_in_db(id, token, tokentype)
        db.execute("COMMIT")

        apologymsg = "Reset Password Request Sent"

        return render_template("forgotpassword.html", apologymsg=apologymsg)
    else:
        return render_template("forgotpassword.html")


@app.route('/resetpassword', methods=["GET","POST"])
def resetpassword():
    #reset the password

    if request.method == "GET":
        # take the query string
        token = request.args.get('validation')
        # if there is no query
        if not token:
            return redirect('/')
        else:
            # verify token is valid
            # try-except to handle error exception
            try:
                user_id = verify_token(token)
                # if it returns no user_id
                if user_id <= 0:
                    apologymsg = "No User associated with this Token"
                    return render_template("forgotpassword.html", apologymsg=apologymsg.capitalize())
                else:
                    # if it returns an user_id
                    # check token status in db to know whether it has already used or not to reset password
                    if check_token_status(user_id, token, "resetpassword") == "expired":
                        apologymsg = "Expired Token"
                        return render_template("forgotpassword.html", apologymsg=apologymsg.capitalize())
                    else:
                        return render_template("resetpassword.html", id=token)
            except:
                # if it returns an error, return to forgot password
                apologymsg = "Expired Token"
                return render_template("forgotpassword.html", apologymsg=apologymsg)

    # check request method
    if request.method == "POST":
        # handle exception from verifying token to get user_id back
        try:
            newpassword = request.form.get("newpassword")
            confirmationpassword = request.form.get("confirmationpassword")
            token = request.form.get("id")
            
            user_id = verify_token(token)

            # check input is not null
            # create an apology message for each and render it
            if not newpassword and not confirmationpassword:
                apologymsg = "all fields are required"
                return render_template("resetpassword.html", apologymsg=apologymsg.capitalize(), id=token)
            if not newpassword:
                apologymsg = "must provide a new password"
                return render_template("resetpassword.html", apologymsg=apologymsg.capitalize(), id=token)
            # check pass lenght and char
            if not validLenPass(newpassword) or not validCharPass(newpassword):
                apologymsg = "password must be at least 8 char long and include at least 1 digits, 1 letter, 1 capital letter and 1 special char among @!#$%^&*?,:"
                return render_template("resetpassword.html", apologymsg=apologymsg.capitalize(), id=token)
            if not confirmationpassword:
                apologymsg = "must provide confirmation"
                return render_template("resetpassword.html", apologymsg=apologymsg.capitalize(), id=token)
            if not newpassword == confirmationpassword:
                apologymsg = "new password and confirmation must match"
                return render_template("resetpassword.html", apologymsg=apologymsg.capitalize(), id=token)
            
            # select id info
            rows = db.execute("SELECT * FROM users WHERE id=?", user_id)
            # check id exists
            if len(rows) != 1:
                apologymsg = "Invalid Id"
                return render_template("resetpassword.html", apologymsg=apologymsg.capitalize())
            
            # change password
            # changes on db have to be commited together
            db.execute("BEGIN TRANSACTION")
            hash = generate_password_hash(newpassword, method='pbkdf2:sha256', salt_length=8)
            db.execute("UPDATE users SET hash=? WHERE id=?", hash, user_id)
            apologymsg = "Password successfully changed!"

            # make token expire 
            expire_token_status_in_db(user_id, token)
            db.execute("COMMIT")
            return render_template("login.html", apologymsg=apologymsg)
        except:
            # if it returns an error, return to forgot password
            apologymsg = "Expired Token"
            return render_template("forgotpassword.html", apologymsg=apologymsg)


# TODO
