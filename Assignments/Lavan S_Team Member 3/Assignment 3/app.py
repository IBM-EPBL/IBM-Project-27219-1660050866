from flask import Flask, render_template, request, redirect,url_for,flash
from datetime import date
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import ibm_db

COS_ENDPOINT = 'https://s3.au-syd.cloud-object-storage.appdomain.cloud';
COS_API_KEY_ID = '8K5gONcRNcXxeZL_enbzJaKhtCH3yrKlaqh8qPl9nMdW';
COS_INSTANCE_CRN = 'crn:v1:bluemix:public:iam-identity::a/cd2180c82e8543168ae1c7fa8ad7fd89::serviceid:ServiceId-19b13c5b-c97c-46f4-ab13-2264b35a85da';

cos = ibm_boto3.resource("s3",
                         ibm_api_key_id=COS_API_KEY_ID,
                         ibm_service_instance_id=COS_INSTANCE_CRN,
                         config=Config(signature_version="oauth"),
                         endpoint_url=COS_ENDPOINT
                         )
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=wjs91839;PWD=icZzyYaQPuzmkROZ", '', '')
sql = "CREATE TABLE IF NOT EXISTS Users (Email varchar(50),Rollno int,Username varchar(50),Password varchar(50))"
stmt = ibm_db.prepare(conn, sql)
ibm_db.execute(stmt)

# conn = ibm_db.connect(
#     )
def get_bucket_contents(bucket_name):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        files = cos.Bucket(bucket_name).objects.all()
        files_names = []
        for file in files:
            files_names.append(file.key)
            print("Item: {0} ({1} bytes).".format(file.key, file.size))
        return files_names
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))
app = Flask(__name__)
@app.route('/')
def index():
    return redirect(url_for('sign_in'))
@app.route('/sign_in')
def sign_in():

    return render_template('sign_in.html')


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/verifyid',methods=['GET', 'POST'])
def verifyid():
    all_users=[]
    if request.method=='POST':
        emailid = request.form['email']
        pwd = request.form['password']
        sql = "SELECT * FROM Users2"
        stmt = ibm_db.exec_immediate(conn, sql)
        users = ibm_db.fetch_both(stmt)
        while users != False:
            all_users.append(users)
            print(all_users)
            users = ibm_db.fetch_both(stmt)
        for user in all_users:
            if emailid == user['EMAIL']:
                if pwd == user['PASSWORD']:
                    files = get_bucket_contents('images-12345')
                    print(files)    
                    return render_template('home.html', files=files)
        return render_template('login_failed.html')


@app.route('/create_id', methods=['GET', 'POST'])
def create_id():
    temp=0



    if request.method == 'POST':
        name = request.form['username']
        emailid = request.form['email']
        pwd = request.form['password']
        sql = "SELECT * FROM users WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, emailid)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            return render_template('user_already_exists.html')
        else:
            insert_sql = "INSERT INTO Users2 VALUES (?,?,?)"
            # sql1 = "CREATE TABLE IF NOT EXISTS users2 (userame varchar(50),Email varchar(50),Password varchar(50),created_date Date)"
            sql1="CREATE TABLE IF NOT EXISTS Users2 (Username varchar(50),Email varchar(50),Password varchar(50))"
            stmt1 = ibm_db.prepare(conn, sql1)
            ibm_db.execute(stmt1)
            
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, emailid)
            ibm_db.bind_param(prep_stmt, 3, pwd)
            # ibm_db.bind_param(prep_stmt, 4, date.today())
            ibm_db.execute(prep_stmt)
            return render_template('id_created.html')






if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
