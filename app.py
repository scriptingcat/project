#app

import os
from flask import Flask,redirect, request, render_template, session, Response, send_file, url_for
from flask_session import Session
from tempfile import mkdtemp
from flask_mail import Mail, Message


from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from helpers import login_required, validCharPass, validLenPass, generate_token, verify_token, send_reset_email, insert_token_in_db, expire_token_status_in_db, check_token_status, addlist, deletelist, deleteoneelement, add_element_movies_tvseries, addimage, add_element, upadate_address, listelements, listelementstoedit, sorttypes, gridelements, titleelements,send_contact_request
from email_validator import validate_email

from io import BytesIO
import sqlite3


# library to create jwt token 
import jwt

# library to encode/decode img 
import base64


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

'''
    "Name": "a name for the element",
    "Title": "a title for the element",
    "Description" : "a brief text describing the element",
    "Author": "the author of the element",
    "Director": "the director of the movie/tv serie",
    "Datetime": "datetime of particular meaning for the element",
    "Image/Cover": "an image to associate with the element",
    "Link": "a link to assciate with the element",
    "Coordinates": "geographical coordinates to assciate with the element",
    "Note": "a brief text to assciate with the element",
    "Qty": "a number for quantity of the element",
    "Price": "price of the element",
    "Sum": "sum of price * quantity (must include price)",
    "Total": "total of sums of price * quantity of all elements (must include price and sum)"
}
'''

@app.after_request
def after_request(response):
    # ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return render_template("index.html")
    else:
        return render_template("index.html")

@app.route("/mylists", methods=["GET", "POST"])
@login_required
def mylists():
    # select list of types can be chosen
    listtypes = db.execute("SELECT nametable FROM list_types")

    # select user's lists already created
    userslists = db.execute("SELECT namelist, id FROM lists WHERE user_id=?", session['user_id'])
    if request.method == "POST":
        typeoflist = request.form.get('typeoflist')
        namelist = request.form.get('namelist')

        # check values for creating new list
        if not typeoflist and not namelist:
            apologymsg = "All fields required"
            return render_template("mylists.html", apologymsg=apologymsg.capitalize(), listtypes=listtypes,sorttypes=sorttypes, userslists=userslists)
        if not typeoflist:
            apologymsg = "Type of list selection required"
            return render_template("mylists.html", apologymsg=apologymsg.capitalize(), listtypes=listtypes, sorttypes=sorttypes, userslists=userslists)
        
        # not allowing user to manipulate the selections
        checktype=False
        for element in listtypes:
            for key,value in element.items():
                if typeoflist == value:
                    checktype = True
                    break
            if checktype == True:
                break
        if checktype == False:
            apologymsg = "Type of list selected not recognized"
            return render_template("mylists.html", apologymsg=apologymsg.capitalize(), listtypes=listtypes, sorttypes=sorttypes, userslists=userslists)

        if not namelist:
            apologymsg = "Name list required"
            return render_template("mylists.html", apologymsg=apologymsg.capitalize(), listtypes=listtypes, sorttypes=sorttypes, userslists=userslists)

        addlist(typeoflist, namelist, session['user_id'])
        return redirect("/mylists")

    else:
        showmessage = request.args.get('message')
        if showmessage is None or len(showmessage) == 0:
            return render_template("mylists.html", listtypes=listtypes, nametable='lists',sorttypes=sorttypes,userslists=userslists)
        else:
            return render_template("mylists.html", nametable='lists',listtypes=listtypes,sorttypes=sorttypes, userslists=userslists, showmessage=showmessage)

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
        return redirect("/mylists")

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
        apologymsg = "Account created!"
        return redirect("/mylists" + "?message=" + apologymsg)

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
                        apologymsg = "Expired Token 4"
                        return render_template("forgotpassword.html", apologymsg=apologymsg.capitalize())
                    else:
                        return render_template("resetpassword.html", id=token)
            except:
                # if it returns an error, return to forgot password
                apologymsg = "Expired Token 5"
                return render_template("forgotpassword.html", apologymsg=apologymsg)

    # check request method
    if request.method == "POST":
        # handle exception from verifying token to get user_id back
        try:
            newpassword = request.form.get("newpassword")
            confirmationpassword = request.form.get("confirmationpassword")
            token = request.form.get("id")
            
            user_id = verify_token(token)
            print('verified')
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
            db.execute("COMMIT")

            # make token expire 
            expire_token_status_in_db(user_id, token)

            return render_template("login.html", apologymsg=apologymsg)
        
        except:
            # if it returns an error, return to forgot password
            apologymsg = "Expired Token"
            return render_template("forgotpassword.html", apologymsg=apologymsg)


@app.route("/list", methods=["GET", "POST"])
@login_required
def showlist():
    # show list elements

    # query for id of list to be shown
    lists_id = request.args.get('lists_id')
    # select the list from lists
    lists = db.execute("SELECT * FROM lists WHERE id=?", int(lists_id))
    namelist = lists[0]['namelist']
    # select the list from list_types
    list_types = db.execute("SELECT * FROM list_types WHERE id=?", lists[0]['list_type_id'])
    nametable = list_types[0]['nametable']
    # select all the element contained in that list
    elements = db.execute("SELECT * FROM ? WHERE lists_id=? AND user_id=?", nametable, int(lists_id), session['user_id'])
    images = db.execute("SELECT * FROM imgs WHERE lists_id=?", lists_id)
    
    if request.method == 'POST':

        # actions from this route 

        # input from the form for request 
        actiononelement = request.form.get('actiononelement')
        
        # add element to table
        if actiononelement == "addelement": 
            
            # handle inputs based on type of table

            # initialize a void dict where to save all the input
            dictofrequests = {}
            # check in global listelements which types of input are needed for that particular table
            for dictionary in listelements:
                # when found the table type that matches the nametable of lists_id showing
                if dictionary['type'] == nametable:
                    # save that nametable value for key type in dict of inputs requests
                    dictofrequests['type'] = nametable
                    # for each key in this dict add value equals to input
                    for key,value in dictionary.items():
                        # first check whether its a text input or image/file
                        if key in ['cover','image']:
                            # take the object
                            file = request.files['inputimage']
                            elementinput = file
                            # check is not none
                            if len(file.filename)<=0:
                                elementinput = 0
                            dictofrequests[key] = elementinput
                        if key not in ['image', 'cover']:
                            elementinput = request.form.get(key)
                            dictofrequests[key] = elementinput
                    break
            
            # check title-name request is provided
            for k,v in dictofrequests.items():
                if k == 'title':
                    if not dictofrequests['title'] or dictofrequests['title'] == None:
                        apologymsg = "Element Title Is Required"
                        return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
                    else:
                        break
                if k == 'name':
                    if not dictofrequests['name'] or dictofrequests['name'] == None:
                        apologymsg = "Element Name Is Required"
                        return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
                if k == 'status':
                    if not dictofrequests['status'] or dictofrequests['status'] == None or  dictofrequests['status'] not in ['to buy', 'bought']:
                        apologymsg = "Element status Error. Status is required. Values allowed: to buy or bought."
                        return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
                    else:
                        break
            print(dictofrequests)
            # check whether there's an img to save in db:
            if not dictofrequests['cover'] or dictofrequests['cover'] == 0:
                add_element(nametable, dictofrequests, namelist, lists_id, session['user_id'])
            else:
                db.execute("BEGIN TRANSACTION")
                # take all the info from filestorage obj
                #data
                img = dictofrequests['cover'].read()
                #filename - how suggested by the guidelines
                filename = secure_filename(dictofrequests['cover'].filename)
                #mimetype
                mimetype = dictofrequests['cover'].mimetype
                # add the element to the nametable type table and take nametable_id to pass to addimage
                nametable_id_info = add_element(nametable, dictofrequests, namelist, lists_id, session['user_id'])
                # add the image to image db
                addimage(img, filename, mimetype, nametable_id_info['nametable'], nametable_id_info['nametable_id'], nametable_id_info['lists_id'])
                db.execute("COMMIT")
            return redirect("/list?lists_id=" + lists_id)

        # change list name
        elif actiononelement == "changenamelist":
            newnamelist = request.form.get('newnamelist')
            responsechangenamelist = request.form.get('responsechangenamelist')
            # check lists_id to be deleted matches user_id
            checkuser = db.execute("SELECT * FROM lists WHERE id=?", lists_id)
            checkuser = checkuser[0]['user_id']
            if checkuser == session['user_id']:
                # check the response submited
                if responsechangenamelist == "Change":
                    # make sure a new list name is provided when submiting for change
                    if not newnamelist:
                        apologymsg = "New List Name required"
                        return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)

                    else:
                        db.execute("BEGIN TRANSACTION")
                        db.execute("UPDATE lists SET namelist=? WHERE id=?",newnamelist, lists_id)
                        db.execute("UPDATE ? SET namelist=? WHERE lists_id=?",nametable, newnamelist, lists_id)
                        db.execute("COMMIT")
                        return redirect("/list?lists_id=" + lists_id)
                else:
                    apologymsg = "List Name has not been changed"
                    return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
        
        # delete one element from table
        elif actiononelement == "deleteelement":
            iddeleteelement = request.form.get('iddeleteelement')
            # check id element to be deleted exists
            if iddeleteelement:
                # check user of id element to be deleted matches session's user_id
                checkuser = db.execute("SELECT * FROM ? WHERE id=?",nametable, int(iddeleteelement))
                checkuser = checkuser[0]['user_id']
                if checkuser == session['user_id']:
                    deleteoneelement(nametable, int(iddeleteelement))
                    return redirect("/list?lists_id=" + lists_id)
                else:
                    apologymsg = "Id element does not match user id. Action on this id denied"
                    return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
            else:
                apologymsg = "Id element required"
                return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
        
        # delete the whole table
        elif actiononelement == "deletelist":
            # check lists_id to be deleted matches user_id
            checkuser = db.execute("SELECT * FROM lists WHERE id=?", lists_id)
            checkuser = checkuser[0]['user_id']
            if checkuser == session['user_id']:
                # check the response submited
                responsedeletelist = request.form.get('responsedeletelist')
                if responsedeletelist == 'Yes':
                    deletelist(lists_id, nametable)
                    return redirect("/mylists")
                else:
                    apologymsg="This list has not been deleted"
                    return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
            else:
                apologymsg = "Id list does not match user id"
                return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)

        # download element
        elif actiononelement == 'downloadelement':
            iddownloadelement = request.form.get('iddownloadelement')
            # handle id request
            if not iddownloadelement:
                apologymsg = "Id element required"
                return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)

            img_id = db.execute("SELECT * FROM ? WHERE id=?", nametable, int(iddownloadelement))
            # check there's an image to be downloaded
            if img_id[0]['img_id'] == 0:
                images = db.execute("SELECT * FROM imgs WHERE lists_id=?", lists_id)
                apologymsg = "No image to download"
                return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)

            # check id element belongs to session's user
            if img_id[0]['user_id'] != session['user_id']:
                apologymsg = "Id does not match user id"
                return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)


            img = db.execute("SELECT * FROM imgs WHERE id=?", int(img_id[0]['img_id']))
            return send_file(BytesIO(img[0]['img']), attachment_filename='download.jpg',as_attachment=True)

        # edit element
        elif actiononelement == 'editelement':
            try:
                # store the requests in a list
                listreqstoedit = []
                # create strings for colomns to pass new values in order to update db
                coltoset = ""
                # nametags in html inputs is edit{{key}}
                nametag = 'edit'
                # loop through the colomn that can be edited for each corrisponding type of nametable
                for dictionary in listelementstoedit:
                    if dictionary['type'] == nametable:
                        for key,value in dictionary.items():
                            if key != 'type':
                                # handle commas in strings
                                if len(coltoset) == 0:
                                    coltoset = coltoset
                                else:
                                    coltoset = coltoset + ", "
                                # take the requests and save them in a list                            
                                listreqstoedit.append(request.form.get(nametag + str(key)))
                                # update strings
                                coltoset = coltoset + str(key) + " = ?"
                        break

                # take the id and check it belongs to session's user
                ideditelement = request.form.get('ideditelement')
                if not ideditelement:
                    apologymsg = "Id element required"
                    return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
                rows = db.execute("SELECT * FROM ? WHERE id=?", nametable, int(ideditelement))
                # executemany takes 1 seq of param, so requests list must containd the id too, which is also the last param for update sql query (where id = ?), so id needs to be appended as last index of list
                listreqstoedit.append(int(ideditelement))
                if session['user_id'] != rows[0]['user_id']:
                    apologymsg = "Id does not match user id"
                    return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
                # handle the requests, title / name is always the first so at index 0
                if len(listreqstoedit[0]) <=0:
                    apologymsg = "title is required".capitalize()
                    return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
                
                # update the table
                # using sqlite3 library because cs50 sql library doesn't allow to pass a list of param since there's no executemany 
                sqltoupdate = "UPDATE " + nametable + " SET " + coltoset + " WHERE id=?"
                connection = sqlite3.connect('keeptrack.db')
                cursor = connection.cursor()
                # list of params has to be followed by a comma because it need to be treated as tuples
                cursor.executemany(sqltoupdate,(listreqstoedit,))
                connection.commit()
                connection.close()
                if nametable == 'places':
                    upadate_address(int(ideditelement))
                apologymsg = 'Updated'
                return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)
            except:
                apologymsg = 'Something went wrong. Updating failed.'
                return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)

        else:
            # check lists_id user matches session's user_id
            # prevent from showing other users' lists by manipulating html code
            user_id = lists[0]['user_id']
            if session['user_id'] == user_id:
                for image in images:
                    image['imagedata'] = base64.b64encode(image['img']).decode('ascii')
            apologymsg = "Type of Request not recognized"
            return redirect('/list?lists_id=' + lists_id + '&apologymsg=' + apologymsg)


    else:
        # GET METHOD
        # check lists_id user matches session's user_id
        # prevent from showing other users' lists by manipulating html code
        user_id = lists[0]['user_id']
        if session['user_id'] == user_id:
            apologymsg = request.args.get('apologymsg')
            for image in images:
                image['imagedata'] = base64.b64encode(image['img']).decode('ascii')
            if apologymsg:
                return render_template('list.html', nametable=nametable, namelist=namelist,elements=elements,sorttypes= sorttypes, listelements=listelements, lists_id=lists_id, images=images, apologymsg=apologymsg)
            return render_template('list.html', nametable=nametable, namelist=namelist,elements=elements,sorttypes= sorttypes, listelements=listelements, lists_id=lists_id, images=images)
        else:
            apologymsg = "Something went wrong. Access to list Denied"
            return redirect("/mylists" + "?message=" + apologymsg)


@app.route('/image')
@login_required
def image():

    # open image
    nametable_id = request.args.get('nametable_id')
    nametable = request.args.get('nametable')
    
    try:
        # hande input
        if not nametable_id or not nametable:
            apologymsg = "Something went wrong. Access to element Denied"
            return redirect("/mylists" + "?message=" + apologymsg)
        
        rows = db.execute("SELECT * FROM ? WHERE id=?", nametable, int(nametable_id))
        # check user requesting is owner of the element
        if rows[0]['user_id'] != session['user_id']:
            apologymsg = "Something went wrong. Access to element Denied"
            return redirect("/mylists" + "?message=" + apologymsg)

        img = db.execute("SELECT * FROM imgs WHERE nametable_id=? AND nametable=?", int(nametable_id), nametable)
        image = base64.b64encode(img[0]['img']).decode('ascii')
        return render_template('image.html',data=img[0]['mimetype'], image=image)

    # for any other type of exception
    except:
        apologymsg = "Something went wrong"
        return redirect("/mylists" + "?message=" + apologymsg)

@app.route('/search')
@login_required
def search():
    # search element in list with a specific name or title
    query = request.args.get('q')
    lists_id = request.args.get('lists_id')

    # select the list from lists
    lists = db.execute("SELECT * FROM lists WHERE id=?", int(lists_id))
    # select the list from list_types
    list_types = db.execute("SELECT * FROM list_types WHERE id=?", lists[0]['list_type_id'])
    nametable = list_types[0]['nametable']

    entry = db.execute('SELECT * FROM ? WHERE title LIKE ? AND user_id=?', nametable, '%'+ query + '%', session['user_id'])
    if len(entry)>0:
        return render_template("search.html", entry=entry)
    else:
        return render_template("search.html", apologymsg="no result")

@app.route('/elements')
@login_required
def elements():
    # show elements of a list, sort them and return the style of the view

    sortby = request.args.get('sortby')
    styleview = request.args.get('styleview')
    lists_id = request.args.get('lists_id')
    if lists_id != 'lists':
        lists = db.execute("SELECT * FROM lists WHERE id=?", int(lists_id))
        namelist = lists[0]['namelist']
        # select the list from list_types
        list_types = db.execute("SELECT * FROM list_types WHERE id=?", lists[0]['list_type_id'])
        nametable = list_types[0]['nametable']
        # select all the element contained in that list
        elements = db.execute("SELECT * FROM ? WHERE lists_id=? AND user_id=?", nametable, int(lists_id), session['user_id'])
        images = db.execute("SELECT * FROM imgs WHERE lists_id=?", int(lists_id))
    else:
        lists = db.execute("SELECT * FROM lists WHERE user_id=?", session['user_id'])
        nametable = 'lists'
        elements = lists

    try:
        if sortby and styleview:
            if sortby == 'most recent':
                if nametable == 'lists':
                    elementssorted = db.execute("SELECT * FROM lists WHERE user_id=? ORDER BY id DESC", session['user_id'])
                else:
                    elementssorted = db.execute("SELECT * FROM ? WHERE lists_id=? AND user_id=? ORDER BY id DESC", nametable, int(lists_id), session['user_id'])
            elif sortby == 'least recent':
                if nametable == 'lists':
                    elementssorted = db.execute("SELECT * FROM lists WHERE user_id=? ORDER BY id ASC", session['user_id'])
                else:
                    elementssorted = db.execute("SELECT * FROM ? WHERE lists_id=? AND user_id=? ORDER BY id ASC", nametable, int(lists_id), session['user_id'])
            else:
                counter = 0
                # iterate throughout key in dict of sort types
                for k,v in sorttypes.items():
                    # when key = nametable, chack the value which is a list
                    if k == nametable:
                        # iterate through the list
                        for i in v:
                            # when element in list == sortby request value 
                            if i == sortby:
                                # select ordered by that value 
                                if k == 'lists':
                                    if sortby == 'type of list':
                                         elementssorted= db.execute("SELECT * FROM ? WHERE user_id=? ORDER BY list_type_id ASC", nametable, session['user_id'])
                                    else: 
                                        elementssorted= db.execute("SELECT * FROM ? WHERE user_id=? ORDER BY " + sortby +" ASC", nametable, session['user_id'])
                                else:
                                    elementssorted= db.execute("SELECT * FROM ? WHERE lists_id=? AND user_id=? ORDER BY " + sortby +" ASC", nametable, int(lists_id), session['user_id'])
                                # add +1 to counter so that I know elements has been re-selected and break
                                counter+=1
                                break
                        # counter == 0 means no re-selection, so elementssorted == first selection 
                        if counter == 0:
                            elementssorted = elements
                        # break iteration through dict once nametable is found  
                        break
            # elements equals to whatever is in elementssorted
            elements = elementssorted
            # check requested value for styleview and pass it to style
            if styleview == 'table':
                style = 'table'
            elif styleview == 'title':
                style = 'title'
            else:
                style ='grid'
            # always check user's requesting is owner of list
            if nametable != 'lists':
                user_id = lists[0]['user_id']
                if session['user_id'] == user_id:
                    # decode dataimage from bytes to ascii to be rendered
                    for image in images:
                        image['imagedata'] = base64.b64encode(image['img']).decode('ascii')
                return render_template("elements.html", elements=elements, style=style, images=images, listelements=listelements, nametable=nametable, gridelements=gridelements, titleelements=titleelements)
            else:
                return render_template("elements.html", elements=elements, style=style, images='null', listelements=listelements, nametable=nametable, gridelements=gridelements, titleelements=titleelements)
    except:
        return render_template("elements.html", apologymsg="Something went wrong")

@app.route('/contact', methods = ['GET', 'POST'])
def contact():
    # send a message via email to admin

    if request.method == 'POST':

        name=request.form.get('nameofcontact')
        lastname = request.form.get('lastnameofcontact')
        email = request.form.get('emailofcontact')
        account = request.form.get('accountofcontact')
        object = request.form.get('objectofcontact')
        message = request.form.get('messageofcontact')

        # check inputs are filled
        if name == None or len(name) <= 0:
            apologymsg = "Name is required"
            return redirect('/contact'+'?showmessage='+apologymsg)
        if lastname == None or len(lastname) <= 0:
            apologymsg = "Last name is required"
            return redirect('/contact'+'?showmessage='+apologymsg)
        if email == None or len(email) <= 0:
            apologymsg = "Email is required"
            return redirect('/contact'+'?showmessage='+apologymsg)
        if object == None or len(object) <= 0:
            apologymsg = "Name is required"
            return redirect('/contact'+'?showmessage='+apologymsg)
        if message == None or len(message) <= 0:
            apologymsg = "Message is required"
            return redirect('/contact'+'?showmessage='+apologymsg)
        send_contact_request(object, account, email, name, lastname, message)
        apologymsg = "Request Sent"
        return redirect('/contact'+'?showmessage='+apologymsg)
    else:   
        showmessage = request.args.get('showmessage')
        if showmessage:
            return render_template('contact.html', showmessage=showmessage)
        return render_template('contact.html')

@app.route('/customizedtype')
@login_required
def customizedtype():
    return render_template('customizedtype.html', listelements=listelements)



