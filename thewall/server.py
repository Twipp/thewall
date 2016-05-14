from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re

from flask.ext.bcrypt import Bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "SHHHThisIsSecret!"
mysql = MySQLConnector(app, 'thewall')
@app.route('/')
def index():

    return render_template('index.html')

@app.route('/submit', methods = ['POST'])
def submit():

    #query
    query = "SELECT * FROM users"

    userList = mysql.query_db(query)



    #validations for login registration
    if len(request.form['firstName']) < 2:
        flash("First name must have more than 2 letters")
    elif len(request.form['lastName']) < 2:
        flash("Last name must have more than 2 letters")
    elif len(request.form['email']) < 2:
        flash("Invalid Email Address!")
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
    elif len(request.form['password']) < 2:
        flash("Password must be more than 2 characters long")
    elif request.form['password'] != request.form['confirmPass']:
        flash("Passwords must match")
    elif not (checkUser(userList, request.form['email'])):
        flash("User Already Registered")
    else:
        # encrypts password
        pw_hash = bcrypt.generate_password_hash(request.form['password'])

        # store email address in the database
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:firstName, :lastName, :email, :password,  NOW(), NOW())"
        data = {
            'firstName': request.form['firstName'],
            'lastName': request.form['lastName'],
            'email': request.form['email'],
            'password': pw_hash,
        }

        mysql.query_db(query, data)

        #stores user data into session when logged in.
        session['newFirstName'] = request.form['firstName']
        session['newLastName'] = request.form['lastName']
        session['newEmail'] = request.form['email']
        return redirect ('/success')
    return redirect ('/register')

@app.route('/register')
def register():

    return render_template('registration.html')

@app.route('/login', methods = ['POST'])
def login():

    query = "SELECT * FROM users WHERE email = :email"
    data = {'email': request.form['email']}
    user =  mysql.query_db(query, data)
    password = request.form['password']

    if not user:
        flash( "Invalid Login")
        redirect ('/')
    elif (password == ""):
        flash("Please enter a password")
        return redirect ('/')
    elif (bcrypt.check_password_hash(user[0]['password'], password) == False):
        flash("Invalid Password")
        return redirect ('/')
    else:
        session['name'] =  user[0]['first_name']
        session['email'] = user[0]['email']
        session['user_id'] = user[0]['id']

        return redirect ('/wall')

    return redirect ('/')


@app.route('/success')
def success():

    #shows registered information
    return render_template('success.html')

@app.route('/wall')
def wall():

    # query = "SELECT user_id, message, id FROM messages"

    query = "SELECT m.id, m.created_at, m.message, u.first_name, u.last_name FROM messages AS m JOIN users AS u ON m.user_id = u.id ORDER BY m.created_at DESC"

    messagePosts = mysql.query_db(query)

    queryComment = "SELECT comment, first_name, last_name, comments.created_at, comments.id, comments.message_id FROM comments LEFT JOIN users as u ON user_id = u.id"

    commentPosts = mysql.query_db(queryComment)

    # print commentPosts
    # print messagePosts
    #
    # for inc in messagePosts:
    #     print inc['message']
    #going to have to join tables
    # print session['user_id']

    return render_template('/wall.html', messagePosts = messagePosts, commentPosts = commentPosts)

@app.route ('/logout')
def logout():


    session.pop('name')
    session.pop('email')
    session.pop('user_id')

    return redirect('/')

@app.route ('/postMessage', methods = ['POST'])
def postMessage():

    if(request.form['message']):

        query =  "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:user_id, :message, NOW(), NOW())"
        data = {
                'user_id': session['user_id'],
                'message': request.form['message'],
        }


        mysql.query_db(query, data)
    else:
        flash('Please enter a message.')



    return redirect('/wall')

@app.route ('/comment', methods = ['POST'])
def comment():

    if(request.form['comment']):
        query =  "INSERT INTO comments (message_id, user_id, comment, created_at, updated_at) VALUES (:message_id, :user_id, :comment, NOW(), NOW())"

        data = {

            'message_id':request.form['message_id'],
            'user_id': session['user_id'],
            'comment': request.form['comment'],

        }

        mysql.query_db(query, data)
    # print "Message ID: " + request.form['message_id']
    else:
        flash('Please enter a comment.')

    return redirect('/wall')


###Helper Functions

def checkUser(list, email):
    print "In Check User"
    for user in list:
        print user['email']
        if (user['email'] == email):
            print "SAME USER"
            return False

    return True;


app.run(debug=True)
