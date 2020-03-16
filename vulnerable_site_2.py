from bottle import route, get, run, post, request, response, redirect
import re
import sqlite3
import sys

# CHANGE THIS
address = 'localhost'
port = 8080

# SETUP -------------------------------------------------------------

def database_setup():
    cur.execute("DROP TABLE IF EXISTS Users")
    conn.commit()
    cur.execute("""CREATE TABLE Users(
        Id INT,
        username TEXT,
        password TEXT,
        status TEXT,
        admin INTEGER DEFAULT 0
    )""")
    cur.execute("""INSERT INTO Users
        VALUES(1, 'The FBI', 'throwawaypassword#123456', 'Watching this page', 0)""")
    cur.execute("""INSERT INTO Users
        VALUES(2, 'Bobby', 'tables', 'Being an Admin 24/7', 1)""")
    conn.commit()


# LOGIN PAGES --------------------------------------------------
@get('/') # or @route('/login')
def login():
    return '''
        Login with a username and password
        <form action="/login" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
        \n
        Or register here: 
        <form action="/register" method="get">
            <input value="Register" type="submit" />
        </form>
    '''

# Attempt to register a username and password
@post('/login') # or @route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')

    cur.execute("""SELECT 1 FROM Users
    WHERE username = '%s' AND password = '%s'""" % (username, password))
    if cur.fetchone():
        # Competition: How insecure can you make a website?
        if cur.execute("SELECT admin FROM Users WHERE username = '%s'" % username).fetchone():
            admin = cur.execute("SELECT admin FROM Users WHERE username = '%s'" % username).fetchone()[0]
        else:
            admin = 0
        response.set_cookie("username", username)  
        response.set_cookie("password", password)
        response.set_cookie("admin", str(admin))
        return '''<p>You've successfully logged in as %s </p> 
                <form action="/list" method="get">
                <input value="View Users" type="submit" />
                </form> \n
                <form action="/logout" method="get">
                <input value="logout" type="submit" />
                </form>
                <p> Search for a user </p>
                <form action="/search" method="post">
                    Username: <input name="username" type="text"/>
                    <input value="Search!" type="submit" />
                </form>
        '''  % username
    else:
        return "<p>This combination is invalid.</p>"

# LOGOUT ----------------------------------------
@get('/logout')
def do_logout():
    response.delete_cookie('username')
    response.delete_cookie('password')
    response.delete_cookie('admin')
    redirect('/')

# REGISTRATION PAGES ---------------------------------
@get('/register')
def register():
    return '''
        Register with a username and password
        <form action="/register" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            Status: <input name="status" type="text" /> 
            <input value="Register" type="submit" />
        </form>
    '''

# Attempt to register a username and password
@post('/register') # or @route('/login', method='POST')
def do_register():
    global n_users
    username = request.forms.get('username')
    password = request.forms.get('password')
    status = request.forms.get('status')

    cur.execute("INSERT INTO Users VALUES(%d, '%s', '%s', '%s', 0)" %(n_users+1, username, password, status))
    conn.commit()
    n_users += 1
    return '''
        <p>You have registered successfully!</p>
        <form action="/" method="get">
            <input value="Login" type="submit" />
        </form>
    '''

# VIEW USERS ---------------------------------------------

@get('/list')
def list():
    username = request.cookies.get('username','0')
    password = request.cookies.get('password','0')
    admin = int(request.cookies.get('admin','0'))

    cur.execute("""SELECT 1 FROM Users
    WHERE username = '%s' AND password = '%s'""" % (username, password))
    if cur.fetchone():

        str_out = "<p>A list of all current users and their status:</p><p></p>"

        for user in cur.execute("SELECT username, password, status FROM Users"):
            if admin == 1: #Print the passwords too, just to be even more insecure
                str_out += "<p>Username: %s, Password: %s, Status: %s </p>" % (user[0], user[1], user[2])
            else:
                str_out += "<p>Username: %s Status: %s </p>" % (user[0],  user[2])
        return str_out
    else:
        return "Please Log In First"

# SEARCH -----------------------------

@post('/search')
def search_int():
    username = request.forms.get('username', '0')
    redirect('/search/%s' % username)
    return 

@get('/search/<username:path>')
def search(username):
    cur.execute("""
        SELECT username, status 
        FROM Users
        WHERE username = '%s'""" % username)
    user = cur.fetchone()
    if user is not None and user is not False:
        return"<p>%s is %s </p>" % (user[0], user[1])
    else:
        return "User %s was not found!" % username

# VIEW USERS ---------------------------------------------
@get('/db')
def db():
    s = ''
    for line in conn.iterdump():
        s += line
    return s

conn = sqlite3.connect(":memory:")
cur = conn.cursor()
database_setup()

n_users = 2

run(host=address, port=port, debug=True)