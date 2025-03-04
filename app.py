from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Message, Mail
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import random
from email_otp import sendEmailVerificationRequest

app = Flask(__name__)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'dhruvpa0913@gmail.com'
app.config['MAIL_PASSWORD'] = 'bajrnfibuwmmrojb'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.secret_key = 'xyzsdf'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'kaival'

mail = Mail(app)
mysql = MySQL(app)




@app.route('/')
def index():
    return render_template('index.html', session=session)
   

@app.route('/index1')
def index1():
    if 'name' in session:
        return render_template('index1.html', session=session)
    else:
        return redirect(url_for('login'))
    

@app.route('/hello')
def hello():
    return render_template('hello.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        if 'name' in request.form and 'password' in request.form and 'email' in request.form:
            userName = request.form['name']
            password = request.form['password']
            email = request.form['email']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
            account = cursor.fetchone()
            if account:
                message = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                message = 'Invalid email address!'
            elif not userName or not password or not email:
                message = 'Please fill out the form!'
            else:
                session['name'] = userName
                session['email'] = email
                session['password'] = password
                otp = random.randint(1000, 9999)
        
                session['current_otp'] = str(otp)
                html_body = render_template('mail.html')
                msg = Message("OTP", sender=email, recipients=[email],html=html_body)
                msg.body = str(otp)
                mail.send(msg)

                return redirect(url_for('verify'))

        else:
            message = 'Please fill out the form!'
    return render_template('register.html', message=message)

@app.route('/verify', methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        return redirect(url_for('login'))
    return render_template("verify.html")

@app.route('/validate', methods=["POST"])
def validate():
   
    current_user_otp = session.get('current_otp')
    print("Current User OTP", current_user_otp)

    name = session.get('name')
    email = session.get('email')
    password = session.get('password')
    print(name,email,password)
    user_otp = request.form['otp']
    print("User OTP : ", user_otp)

    if current_user_otp == user_otp:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO user(name, email, password) VALUES (%s, %s, %s)', (name,email,password,))
        mysql.connection.commit()
        session.pop('name')
        session.pop('email')
        session.pop('password')
        message = 'You have successfully registered!'
        return render_template('register.html', message=message)
    else:
        return "<h3> Oops! Email Verification Failure, OTP does not match. </h3>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        if user:
            session['name'] = user['name']  
            return redirect(url_for('index1'))  
        else:
            message = 'Please enter correct email / password!'
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
