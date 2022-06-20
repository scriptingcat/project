# KEEP TRACK

### Video Demo:  <URL HERE>

***
### Description:
Keep Track is a web-based application that allows the users to create and save its lists on a personal account, to choose the type of list among different options provided by the web-app and have the possibility to also add and store in the db an image for each item added to that list.

***
### Built with:
* Python
* flask and Jinja
* SQL
* HTML
* CSS
* JavaScript
* Bootstrap

***
#### Get started:

First of all, be sure to have installed each of the library of th requirements.txt file.
Requirements.txt contains all the libraries used in this project you can see at the beginning of the app.py and helpers.py files.

In order to start the web-app, it is needed to download the project folder and create a virtual env folder where some variables have to be set in order to make the app work.

After the creation of the .env folder, open the file activate in the bin folder contained in the .env folder, and add the following variables:

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
The sending email functions are needed to send emails for the forgot password requests and for the contact requests and this instructions have to be followed in order to make them working.

In this version, the app comes with the variable unsetMail set on True because during the developing process I was using a gmail account as default email to send reset password tokens and contact requests but since May, 30th 2022, gmail has not been allowing anymore this kind of usage unless a phone number is provided (which I don't want to).

***
### To run the app:
In order to run the app in vs code using flask, the .env has to be activated.
So, in the terminal the command source followed by the path to the activate file in your venv must be executed. 
If you are using WSL in VS Code, this is the code:

* $ source /yourpath/project/.env/bin/activate

If the venv is correctly activated, (.env) will precede your account in the terminal. Then, run flask:

* (.env) youraccount:~/project$ flask run

Click on the link provided in the terminal and the web-app will open in the browser.

***
### Index:

The index page is the first one opening; from this page you can choose to log in or sign up by clicking on the button on the navbar on the right side or on the a-link on the footer of the page.
Some other pages that can be reached from here are the about.html and the contact.html both on the footer as anchor links. 

The index page is rendered by the @app.route("/") function index() which return the render_template of index.html

***
### Layout:

This is a layout page used to recreate the same style layout on every other html page created.
The nav-bar provides two different versions according to whether a user has logged in or not:

* if a user has logged in, on the nav-bar right buttons /mylists can be reached as well as /changepassword and /logout from a dropdown menu button named Account placed next to mylists button; also, the log in and sign up a-links on the footer will redirect to the index page.

* if there is no session['user_id'], the buttons on the nav-bar will be log in and sign up.

Layout.html is the only html file that is not linked to any app.route in the app.py file since it only works as a layout model for all the other .html pages meaning that each of the pages .html extends layout.html's title and main blocks.

***
### SignUp:
This html page is rendered by the get method of app.route /signup which clears the session and render the template of signup.html if no session is provided, otherwise the user is redirected to the '/'.

***
### Mylists:








