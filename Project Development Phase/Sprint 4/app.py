from flask import Flask, render_template, request, redirect, url_for, session

import requests, json, os
import ibm_db
import re
import os
import pathlib
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

app.secret_key = 'a'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=spw66260;PWD=;",'','')
print(conn)
print("connection successfull")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global userid
    msg=''

    if request.method =='POST':
        username = request.form['username']
        password =request.form['password']
        sql ="SELECT * FROM users WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            session['loggedin']=True
            session['id'] = account ['USERNAME']
            userid = account['USERNAME']
            session['username'] = account['USERNAME']
            msg = 'logged in successfully !'

            return render_template('submission.html',msg = msg)

        else:
            msg ='Incorrect username / password !'
    return render_template('login.html',msg=msg)
def execute_sql(statement, **params):
    global conn
    stmt = db.prepare(conn, statement)
    
    param_id = 1
    for key, val in params.items():
        db.bind_param(stmt, param_id, val)
        param_id += 1
    
    result = ''
    try:
        db.execute(stmt)
        result = db.fetch_assoc(stmt)
    except:
        pass
    
    return result
def send_confirmation_mail(user, email):
    message = Mail(
        from_email="",
        to_emails="",
        subject="YAYY!! Your Account was created successfully!",
        html_content= "<strong>Account Created with username {0}</strong>".format(user)
    )
    
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        sql = "SELECT * FROM users WHERE username = ?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg ='Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg ='Invaild email address !'
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg = 'Name must contain only characters and numbers!'
        else:
            insert_sql = "INSERT INTO users VALUES (?,?,?)"
            prep_stmt= ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1 , username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
            msg = ' you have successfully registered !'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/forgot', methods=['GET', 'POST'])
url = "https://low-carb-recipes.p.rapidapi.com"

headers = {
  "x-rapidapi-key": "ad933ea36amsh6b0a83e514b1a58p14bc9ejsne745a5851a1b",
  "x-rapidapi-host":  "low-carb-recipes.p.rapidapi.com"
  }

searchForRecipes = "/search"
getRecipe="/recipes/"
getImage="/images/2807982c-986a-4def-9e3a-153a3066af7a.jpeg"
getRandomRecipe="/random"
@app.route('/result',methods=['GET','POST'])
def per_info():
    msg=''
    if request.method =='POST':
        Name=request.form['Name']
        gender=request.form['gender']
        tar_weight=request.form['Target Weight']
        Age=request.form['Age']
        Height=request.form['Height']
        Weight=request.form['Weight']
        email=request.form['email']
        location=request.form['location']
        phoneno=request.form['phoneno']
        sql='SELECT * FROM USER WHERE username=?'
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,Name)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            insert_sql='INSERT INTO USER values(?,?,?,?,?,?,?)'
            prep_stmt=ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt,1,Name)
            ibm_db.bind_param(prep_stmt,2,gender)
            ibm_db.bind_param(prep_stmt,3,Age)
            ibm_db.bind_param(prep_stmt,4,Height)
            ibm_db.bind_param(prep_stmt,5,Weight)
            ibm_db.bind_param(prep_stmt,7,location)
            ibm_db.execute(prep_stmt)
            msg="Your details are successfully stored"
            return render_template('viewprofile.html',msg=msg)
    elif request.method=="POST":
        msg="Please fill out the form"
    return render_template('result.html',msg=msg)

def forgot():
    if not session.get('user'):
        return redirect(LOG_IN_PAGE_URL)

    msg = ''
    user = ''
    email = ''
    if request.method == 'POST':
        user = session.get('user')
        oldpass = request.form['oldpass']
        newpass = request.form['newpass']

        sqlst = 'SELECT password from user where username = ?'
        dbpass = execute_sql(statement = sqlst , username = user)['PASSWORD']
        sqlst = 'SELECT email from user where username = ?'
        email = execute_sql(statement = sqlst ,username = user)['EMAIL']

        if dbpass == oldpass:
            sqlst = 'UPDATE user SET password = ? where username = ?'
            execute_sql(statement = sqlst , password = newpass , username = user)
            msg = 'Updated Successfully!'
        else:
            msg = 'Old Password Incorrect!'
        
        return render_template('login.html', user=user, email=email, msg=msg)

    return render_template('forgot.html')

@app.route('/home')
def submission():
    return render_template('home')


if __name__=='__main__':
    app.run()