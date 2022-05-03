# helpers for main app.py
import os
import requests
from cs50 import SQL
import datetime

# library to create url
import urllib.parse
from urllib.parse import urljoin

from flask import Flask, redirect, render_template, request, session
from flask_mail import Mail, Message
from functools import wraps

# library to create jwt token 
import jwt

# library to conver img into a string
import base64

# configure application
app = Flask(__name__)

app.config['MAIL_DEFAULT_SENDER'] = os.environ["MAIL_DEFAULT_SENDER"]
app.config['MAIL_PASSWORD'] = os.environ["MAIL_PASSWORD"]
app.config['MAIL_PORT'] = 587
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ["MAIL_USERNAME"]
mail=Mail(app)

# configure private key
SECRET = os.environ['SECRET']


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///keeptrack.db")


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
def generate_token(payload_data):
    token = jwt.encode(payload=payload_data,key=SECRET)
    return token

# func to verify token validation
def verify_token(token): 
    # token is passed as string but needs to be bytes to be decoded as jwt object
    token = bytes(token, 'utf-8')
    payload_data = jwt.decode(jwt=token, key=SECRET, algorithm='HS256')
    user_id = payload_data['id']
    return user_id

# func to create an url
def createforgotpassurl(token):
    # take the url and join the token
    # token is bytes class so needs to be decoded to be joined
    url = urljoin('http://127.0.0.1:5000/resetpassword','?validation='+ token.decode('utf-8'))
    print(url)
    return url


# func to send email 
def send_reset_email(id, email):
    payload_data = {
        "id": id,
        "email": email,
        # to give an expiration in 300 seconds from the creation
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=300)
    }

    # create a token
    token = generate_token(payload_data)
    # create url
    url = createforgotpassurl(token)
    # create an email object, sender and recipient 
    msg = Message('Reset Your Password', sender = 'MAIL_DEFAULT_SENDER', recipients=[email])
    # create body of email
    msg.body = f'To reset your password, visit the following link: \n{url}\nIf you did not make this request, please ignore this message.'
    # send email
    mail.send(msg)
    token = token.decode('utf-8')
    return token

#func to insert/update the token in db not to make accessible once password has been changed but the token has not expired yet
def insert_token_in_db(user_id, token, tokentype):
    rows = db.execute("SELECT * FROM tokens WHERE user_id=? AND type=?", user_id, tokentype)
    status = 'active'
    if len(rows) <= 0:
        db.execute("INSERT INTO tokens (user_id, token, type, status) VALUES (?,?,?,?)", user_id, token, tokentype, status)
    else:
        db.execute("UPDATE tokens SET token=?, status=? WHERE user_id=?", token, status, user_id)
    return

# func to change status of token when password is successfully reset
def expire_token_status_in_db(user_id, token):
    status = 'expired'
    rows = db.execute("SELECT * FROM tokens WHERE user_id=? AND token=?", user_id, token)
    db.execute("UPDATE tokens SET status=? WHERE user_id=? AND token=?", status, user_id, token)
    return

#func to check token status in db
def check_token_status(user_id, token, tokentype):
    rows = db.execute("SELECT * FROM tokens WHERE user_id=? AND token=?", user_id, token)
    status = rows[0]['status']
    return status

# func to convert img into a string to save in db
def imgtostr(img):
    with open(img, "rb") as file:
        imageinstr = base64.b64encode(file.read())
    return imageinstr

#func to create a new list in db
def addlist(nametable, namelist,user_id):
    # take the id from table of all types of list
    rows = db.execute("SELECT * FROM list_types WHERE nametable=?", nametable)
    list_type_id = rows[0]['id']
    # insert the element
    db.execute("INSERT INTO lists (user_id,list_type_id,namelist) VALUES (?,?,?)", user_id, list_type_id, namelist)
    return 

#func to delete a list from db
def deletelist(nametable, namelist,user_id):
    # take the id from table of all types of list
    rows = db.execute("SELECT * FROM list_types WHERE nametable=?", nametable)
    list_type_id = rows[0]['id']
    rows2 = db.execute("SELECT * FROM lists WHERE user_id=? AND list_type_id=? AND namelist=?")
    id = rows2[0]['id']
    # delete the list from lists
    db.execute("DELETE FROM lists WHERE id=?", id)
    # return the lists(id) in order to delete its elements from the specific table
    return lists_id

# func to delete list's elements
def deleteelements(nametable, lists_id):
    #delete elements
    db.execute("DELETE FROM ? WHERE id=?", nametable, lists_id)
    return 

#func to add a new element to list in db
def add_element_movies_tvseries(nametable,namelist,lists_id,user_id,title,year,director,description,cover,link,note):
    db.execute("BEGIN TRANSACTION")
    # insert the element
    db.execute("INSERT INTO movies_tvseries (namelist,lists_id,user_id,title,year,director,description,cover,link,note) VALUES (?,?,?,?,?,?,?,?,?,?)",namelist,lists_id, user_id,title,year,director,description,cover,link,note)
    db.execute("COMMIT")
    return 

# func to check input
def checkinput(input):
    if input == None:
        input == 'null'
    return input

#CREATE TABLE lists (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER,list_type_id INTEGER, namelist TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (list_type_id) REFERENCES list_types(id));

#CREATE TABLE movies_tvseries (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, lists_id INTEGER, user_id INTEGER, title TEXT NOT NULL, year VARCHAR(4), director TEXT, description TEXT, cover TEXT, link TEXT, note TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (lists_id) REFERENCES lists(id));

#CREATE TABLE books (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, list_type_id INTEGER, user_id INTEGER, title TEXT NOT NULL, year VARCHAR(4), author TEXT, description TEXT, cover TEXT, link TEXT, note TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (list_type_id) REFERENCES list_types(id));
#CREATE TABLE places (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, list_type_id INTEGER, user_id INTEGER, place TEXT NOT NULL, address TEXT, coordinates TEXT, description TEXT, image TEXT, note TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (list_type_id) REFERENCES list_types(id));
#CREATE TABLE shopping (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, list_type_id INTEGER, user_id INTEGER, item TEXT NOT NULL, brand TEXT, collection TEXT, quantity INTEGER, price FLOAT, description TEXT, image TEXT, wheretobuy TEXT, note TEXT, status CHECK(status in ('to buy', 'bought')), FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (list_type_id) REFERENCES list_types(id));
