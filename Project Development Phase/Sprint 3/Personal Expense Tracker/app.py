

import ibm_db
from flask import Flask, redirect, render_template, request, session, url_for
from markupsafe import escape

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=764264db-9824-4b7c-82df-40d1b13897c2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=32536;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=dkh61031;PWD=epbaJyxx5Cfi7vTl",'','')

app = Flask(__name__)
app.secret_key='a'


@app.route('/')
@app.route('/register')
def register():
  return render_template('register.html')
@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/header')
def header():
    return render_template('header.html')

@app.route('/home')
def home():
  return render_template('home.html')



@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/addExpense')
def addExpense():
    return render_template('AddExpense.html')




@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
  if request.method == 'POST':

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    password= request.form['password']

    sql = "SELECT * FROM USERS WHERE NAME =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,name)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    if account:
      return render_template('login.html', msg="You are already a member, please login using your details")
    else:
      insert_sql = "INSERT INTO USERS (Name,email,phone,password) VALUES (?,?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, name)
      ibm_db.bind_param(prep_stmt, 2, email )
      ibm_db.bind_param(prep_stmt, 3, phone)
      ibm_db.bind_param(prep_stmt, 4, password)
      ibm_db.execute(prep_stmt)
    
    return render_template('login.html', msg="Registered successfuly..")






@app.route('/signin', methods =['GET', 'POST'])
def signIn():
    global userid
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        sql ="SELECT * FROM USERS WHERE  email = ? AND password = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
            
        if account:
            session['loggedin'] = True
            session['id'] = account['USERID']
            userid=account['USERID']
            session['username']=account['NAME']

            #session["name"] = request.form.get("name")
            
            #session['username'] = account['Name']
            msg = 'Welcome'+" "+session['username']+"!!"
            return render_template('home.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
        return render_template('login.html', msg = msg)





@app.route('/add', methods =['GET', 'POST'])
def add():
    global id
    if request.method=='POST':
      date=request.form['date']
      name=request.form['expenseName']
      amount=request.form['expenseAmount']
      category=request.form['expenseCategory']
      paymethod=request.form['payMethod']
      id=session['id']
      print(id)
      limit="SELECT AMOUNT FROM LIMIT WHERE USERID=id"
      stmt = ibm_db.prepare(conn, limit)
      ibm_db.bind_param(stmt,1,amount)
      ibm_db.execute(stmt)
      account = ibm_db.fetch_assoc(stmt)
      print(account)

      insert_sql = "INSERT INTO EXPENSE (USERID,DATE,NAME,AMOUNT,CATEGORY,PAYMENTMETHOD) VALUES (?,?,?,?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, id)
      ibm_db.bind_param(prep_stmt, 2, date )
      ibm_db.bind_param(prep_stmt, 3, name)
      ibm_db.bind_param(prep_stmt, 4, amount)
      ibm_db.bind_param(prep_stmt, 5, category)
      ibm_db.bind_param(prep_stmt, 6, paymethod)
      ibm_db.execute(prep_stmt)
    
    return render_template('history.html', msg="Data saved successfuly..")

      
      

@app.route('/history')
def history():
  global id
  id=session['id']
  print(session['username'])
  students = []
  sql = "SELECT * FROM EXPENSE where USERID=?"
  stmt = ibm_db.exec_immediate(conn, sql)
  dictionary = ibm_db.fetch_both(stmt)
  while dictionary != False:
    # print ("The Name is : ",  dictionary)
    students.append(dictionary)
    dictionary = ibm_db.fetch_both(stmt)

  if students:
    return render_template("history.html", students = students)


@app.route('/limit')
def limit():
      return render_template("limit.html")



@app.route('/limitnum' , methods = ['POST' ])
def limitnum():
     if request.method == "POST":
        number= request.form['number']
        sql = "INSERT INTO LIMIT(USERID,AMOUNT) VALUES(?,?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['id'])
        ibm_db.bind_param(stmt,2,number)
        ibm_db.execute(stmt)
        return render_template("today.html")

@app.route('/logout')
def logout():
  session.pop('loggedin', None)
  session.pop('id', None)
  session.pop('username', None)
  return render_template('register.html')
      
@app.route("/today")
def today():
      
      
      sql = "SELECT * FROM EXPENSE  WHERE userid =? AND date = DATE(NOW())"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list2=[]
      texpense=ibm_db.fetch_tuple(stmt)
      print(texpense)
      
      

      sql = "SELECT * FROM EXPENSE WHERE USERID=? AND DATE(date) = DATE(NOW())"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list1=[]
      expense = ibm_db.fetch_tuple(stmt)
      while(expense):
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)  
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in list1:
        total +=int(x[3])
        if x[4] == "food":
          t_food += int(x[3])
        
        elif x[4] == "entertainment":
            t_entertainment  += int(x[3])
      
        elif x[4] == "business":
              t_business  += int(x[3])
        elif x[4] == "rent":
          t_rent  += int(x[3])
           
        elif x[4] == "emi":
          t_EMI  += int(x[3])
         
        elif x[4] == "Miscellaneous":
          t_other  += int(x[3])
          
  


     
      return render_template("today.html", texpense = list1, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )




@app.route("/month")
def month():
      sql = "SELECT MONTHNAME(DATE),SUM(AMOUNT) FROM EXPENSE WHERE USERID=? GROUP BY MONTHNAME(DATE)"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list2=[]
      texpense = ibm_db.fetch_tuple(stmt)
      while(texpense):
        list2.append(texpense)
        texpense = ibm_db.fetch_tuple(stmt)
      print(list2)
      
      

      sql = "SELECT * FROM EXPENSE WHERE USERID=? AND MONTH(date)=MONTH(DATE(NOW()))"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list1=[]
      expense = ibm_db.fetch_tuple(stmt)
      while(expense):
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)
      print(list1)  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in list1:
          
        total += int(x[3])
        if x[4] == "food":
          t_food +=int(x[3])
            
        elif x[4] == "entertainment":
          t_entertainment  += int(x[3])
        
        elif x[4] == "business":
          t_business  += int(x[3])
        elif x[4] == "rent":
          t_rent  += int(x[3])
           
        elif x[4] == "emi":
          t_EMI  += int(x[3])
         
        elif x[4] == "Miscellaneous":
          t_other  += int(x[3])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("month.html", texpense = list2, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
         


@app.route("/year")
def year():
      
      
      sql = "SELECT YEAR(DATE),SUM(AMOUNT) FROM EXPENSE WHERE USERID=? GROUP BY YEAR(DATE)"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list2=[]
      texpense = ibm_db.fetch_tuple(stmt)
      while(texpense):
        list2.append(texpense)
        texpense = ibm_db.fetch_tuple(stmt)
      print(list2)


      

      sql = "SELECT * FROM EXPENSE WHERE USERID=? AND YEAR(date)=YEAR(DATE(NOW()))"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list1=[]
      expense = ibm_db.fetch_tuple(stmt)
      while(expense):
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in list1:
        total += int(x[3])
        if x[4] == "food":
          t_food +=int(x[3])
            
        elif x[4] == "entertainment":
          t_entertainment  += int(x[3])
        
        elif x[4] == "business":
          t_business  += int(x[3])
        elif x[4] == "rent":
          t_rent  += int(x[3])
           
        elif x[4] == "emi":
          t_EMI  += int(x[3])
         
        elif x[4] == "Miscellaneous":
          t_other  += int(x[3])
          
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("year.html", texpense = list2, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

if __name__ =='__main__':
    app.run(host='0.0.0.0',debug=True)