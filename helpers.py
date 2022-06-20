# helpers for main app.py
import os
import requests
from cs50 import SQL
import datetime

# library to create url
import urllib.parse
from urllib.parse import urljoin

from flask import Flask, redirect, render_template, request, session, send_file
from flask_mail import Mail, Message
from functools import wraps


# library to create jwt token 
import jwt

# library to conver img into a string
import base64
# library to conver str img into bytes
from io import BytesIO



# configure application
app = Flask(__name__)

mail_default_sender = os.environ["MAIL_DEFAULT_SENDER"]


app.config['MAIL_DEFAULT_SENDER'] = mail_default_sender
app.config['MAIL_PASSWORD'] = os.environ["MAIL_PASSWORD"]
app.config['MAIL_PORT'] = 587
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ["MAIL_USERNAME"]
mail=Mail(app)

recipientcontact = os.environ["MAIL_DEFAULT_SENDER"]
# configure private key
SECRET = os.environ['SECRET']

# configure sending email since gmail blocked less secure app
unsetMail = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///keeptrack.db")


listelements = [ 
        {
            "type": "books",
            "title": "a title for the element",
            "year": "year of release",
            "author": "the author of the book",
            "description" : "a brief text describing the element",
            "cover": "an image to associate with the element",
            "link": "a link to assciate with the element",
            "note": "a brief text to assciate with the element"
        },
        {
            "type": "movies_tvseries",
            "title": "a title for the element",
            "year": "year of release",
            "director": "the director of the movie/tv serie",
            "description" : "a brief text describing the element",
            "cover": "an image to associate with the element",
            "link": "a link to assciate with the element",
            "note": "a brief text to assciate with the element"
        },
        {
            "type": "places",
            "name": "name of location",
            "street": "street of location",
            "city": "city of location",
            "postal_code": "postal code of location",
            "province": "province of location",
            "country": "country of location",
            "latitude": "geographical coordinates to assciate with the element",
            "longitude": "geographical coordinates to assciate with the element",
            "cover": "an image to associate with the element",
            "link": "a link to assciate with the element",
            "description" : "a brief text describing the element",
            "note": "a brief text to assciate with the element",
        },
        {
            "type": "shopping",
            "name": "name of item",
            "brand": "brand of the item",
            "collection": "collection the item belongs to",
            "quantity": "how many items are needed",
            "price": "price per item",
            "description" : "a brief text describing the element",
            "cover": "an image to associate with the element",
            "wheretobuy": "places or stores where to buy the item",
            "note": "a brief text to assciate with the element",
            "status": ["to buy","bought"]
        },
        {
            "type": "closet",
            "name": "name of item",
            "brand": "brand of the item",
            "tag": "a particular tag you want to label the item as",
            "type_of_item": "type of item",
            "price": "item's cost at time of buying",
            "cover": "an image to associate with the element",
            "store": "store where the item has been bought",
            "datetime_of_buying": "when the item has been bought",
            "note": "a brief text to assciate with the element",
        },
        {
            "type": "storage",
            "name": "name of item",
            "brand": "brand of the item",
            "tag": "a particular tag you want to label the item as",
            "type_of_item": "type of item",
            "quantity": "number of pieces per item in your storage",
            "cover": "an image to associate with the element",
            "note": "a brief text to assciate with the element",
        }, 
        {
            "type": "shoppinglist",
            "name": "name of product",
            "quantity": "number of pieces per item needed",
            "price": "price of the product",
            "cover": "an image to associate with the bill",
            "note": "a brief text to assciate with the element",
        }, 
        {
            "type": "bills",
            "name": "name of bill",
            "description" : "a brief text describing the element",
            "expiration_date": "expiring date of the bill",
            "cost": "cost of the bill",
            "cover": "an image to associate with the bill",
            "status": ["to pay", "paid"],
            "cover_paid": "an image to associate with the paid bill",
            "note": "a brief text to assciate with the element",
        }, 
        {
            "type": "todo",
            "name": "name of to do action",
            "nolaterthan": "date by which it has to be done",
            "onthisdatetime": "date on which it has to be done",
            "cover": "an image to associate with the to do action",
            "time": "time at which it has to be done",
            "status": ["to do", "done"],
            "note": "a brief text to assciate with the element",
        }, 
]

listelementstoedit= [ 
        {
            "type": "movies_tvseries",
            "title": "a title for the element",
            "year": "year of release",
            "director": "the director of the movie/tv serie",
            "description" : "a brief text describing the element",
            "link": "a link to assciate with the element",
            "note": "a brief text to assciate with the element"
        },
        {
            "type": "books",
            "title": "a title for the element",
            "year": "year of release",
            "author": "the author of the book",
            "description" : "a brief text describing the element",
            "link": "a link to assciate with the element",
            "note": "a brief text to assciate with the element"
        },
        { 
            "type": "places",
            "name": "name of location",
            "street": "street of location",
            "city": "city of location",
            "postal_code": "postal code of location",
            "province": "province of location",
            "country": "country of location",
            "latitude": "geographical coordinates to assciate with the element",
            "longitude": "geographical coordinates to assciate with the element",            "link": "a link to assciate with the element",
            "description" : "a brief text describing the element",
            "note": "a brief text to assciate with the element",
        },
        {
            "type": "shopping",
            "name": "name of item",
            "brand": "brand of the item",
            "collection": "collection the item belongs to",
            "quantity": "how many items are needed",
            "price": "price per item",
            "description" : "a brief text describing the element",
            "wheretobuy": "places or stores where to buy the item",
            "note": "a brief text to assciate with the element",
            "status": "to buy or bought"
        },
        {
            "type": "closet",
            "name": "name of item",
            "brand": "brand of the item",
            "tag": "a particular tag you want to label the item as",
            "type_of_item": "type of item",
            "price": "item's cost at time of buying",
            "store": "store where the item has been bought",
            "datetime_of_buying": "when the item has been bought",
            "note": "a brief text to assciate with the element",
        },
        {
            "type": "storage",
            "name": "name of item",
            "brand": "brand of the item",
            "tag": "a particular tag you want to label the item as",
            "type_of_item": "type of item",
            "quantity": "number of pieces per item in your storage",
            "note": "a brief text to assciate with the element",
        },
        {
            "type": "shoppinglist",
            "name": "name of product",
            "quantity": "number of pieces per item needed",
            "price": "price of the product",
            "note": "a brief text to assciate with the element",
        }, 
        {
            "type": "bills",
            "name": "name of bill",
            "description" : "a brief text describing the element",
            "expiration_date": "expiring date of the bill",
            "cost": "cost of the bill",
            "status": ["to pay", "paid"],
            "note": "a brief text to assciate with the element",
        },
        {
            "type": "todo",
            "name": "name of to do action",
            "nolaterthan": "date by which it has to be done",
            "onthisdatetime": "date on which it has to be done",
            "time": "time at which it has to be done",
            "status": ["to do", "done"],
            "note": "a brief text to assciate with the element",
        },
]

sorttypes = { 
    'lists': ['namelist', 'most recent', 'least recent', "type of list"],
    'movies_tvseries': ['title','most recent', 'least recent', 'director', 'year'],
    'books': ['title','most recent', 'least recent', 'author'],
    'places': ['name', 'city', 'province', 'country','most recent', 'least recent'],
    'shopping': ['name', 'brand', 'most recent', 'least recent', 'price','status'],
    'closet' : ['name', 'brand', 'most recent', 'least recent', 'price', 'tag', 'type_of_item','datetime_of_buying'],
    'storage' : ['name', 'brand', 'most recent', 'least recent', 'tag', 'type_of_item','quantity'],
    'shoppinglist': ['name', 'quantity', 'most recent', 'least recent', 'price'],
    'bills' : ['name', 'most recent', 'least recent', 'cost','expiration_date', 'status'],
    'todo': ['name', 'most recent', 'least recent', 'nolaterthan','onthisdatetime', 'status']
    }

gridelements = [
    {
        "type": "lists",
        "namelist" : "name of a list",
    },
    {
            "type": "movies_tvseries",
            "title": "a title for the element",
            "year": "year of release",
            "director": "the director of the movie/tv serie",
        },
        {
            "type": "books",
            "title": "a title for the element",
            "year": "year of release",
            "author": "the author of the book",
        },
        {
            "type": "places",
            "name": "name of location",
            "city": "city of location",
            "province": "province of location",
        },
        {
            "type": "shopping",
            "name": "name of item",
            "brand": "brand of item",
            "status": "to buy or bought",
        },
        {
            "type": "closet",
            "name": "name of item",
            "brand": "brand of the item",
            "tag": "a particular tag you want to label the item as",
        },
        {
            "type": "storage",
            "name": "name of item",
            "quantity": "number of pieces per item in your storage",
            "tag": "a particular tag you want to label the item as",
        },
        {
            "type": "shoppinglist",
            "name": "name of item",
            "quantity": "number of pieces per item needed",
            "price": "price of the product",
        },
        {
            "type": "bills",
            "name": "name of bill",
            "expiration_date": "expiring date of the bill",
            "status": "to pay or paid",
        },
        {
            "type": "todo",
            "name": "name of to do action",
            "nolaterthan": "date by which it has to be done",
            "status": "to do or done",
        },
        
]
titleelements = [
    {
        "type": "lists",
        "namelist" : "name of a list",
        "type of list": "type of list"
    },
    {
            "type": "movies_tvseries",
            "title": "a title for the element",
            "year": "year of release",
        },
        {
            "type": "books",
            "title": "a title for the element",
            "author": "the author of the book",
        },
        {
            "type": "places",
            "name": "name of location",
            "city": "city of location",
        },
        {
            "type": "shopping",
            "name": "name of item",
            "status": "to buy or bought",
        },
        {
            "type": "closet",
            "name": "name of item",
            "brand": "brand of the item",
        },
        {
            "type": "storage",
            "name": "name of item",
            "quantity": "number of pieces per item in your storage",
        },
        {
            "type": "shoppinglist",
            "name": "name of item",
            "quantity": "number of pieces per item needed",
        },
        {
            "type": "bills",
            "name": "name of bill",
            "expiration_date": "expiring date of the bill",
        },
        {
            "type": "todo",
            "name": "name of to do action",
            "status": "to do or done",
        },

]

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
    print(rows)
    db.execute("UPDATE tokens SET status=? WHERE user_id=? AND token=?", status, user_id, token)
    return

#func to check token status in db
def check_token_status(user_id, token, tokentype):
    rows = db.execute("SELECT * FROM tokens WHERE user_id=? AND token=?", user_id, token)
    status = rows[0]['status']
    return status


#func to create a new list in db
def addlist(nametable, namelist,user_id):
    # take the id from table of all types of list
    rows = db.execute("SELECT * FROM list_types WHERE nametable=?", nametable)
    list_type_id = rows[0]['id']
    # insert the element
    db.execute("INSERT INTO lists (user_id,list_type_id,namelist) VALUES (?,?,?)", user_id, list_type_id, namelist)
    return 

#func to delete a list from db and all its element in nametable db
def deletelist(lists_id, nametable):
    db.execute("BEGIN TRANSACTION")

    # first delete all its elements in nametable db
    db.execute("DELETE FROM ? WHERE lists_id=?", nametable, lists_id)
    # second delete all its imgs in imgs db
    db.execute("DELETE FROM imgs WHERE lists_id=?", lists_id)
    # then, delete the list from table of all of user's lists
    db.execute("DELETE FROM lists WHERE id=?", lists_id)
    db.execute("COMMIT")
    return

# func to delete one list's element
def deleteoneelement(nametable, elementid):
    #delete elements
    # first delete its image in imgs db
    db.execute("DELETE FROM imgs WHERE nametable=? AND nametable_id=?", nametable, elementid)
    db.execute("DELETE FROM ? WHERE id=?", nametable, elementid)
    return 

# func to add a new element to list in db
def add_element_movies_tvseries(nametable,namelist,lists_id,user_id,title,year,director,description,img_id,link,note):
    db.execute("BEGIN TRANSACTION")
    # insert the element data
    # 0 value is value for null since db column only takes integers
    # if img_id == 'null':
        #img_id == 0;
    db.execute("INSERT INTO movies_tvseries (namelist,lists_id,user_id,title,year,director,description,img_id,link,note) VALUES (?,?,?,?,?,?,?,?,?,?)",namelist,lists_id, user_id,title,year,director,description,img_id,link,note)
    rows = db. execute("SELECT * FROM movies_tvseries WHERE namelist=? AND lists_id=? AND user_id=? AND title=?", namelist, lists_id, user_id, title)
    nametable_id = {'nametable': nametable, 'nametable_id': rows[0]['id'], 'lists_id': lists_id}
    db.execute("COMMIT")
    return nametable_id

# func to add an img in imgs db
def addimage(img, name, mimetype, nametable, nametable_id, lists_id):
    # insert the img in imgs db 
    db.execute("INSERT INTO imgs (img, name, mimetype, nametable, nametable_id, lists_id) VALUES (?,?,?, ?,?, ?)", img, name, mimetype, nametable, nametable_id, lists_id)
    # update img_id in the nametable
    img_id = db.execute("SELECT * FROM imgs WHERE nametable_id=? AND nametable=? AND lists_id=?", nametable_id, nametable, lists_id)
    img_id = img_id[0]['id']
    db.execute("UPDATE ? SET img_id=? WHERE id=?",nametable, img_id, nametable_id)
    return

# func to add a new element to list in db
def add_element(nametable,dictofelements, namelist, lists_id, user_id):
    if nametable == 'books':
        db.execute("BEGIN TRANSACTION")
        # insert the element data
        # 0 value is value for null since db column only takes integers
        # img_id is always 0, it is updated after the image has been stored in imgs db
        db.execute("INSERT INTO books (namelist,lists_id,user_id,title,year,author,description,img_id,link,note) VALUES (?,?,?,?,?,?,?,?,?,?)",namelist,lists_id,user_id,dictofelements['title'],dictofelements['year'],dictofelements['author'],dictofelements['description'],0,dictofelements['link'],dictofelements['note'])
        rows = db.execute("SELECT * FROM books WHERE namelist=? AND lists_id=? AND user_id=? AND title=?", namelist, lists_id, user_id, dictofelements['title'])
        nametable_id = {'nametable': nametable, 'nametable_id': rows[0]['id'], 'lists_id': lists_id}
        db.execute("COMMIT")
        return nametable_id
    elif nametable == 'movies_tvseries':
        db.execute("BEGIN TRANSACTION")
        # insert the element data
        # 0 value is value for null since db column only takes integers
        # img_id is always 0, it is updated after the image has been stored in imgs db
        db.execute("INSERT INTO movies_tvseries (namelist,lists_id,user_id,title,year,director,description,img_id,link,note) VALUES (?,?,?,?,?,?,?,?,?,?)",namelist,lists_id,user_id,dictofelements['title'],dictofelements['year'],dictofelements['director'],dictofelements['description'],0,dictofelements['link'],dictofelements['note'])
        rows = db.execute("SELECT * FROM movies_tvseries WHERE namelist=? AND lists_id=? AND user_id=? AND title=?", namelist, lists_id, user_id, dictofelements['title'])
        nametable_id = {'nametable': nametable, 'nametable_id': rows[0]['id'], 'lists_id': lists_id}
        db.execute("COMMIT")
        return nametable_id
    elif nametable == 'places':
        db.execute("BEGIN TRANSACTION")
        # insert the element data
        # 0 value is value for null since db column only takes integers
        # img_id is always 0, it is updated after the image has been stored in imgs db
        if len(dictofelements['postal_code']) <= 0:
            dictofelements['postal_code'] = 'null'
            address = f"{dictofelements['street']}, {dictofelements['city']}, {dictofelements['province']}, {dictofelements['country']}"
        else:
            dictofelements['postal_code'] = int(dictofelements['postal_code'])
            address = f"{dictofelements['street']}, {dictofelements['city']} {(dictofelements['postal_code'])}, {dictofelements['province']}, {dictofelements['country']}"

        db.execute("INSERT INTO places (namelist,lists_id,user_id,name,street,city,postal_code,province, country, address, latitude, longitude, link, description, img_id,note) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",namelist,lists_id,user_id,dictofelements['name'],dictofelements['street'],dictofelements['city'], (dictofelements['postal_code']), dictofelements['province'], dictofelements['country'], address, dictofelements['latitude'], dictofelements['longitude'], dictofelements['link'],dictofelements['description'], 0 , dictofelements['note'])
        rows = db.execute("SELECT * FROM places WHERE namelist=? AND lists_id=? AND user_id=? AND name=?", namelist, lists_id, user_id, dictofelements['name'])
        nametable_id = {'nametable': nametable, 'nametable_id': rows[0]['id'], 'lists_id': lists_id}
        db.execute("COMMIT")
        upadateLongLat(rows)

        return nametable_id
    elif nametable == 'shopping':
        db.execute("BEGIN TRANSACTION")
        # insert the element data
        # 0 value is value for null since db column only takes integers
        # img_id is always 0, it is updated after the image has been stored in imgs db
        db.execute("INSERT INTO shopping (namelist,lists_id,user_id,name,brand,collection,quantity, price, description, img_id, wheretobuy,note, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",namelist,lists_id,user_id,dictofelements['name'],dictofelements['brand'],dictofelements['collection'],dictofelements['quantity'],dictofelements['price'],dictofelements['description'], 0, dictofelements['wheretobuy'], dictofelements['note'], dictofelements['status'] )
        rows = db.execute("SELECT * FROM shopping WHERE namelist=? AND lists_id=? AND user_id=? AND name=?", namelist, lists_id, user_id, dictofelements['name'])
        nametable_id = {'nametable': nametable, 'nametable_id': rows[0]['id'], 'lists_id': lists_id}
        db.execute("COMMIT")
        return nametable_id
    elif nametable == 'closet':
        db.execute("BEGIN TRANSACTION")
        # insert the element data
        # 0 value is value for null since db column only takes integers
        # img_id is always 0, it is updated after the image has been stored in imgs db
        db.execute("INSERT INTO closet (namelist,lists_id,user_id,name,brand,tag,type_of_item, price, img_id, store,datetime_of_buying,note) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",namelist,lists_id,user_id,dictofelements['name'],dictofelements['brand'],dictofelements['tag'],dictofelements['type_of_item'], dictofelements['price'], 0, dictofelements['store'],dictofelements['datetime_of_buying'], dictofelements['note'] )
        rows = db.execute("SELECT * FROM closet WHERE namelist=? AND lists_id=? AND user_id=? AND name=?", namelist, lists_id, user_id, dictofelements['name'])
        nametable_id = {'nametable': nametable, 'nametable_id': rows[0]['id'], 'lists_id': lists_id}
        db.execute("COMMIT")
        return nametable_id
    elif nametable == 'storage':
        db.execute("BEGIN TRANSACTION")
        # insert the element data
        # 0 value is value for null since db column only takes integers
        # img_id is always 0, it is updated after the image has been stored in imgs db
        db.execute("INSERT INTO storage (namelist,lists_id,user_id,name,brand,tag,type_of_item,quantity, img_id,note) VALUES (?,?,?,?,?,?,?,?,?,?)",namelist,lists_id,user_id,dictofelements['name'],dictofelements['brand'],dictofelements['tag'],dictofelements['type_of_item'], dictofelements['quantity'], 0, dictofelements['note'])
        rows = db.execute("SELECT * FROM storage WHERE namelist=? AND lists_id=? AND user_id=? AND name=?", namelist, lists_id, user_id, dictofelements['name'])
        nametable_id = {'nametable': nametable, 'nametable_id': rows[0]['id'], 'lists_id': lists_id}
        db.execute("COMMIT")
        return nametable_id
    elif nametable == 'bills':
        db.execute("BEGIN TRANSACTION")
        # insert the element data
        # 0 value is value for null since db column only takes integers
        # img_id is always 0, it is updated after the image has been stored in imgs db
        db.execute("INSERT INTO bills (namelist,lists_id,user_id,name,description,expiration_date,cost,img_id,status, img_paid_id, note) VALUES (?,?,?,?,?,?,?,?,?,?,?)",namelist,lists_id,user_id,dictofelements['name'],dictofelements['description'],dictofelements['expiration_date'],dictofelements['cost'], 0, dictofelements['status'], 0, dictofelements['note'])
        rows = db.execute("SELECT * FROM bills WHERE namelist=? AND lists_id=? AND user_id=? AND name=?", namelist, lists_id, user_id, dictofelements['name'])
        nametable_id = {'nametable': nametable, 'nametable_id': rows[0]['id'], 'lists_id': lists_id}
        db.execute("COMMIT")
        return nametable_id
    elif nametable == 'shoppinglist':
        db.execute("BEGIN TRANSACTION")
        # insert the element data
        # 0 value is value for null since db column only takes integers
        # img_id is always 0, it is updated after the image has been stored in imgs db
        db.execute("INSERT INTO shoppinglist (namelist,lists_id,user_id,name,quantity, price,img_id,note) VALUES (?,?,?,?,?,?,?,?)",namelist,lists_id,user_id,dictofelements['name'],dictofelements['quantity'],dictofelements['price'], 0, dictofelements['note'])
        rows = db.execute("SELECT * FROM shoppinglist WHERE namelist=? AND lists_id=? AND user_id=? AND name=?", namelist, lists_id, user_id, dictofelements['name'])
        nametable_id = {'nametable': nametable, 'nametable_id': rows[0]['id'], 'lists_id': lists_id}
        db.execute("COMMIT")
        return nametable_id
    elif nametable == 'todo':
        db.execute("BEGIN TRANSACTION")
        # insert the element data
        # 0 value is value for null since db column only takes integers
        # img_id is always 0, it is updated after the image has been stored in imgs db
        db.execute("INSERT INTO todo (namelist,lists_id,user_id,name,nolaterthan, onthisdatetime,img_id,time,note, status) VALUES (?,?,?,?,?,?,?,?,?,?)",namelist,lists_id,user_id,dictofelements['name'],dictofelements['nolaterthan'],dictofelements['onthisdatetime'], 0, dictofelements['time'], dictofelements['note'], dictofelements['status'])
        rows = db.execute("SELECT * FROM todo WHERE namelist=? AND lists_id=? AND user_id=? AND name=?", namelist, lists_id, user_id, dictofelements['name'])
        nametable_id = {'nametable': nametable, 'nametable_id': rows[0]['id'], 'lists_id': lists_id}
        db.execute("COMMIT")
        return nametable_id
    else:
        return

def upadate_address(id):
    rows = db.execute("SELECT * FROM places WHERE id=?", id)
    print(rows[0]['postal_code'])
    if rows[0]['postal_code'] == 'null':
        address = f"{rows[0]['street']}, {rows[0]['city']}, {rows[0]['province']}, {rows[0]['country']}"
    else:
        address = f"{rows[0]['street']}, {rows[0]['city']} {rows[0]['postal_code']}, {rows[0]['province']}, {rows[0]['country']}"
    db.execute("UPDATE places SET address=? WHERE id=?", address, id )
    # updates long and lat
    upadateLongLat(rows)
    return

def send_contact_request(object, account, email, name, lastname, messagecontact):
    # create an email object, sender and recipient 
    msg = Message(object, sender = 'MAIL_DEFAULT_SENDER', recipients=[recipientcontact])
    # create body of email
    msg.body = f'Request sent by:\nemail: {email}\naccount: {account} \nLast Name: {lastname}\nName: {name}\nObject: {object}\nMessage: \n{messagecontact}'
    # send email
    mail.send(msg)
    return 


# func to add an img in imgs db
def addpaidimage(img, mimetype, nametable, nametable_id, lists_id):
    # insert the img in imgs db 
    db.execute("INSERT INTO imgs (img, name, mimetype, nametable, nametable_id, lists_id) VALUES (?,?,?,?, ?,?)", img, 'img_paid', mimetype, nametable, nametable_id, lists_id)
    # update img_id in the nametable
    # paid img in bills always have 'img_paid' as img['name']
    img_id = db.execute("SELECT * FROM imgs WHERE nametable_id=? AND nametable=? AND lists_id=? and name=?", nametable_id, 'bills', lists_id, 'img_paid')
    img_paid_id = img_id[0]['id']
    # update paid img id in bills table 

    db.execute("UPDATE bills SET img_paid_id=? WHERE id=?",img_paid_id, nametable_id)
    return

# func to update quantity in shopping list view
def updatequantity(qnty, type, id):
    x = db.execute("SELECT quantity FROM shoppinglist WHERE id=?", int(id))
    if type == 'add':
        db.execute("UPDATE shoppinglist SET quantity=? WHERE id=?", x[0]['quantity']+1, int(id))
    if type == 'remove':
        db.execute("UPDATE shoppinglist SET quantity=? WHERE id=?", x[0]['quantity']-1, int(id))
    return

# func to update status in to do list view
def updatetodostatus(status, id):
    x = db.execute("SELECT status FROM todo WHERE id=?", int(id))
    if status == 'to do':
        newstatus = 'done'
    if status == 'done':
        newstatus = 'to do'
    db.execute("UPDATE todo SET status=? WHERE id=?", newstatus, int(id))
    return


# func to update long and lat in places table
def upadateLongLat(dict):
    # return a json to update long and lat in the table
    for element in dict:
        if element['address'] and len(element['address']) > 0:
            address = element['address']
            # url for the request
            url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
            # make a request and await a json response
            response = requests.get(url).json()
            if len(response) > 0:
                latitude = (response[0]["lat"])
                longitude = (response[0]["lon"])
                # update db places
                db.execute('UPDATE places SET latitude=?, longitude=? WHERE id=?', latitude, longitude, element['id'])
            else:
                address = f"{element['name']} {element['city']}"
                url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
                response = requests.get(url).json()
                if len(response) > 0:
                    latitude = (response[0]["lat"])
                    longitude = (response[0]["lon"])
                    # update db places
                    db.execute('UPDATE places SET latitude=?, longitude=? WHERE id=?', latitude, longitude, element['id'])
                return
        return
   

#CREATE TABLE lists (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER,list_type_id INTEGER, namelist TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (list_type_id) REFERENCES list_types(id));

#CREATE TABLE movies_tvseries (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, lists_id INTEGER, user_id INTEGER, title TEXT NOT NULL, year VARCHAR(4), director TEXT, description TEXT, cover TEXT, link TEXT, note TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (lists_id) REFERENCES lists(id));

#CREATE TABLE books (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, lists_id INTEGER, user_id INTEGER, title TEXT NOT NULL, year VARCHAR(4), author TEXT, description TEXT, img_id INTEGER, link TEXT, note TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (lists_id) REFERENCES lists(id));

#CREATE TABLE places (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, lists_id INTEGER, user_id INTEGER, name TEXT NOT NULL, street TEXT, city TEXT, postal_code INTEGER, province TEXT, country TEXT, address TEXT, latitude TEXT, longitude TEXT, link TEXT, description TEXT, img_id INTEGER, note TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (lists_id) REFERENCES lists(id));

#CREATE TABLE shopping (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, lists_id INTEGER, user_id INTEGER, name TEXT NOT NULL, brand TEXT, collection TEXT, quantity INTEGER, price FLOAT, description TEXT, img_id INTEGER, wheretobuy TEXT, note TEXT, status CHECK(status in ('to buy', 'bought')), FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (lists_id) REFERENCES lists(id));

#CREATE TABLE closet (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, lists_id INTEGER, user_id INTEGER, name TEXT NOT NULL, brand TEXT, tag TEXT, type_of_item TEXT, price FLOAT, img_id INTEGER, store TEXT, datetime_of_buying DATETIME, note TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (lists_id) REFERENCES lists(id));

#CREATE TABLE storage (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, lists_id INTEGER, user_id INTEGER, name TEXT NOT NULL, brand TEXT, tag TEXT, type_of_item TEXT, quantity INTEGER, img_id INTEGER, note TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (lists_id) REFERENCES lists(id));

#CREATE TABLE bills (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, lists_id INTEGER, user_id INTEGER, name TEXT NOT NULL, description TEXT, expiration_date datetime, cost FLOAT, img_id INTEGER, status CHECK(status in ('to pay', 'paid')), img_paid_id INTEGER, note TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (lists_id) REFERENCES lists(id));

#CREATE TABLE shoppinglist (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, lists_id INTEGER, user_id INTEGER, name TEXT NOT NULL, quantity INTEGER, price FLOAT, img_id INTEGER, note TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (lists_id) REFERENCES lists(id));


#CREATE TABLE todo (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, namelist TEXT NOT NULL, lists_id INTEGER, user_id INTEGER, name TEXT NOT NULL, nolaterthan DATE, onthisdatetime DATE, img_id INTEGER, time TIME, note TEXT, status CHECK(status in ('to do', 'done')), FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (lists_id) REFERENCES lists(id));