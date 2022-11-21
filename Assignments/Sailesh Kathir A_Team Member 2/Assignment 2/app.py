from flask import Flask, redirect, render_template, url_for, request, session
import ibm_db

app = Flask(__name__)
app.secret_key = "aiuhe72texy8SASAo2qDHKXsfsfZNkeyuxU2WOXo"
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=2d46b6b4-cbf6-40eb-bbce-6251e6ba0300.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=32328;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=lvc22806;PWD=bVsxv0mAqXhfYPoT", '', '')
sql = "CREATE TABLE IF NOT EXISTS Users (Email varchar(50),Rollno int,Username varchar(50),Password varchar(50))"
stmt = ibm_db.prepare(conn, sql)
ibm_db.execute(stmt)


@app.route("/")
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'], email=session['email'], rollno=session['rollno'])
    return redirect(url_for('register'))


@app.route("/register/", methods=['POST', 'GET'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        email = request.form['email']
        rollno = request.form['rollno']
        username = request.form['username']
        password = request.form['password']

        sql = "SELECT * FROM Users WHERE Email =? or Rollno =? or Username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, rollno)
        ibm_db.bind_param(stmt, 3, username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            error = "Either Email Id or Username or Roll no already exists,Please Try Again"
        else:
            insert_sql = "INSERT INTO Users VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, email)
            ibm_db.bind_param(prep_stmt, 2, rollno)
            ibm_db.bind_param(prep_stmt, 3, username)
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.execute(prep_stmt)

            session['loggedin'] = True
            session['email'] = email
            session['username'] = username
            session['rollno'] = rollno

            return redirect(url_for('home'))

    return render_template('register.html', error=error)


@app.route("/login/", methods=['POST', 'GET'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        sql = "SELECT * FROM Users WHERE Username =? AND Password =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session['loggedin'] = True
            session['email'] = account["EMAIL"]
            session['username'] = username
            session['rollno'] = account["ROLLNO"]
            return redirect(url_for('home'))
        else:
            error = "Invalid Credentials, Please Try Again"
    return render_template('login.html', error=error)

@app.route('/update/', methods=['POST', 'GET'])
def update():
    error = None
    if not 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        oldpassword = request.form['oldpassword']
        password = request.form['password']

        sql = "SELECT * FROM Users WHERE Username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1,session['username'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account['PASSWORD']==oldpassword:
            insert_sql = "UPDATE Users SET Password =? WHERE Username =?"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1,password)
            ibm_db.bind_param(prep_stmt, 2,session['username'])
            ibm_db.execute(prep_stmt)
            return redirect(url_for('home'))
        else:
            error = "Wrong Password Entered,Try Again"
    return render_template('update_pass.html', error=error)

@app.route('/delete/')
def delete():
    if 'username' in session:
        sql = "DELETE FROM Users WHERE Username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session['username'])
        ibm_db.execute(stmt)
        return redirect(url_for('logout'))
    return redirect(url_for('home'))

@app.route('/logout/')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    session.pop('username', None)
    session.pop('rollno', None)
    return redirect(url_for('login'))
