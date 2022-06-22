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
If the user provides a username, an email, a password and a password confirmation, they are all sent to the server by a post request.  The server checks this information and if something is missing or does not meet the requirements, an error message is rendered.

If the input data does not fail the checks, the password is hashed and saved into users table in the db as well as th username, and the email address.
Then, the user is redirected to /mylists.

***
### Login:

If the user has already signed up, it can log in by providing its username and password in the template login.html rendered by get request of app.route /login.
The server checks the receiving data and if a username as username provided input exists, it checks the corrisponding password matches the hashed password stored in the users table for that username.
It returns an error message if the checks fails, or it redirects the users to its /mylists.

***
### Logout:

The user can log out by clicking on log out from my account dropdown menu and the server will clear the session and redirect to the index.

***
### Changepassword:

The user can change its password by clicking on change password from my account dropdown menu and the server will answer this request by rendering the changepassword.html where the user has to provide first its current password and then, a new password that must be confirmed.
When the user clicks on change password a post request is sent to the /changepassword and the server will check the provided inputs, and save the new hashed password in the users table if all checks do not fail, in that case an error message is redered according to the type of error.

***
### Forgotpassword:

If the user does not remember its password, it can ask for adding a new one by clicking on forgot password.
In the /forgotpassword, the user has to provide its username or email, if one of these provided exists on users table in the db, the server will send an email to the user's email address, cointaining a link with a validation token which will be saved in the tokens table in the db.
The token is a jwt and cointains payload data in which user's id, user's email and expiring time of 300 seconds from the time of request have been stored and hashed using the secret key provided in the venv.

***
### Resetpassword:

When the user clicks on the link received via email, the server checks the token. If it is valid, meaning not being expired, the resetpaswword.html is rendered. At that point, the user can provide all the inputs for the new password to be saved and the process is the same as that one for the sign up post request with the exception of already having username and email.
Before rendering the login.html, the used token is stored as expired in its status table column.

***
### Mylists:

This page will only be rendered if the user has logged in.
When no lists has aleady been created, the user will a large toggle in the middle of the window and by clicking on it some other button will show up from which it can send a post request to server to create a new list.
It has to provide a name for the list and to choose a type.
When the server receives the post request, it checks the inputs are correctly provided, it has to be sure the type of list exists by looking for it in the list_types table and that case saves the corrisponding list_type_id in the general lists table where the newly created list will be stored and associated with the user_id.

Now, the /mylists can show the first user list.

From now on, for all the other route.app, every function associated with that particular path which requires the log in always checks the user_id of requesting data belongs to the session['user_id'].
Never trust the user.

When the user's lists cointains more than one list, the user can choose to sort by its lists and/or change the view mode  - from the title view which is the default view, into the table view - by clicking on the specific buttons.
Sort by select and view mode buttons call javascript async functions requesting the sorted elements and views to app.route /elements which renders elements.html.

By clicking on the title of the list, the user can access to its elements.

***
### List:





The same happens to the search bar where, by providing inputs, an async function calls /search.

***
### Search:
This path is called








