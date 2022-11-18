import ibm_db
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=764264db-9824-4b7c-82df-40d1b13897c2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=32536;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=dkh61031;PWD=epbaJyxx5Cfi7vTl",'','')
print(conn)
print("connection successful")

sql="SELECT * FROM USERS"
stmt = ibm_db.exec_immediate(conn,sql)
dictionary = ibm_db.fetch_assoc(stmt)
while dictionary!=False:
    print("FUll ROW: ",dictionary)
    dictionary=ibm_db.fetch_assoc(stmt)