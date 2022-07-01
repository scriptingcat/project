# **KEEP TRACK**


### **Video Demo**:   https://youtu.be/Qi7wSdEPuBM

<br>

***
### **Description**:
Keep Track is a web-based application that allows the users to create and save its lists on a personal account, choose the type of list among different options provided by the web-app and have the possibility to also add and store in the db an image for each item added to that list.

<br>

***
## **Table of Contents**

- [Get started](#get-started)
- [To run the app](#to-run-the-app)
- [Style](#style)
- [Keeptrack.db](#keeptrackdb)
- [App.py and Helpers.py](#apppy-and-helperspy)
- [Index](#index)
- [Layout](#layout)
- [SignUp](#signup)
- [Login](#login)
- [Logout](#logout)
- [Changepassword](#changepassword)
- [Forgotpassword](#forgotpassword)
- [Resetpassword](#resetpassword)
- [Mylists](#mylists)
- [List](#list)
- [About](#about)
- [Contact](#contact)

<br>

***
### **Built with**:
* Python
* flask and Jinja
* SQL
* HTML
* CSS
* JavaScript
* Bootstrap

<br>

***
### **Get started**:

First of all, be sure to have installed each of the library of the requirements.txt file.
Requirements.txt contains all the libraries used in this project you can see at the beginning of the app.py and helpers.py files.

In order to start the web-app, it is needed to download the project folder and create a virtual env folder where some variables have to be set in order to make the app work.

After the creation of the .env folder, open the file activate in the bin folder, contained in the .env folder, and add the following variables:

* MAIL_DEFAULT_SENDER = your email address
    it is required in order to send mails using flask, so it is needed to set the email address of administrator 

* MAIL_PASSWORD = your password
    Also, its password is requires in order to send mails using flask,

* MAIL_USERNAME = your email address

* SECRET = a secret key
    A secret key has to be provided in order to create the jwt

All these variables have to be added after the variable VIRTUAL_ENV = 'yourpath'.

After this, you also have to set on both helpers.py and app.py files the port and the server - according to your email address - where the following variables are initialized:

* app.config['MAIL_PORT'] = your port

* app.config['MAIL_SERVER'] = your sever address

Finally, you have to set the variable unsetMail in helpers.py on False so that the app is ready to send emails using the email address account provided.
The sending email functions are needed to send emails for the forgot password requests and for the contact requests and this instructions have to be followed in order to make them work.

In this version, the app comes with the variable unsetMail set on True because during the developing process I was using a gmail account as default email to send reset password tokens and contact requests but since May, 30th 2022, gmail has not been allowing anymore this kind of usage unless a phone number is provided (which I don't want to).

<br>

***
### **To run the app** :

In order to run the app using flask, the .env has to be activated.
So, in the terminal the command 'source' followed by the path to the activate file in your venv must be executed. 
If you are using WSL in VS Code, this is the code:

* $ source /yourpath/project/.env/bin/activate

If the venv is correctly activated, (.env) will precede your account in the terminal. Then, run flask:

* (.env) youraccount:~/project$ flask run

Click on the link provided in the terminal and the web-app will open in the browser.

<br>

***
### **Style**:

It is the CSS file where all the css styles are collected and stored in by tag, class, and id.
Every change is very basic in terms of styling (they concern margins, font-size, colors, hover transformations and so on) since I have used bootstrap framework.

<br>

***
### **Keeptrack.db**:

This is the database where all the tables used to make this web-app work are stored.
It cointains:

* **users** table
    <br>where all users' id, address and hashed password are stored;

* **tokens** table
    <br> where tokens and their detailed information are stored and associated with a user id;

* **list_types** table
    <br>in which all types of lists being possible to create are stored;

* **lists** table
    <br>this is a general list of lists where every new list created by a user is saved by storing: 
    * user id, in order to know the user it belongs to;
    * list type id, to know its type of list and the type table where list's elements are stored;
    * name of the list;
    
    <br>

* a series of type tables
    <br>everyone having its specific columns according to the kind of information needed to save:
    * **movies_tvseries** table
    * **books**
    * **shopping**
    * **closet**
    * **storage**
    * **bills**
    * **shoppinglist**
    * **to do**
    * **places**
    
    <br>
* **imgs** table
    <br>where all images from all users are stored by saving their names, mimetype and data (all as read from the filestorage object), name of the type table and its id which refers to a specific element saved in that nametable, and the lists id in order to know which list this element belongs to.
    Imgs id is stored in a specific column named img_id (that all type tables have) where an integer is saved: it is 0 by default if no image is uploaded for that element.

<br>

***
### **App.py and Helpers.py**:

App.py contains all the app.routes while in helpers.py are stored all the functions used to help and called by app.routes' functions.
In helpers.py all the dictionaries to correctly render each type of list are stored, too.

<br>

***
### **Index**:

The index page is the first one opening; from this page you can choose to log in or sign up by clicking on the button on the navbar on the right side or on the a-link on the footer of the page.
Some other pages that can be reached from here are the about.html and the contact.html both on the footer as anchor links. 

The index page is rendered by the @app.route("/") function index() which returns the render_template of index.html

<br>

***
### **Layout**:

This is a layout page used to recreate the same style layout on every other html page created.
The nav-bar provides two different versions according to whether a user has logged in or not:

* if a user has logged in, on the nav-bar right buttons /mylists can be reached as well as /changepassword and /logout from a dropdown menu button named Account placed next to mylists button; also, the log in and sign up a-links on the footer will redirect to the index page.

* if there is no session['user_id'], the buttons on the nav-bar will be log in and sign up.

Layout.html is the only html file that is not linked to any app.route in the app.py file since it only works as a layout model for all the other .html pages meaning that each of the pages .html extends layout.html's title and main blocks.

<br>

***
### **SignUp**:

This html page is rendered by the get method of app.route /signup which clears the session and renders the template of signup.html if no session is provided, otherwise the user is redirected to the '/'.
If the user provides a username, an email, a password and a password confirmation, they are all sent to the server by a post request.  The server checks this information and if something is missing or does not meet the requirements, an error message is rendered.

If the input data does not fail the checks, the password is hashed and saved into users table in the db as well as the username, and the email address.
Then, the user is redirected to /mylists.

<br>

***
### **Login**:

If the user has already signed up, it can log in by providing its username and password in the template login.html rendered by get request of app.route /login.
The server checks the receiving data and if a username as username provided input exists, it checks the corrisponding password matches the hashed password stored in the users table for that username.
It returns an error message if the checks fails, or it redirects the users to its /mylists.

<br>

***
### **Logout**:

The user can log out by clicking on log out from my account dropdown menu and the server will clear the session and redirect to the index.

<br>

***
### **Changepassword**:

The user can change its password by clicking on change password from my account dropdown menu and the server will answer this request by rendering the changepassword.html where the user has to provide first its current password and then, a new password that must be confirmed.
When the user clicks on change password a post request is sent to the /changepassword and the server will check the provided inputs, and save the new hashed password in the users table if all checks do not fail, in that case an error message is redered according to the type of error.

<br>

***
### **Forgotpassword**:

If the user does not remember its password, it can ask for adding a new one by clicking on forgot password.
In the /forgotpassword, the user has to provide its username or email, if any of these provided ones exists on users table in the db, the server will send an email to the user's email address, cointaining a link with a validation token which will be saved in the tokens table in the db.
The token is a jwt and cointains payload data in which user's id, user's email and expiring time of 300 seconds from the time of request have been stored and hashed using the secret key provided in the venv.

<br>

***
### **Resetpassword**:

When the user clicks on the link received via email, the server checks the token. If it is valid, meaning not being expired, the resetpassword.html is rendered. At that point, the user can provide all the inputs for the new password to be saved and the process is the same as that one for the sign up post request with the exception of already having username and email.
Before rendering the login.html, the used token is stored as expired in its status table column.

<br>

***
### **Mylists**:

This page will only be rendered if the user has logged in.
When no list has aleady been created, the user will see a large toggle in the middle of the window and by clicking on it, a form will show up from which it can send a post request to server to create a new list.
It has to provide a name for the list and to choose a type.
When the server receives the post request, it checks the inputs are correctly provided, it has to be sure the type of list exists by looking for it in the list_types table and in that case, it saves the corrisponding list_type_id in the general lists table where the newly created list will be stored and associated with the user_id.

Now, /mylists route can show the first user list.

From now on, for all the other routes .app, every function associated with that particular path which requires the log in always checks the user_id of requesting data belongs to the session['user_id'].
Never trust the user.

When the user's lists cointains more than one list, the user can choose to sort by its lists and/or change the view mode  - from the title view which is the default view, into the table view - by clicking on the specific buttons.
Sort by select and view mode buttons call javascript async functions requesting the sorted elements and views to app.route /elements which renders elements.html.

By clicking on the title of the list, the user can access to that list and its elements.

<br>

***
### **List**:

App.route /list renders list.html when a get request is made to the server.
showlist function reads lists_id get request and looks for that list id in the lists table, if the id belongs to the session['user_id'], that list's items and their images will be selected and rendered.
If no item has been stored for the specific list, a central toggle will show the inputs to create a new element by clicking on it.

From this page, by a post request the user can:

* change the name of the list 
   <br>first, the server makes sure the lists_id belongs to the session['user_id], then it updates its name with the new provided one in the lists table where the namelist is stored;

* delete the whole list
    <br>having done all the checks required, the server deletes the whole list and all its items as well as its images from the specific tables;

* add a new element to the list
    <br>the server collects and checks all the inputs provided by the user and saves them in a dictionary whose keys change based on the type of that list.
    This dictionary will be used to store/insert into the data in the specific type table and, if there is an image, this one will be stored in images table and its id stored in the image id in type table;
  
* search
    <br> by providing inputs in the search bar, an async function calls /search route where the function looks for that list's element with that provided title/name which is always required - meaning no list's item can be stored if the user does not provide a title/name;

* edit an element
    <br>all elements of a list, no matter what view style is being displayed, is a toggle that opens all the details of that element.
    By clicking on edit button, it is possible to update the data stored in the type table for that element id.
    Only for the type list 'bills' it is possible to also update/add a new image.

* delete an element
    <br>the element and all its details, image included, are deleted from the specific tables;

* close and close all buttons
    they close all the toggles clicked - meaning they remove show class from those elements, which is added when clicked on a bootstrap toggle - via javascript functions;

* show the image
   <br> by clicking on the image, it is possible to open it in the browser, each image stored in the table is accessible only if it belongs to the session['user_id'].
    Images are stored in the db table imgs by saving each filestorage object's filename, mimetype and data.
    When the images' data is sent to be rendered in image.html (this also happens to list.html), what is actually sent is a decoded version of that data that img tag element is ready to receive and read;

* download the image
    <br>by clicking on the icon under the image, a download of that image starts.
    Send_file function converts that image's data, filename and mimetype, into bytes and sends it to the user;

From this page, it is also possible to sort the elements in different ways and to change the view style, both depending on the type of that particular list.
These two functions call async javascript functions requesting the /elements route which renders styling and sorting of list's elements.

There are three basic view style:
* title view, showing the title;
* grid view, showing the images;
* table view, showing a table;

Some other extra view style are provided for:
* type of table 'places', where it is also possible to see markers of all the elements stored on a map;
* type of table 'todo', where it is also possible to see checked and unchecked to do elements;
* type of table 'shoppinglist', where it is also possible to see detailed information of each element such as quantity or price in a shopping list style.

<br>

***
### **About**:

It is a simple route that renders a page that explains how to use the web-app.

<br>

***
### **Contact**:

From this page the user can send a message to the administrator of the app.
The message sent is an email collecting the user's inputs, which is sent using the email information provided as previous explained for the forgot password.
