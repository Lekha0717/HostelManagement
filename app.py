from flask import Flask,flash,redirect,render_template,url_for,request,session
from flask_session import Session
from flask_mysqldb import MySQL
from datetime import date
from datetime import datetime
import smtplib
from otp import genotp
from cmail import sendmail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
app=Flask(__name__)
app.secret_key='*67@hjyjhk'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='hms'
Session(app)
mysql=MySQL(app)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        userid=request.form['userid']
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        code=request.form['passcode']
        #define college code
        ccode='sdmsmkpbsc$#23'
        if ccode==code:
            cursor=mysql.connection.cursor()
            cursor.execute('select userid from admin')
            data=cursor.fetchall()
            cursor.execute('SELECT email from admin')
            edata=cursor.fetchall()
            #print(data)
            if (userid,) in data:
                flash('User already already exists')
                return render_template('Registration.html')
            if (email,) in edata:
                flash('Email id already already exists')
                return render_template('Registration.html')
    
            cursor.close()
            otp=genotp()
            subject='thanks for register'
            body=f'use this otp register{otp}'
            sendmail(email,subject,body)
            return render_template('otp.html',otp=otp,userid=userid,username=username,password=password,email=email)
        else:
            flash('Invalid college code')
            return render_template('registration.html') 
    return render_template('Registration.html')
@app.route('/otp/<otp>/<userid>/<username>/<password>/<email>',methods=['GET','POST'])
def otp(otp,userid,username,password,email):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            cursor.execute('insert into admin values(%s,%s,%s,%s)',(userid,username,password,email))
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,userid=userid,username=username,password=password,email=email)

@app.route('/login')
def login():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT userid,password from admin')
        books=cursor.fetchall()
        cursor.close()
    return render_template('Admin-login.html')
@app.route('/validate',methods=['POST'])
def validate():
    userid=request.form['userid']
    password=request.form['password']
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT userid,password from admin')
    data=cursor.fetchall()[0]
    userid=data[0]
    password=data[1]
    cursor.close()
    if userid==userid and password==password:
        return redirect(url_for('Adminpage'))
    else:
        return redirect(url_for('Adminpage'))
@app.route('/adminpage',methods=['GET','POST'])
def Adminpage():
    return render_template('adminhomepage.html')
@app.route('/addstudent',methods=['GET','POST'])
def addstudent():
    if request.method=='POST':
        id1=request.form['id1']
        name=request.form['name']
        section=request.form['section']
        room=request.form['roomno']
        mobile=request.form['mobile']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into students(Id,Name,Section,Roomno,Mobile) values(%s,%s,%s,%s,%s)',[id1,name,section,room,mobile])
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('studentrecord'))
    return render_template('Add-students.html')
@app.route('/studentrecord',methods=['GET','POST'])
def studentrecord():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from students')
    data=cursor.fetchall()
    cursor.close()
    
    return render_template('Student records.html',data=data)

@app.route('/delete/<id>')
def delete(id):
    cursor=mysql.connection.cursor()
    cursor.execute('delete from students where id=%s',[id])
    mysql.connection.commit()
    cursor.close()
    flash('student delete successfully')
    return redirect(url_for('studentrecord'))
@app.route('/update/<id>',methods=['GET','POST'])
def update(id):
    cursor=mysql.connection.cursor()
    cursor.execute('select * from students where id=%s',[id])
    data=cursor.fetchone()
    if request.method=='POST':
        id1=request.form['id']
        name=request.form['name']
        section=request.form['section']
        room =request.form['Room']
        mobile=request.form['mobile']
        cursor.execute('update students set Name=%s,Section=%s,Roomno=%s,Mobile=%s where id=%s',[name,section,room,mobile,id1])
        mysql.connection.commit()
        return redirect(url_for('studentrecord'))
    return render_template('update.html',data=data)
@app.route('/checkin',methods=['GET','POST'])
def checkin():
    details=None
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from students')
    data=cursor.fetchall()
    data1=request.args.get('name') if request.args.get('name') else 'empty'
    print(data1)
    cursor.execute('SELECT * from students where id=%s',[data1])
    details=cursor.fetchone()
    cursor.execute('SELECT * from records')
    std_records=cursor.fetchall()
    print(std_records)
    cursor.close()
    if request.method=='POST':
        cursor=mysql.connection.cursor()
        Id=request.form['empCode']
        today=date.today()
        day=today.day
        month=today.month
        year=today.year
        date_today=f'{year}-{month}-{day}'
        Name=request.form['name']
        section=request.form['Section']
        roomno=request.form['Roomno']
        mobileno=request.form['Mobileno']
        cursor.execute('select count(*) from records where Id=%s and date=%s',[Id,date_today])
        count=int(cursor.fetchone()[0])
        if Id=="" or Name=="" or section=="" or roomno=="" or mobileno=="":
            flash('Select The student Id first')
        elif count>=1:
            flash('The student already gone outside')
        else:
            cursor=mysql.connection.cursor()
            cursor.execute('insert into records(Id,Name,Section,Roomno,Mobileno,date) values(%s,%s,%s,%s,%s,%s)',[Id,Name,section,roomno,mobileno,date_today])
            mysql.connection.commit()
            cursor.execute('SELECT * from records')
            std_records=cursor.fetchall()
            cursor.close()
    return render_template('Check in-page.html',data1=data1,data=data,details=details,std_records=std_records)
@app.route('/checkout',methods=['GET','POST'])
def checkout():
    details=None
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from students')
    data=cursor.fetchall()
    data1=request.args.get('name') if request.args.get('name') else 'empty'
    print(data1)
    cursor.execute('SELECT * from students where id=%s',[data1])
    details=cursor.fetchone()
    cursor.execute('SELECT * from studentcheckout')
    std_records=cursor.fetchall()
    print(std_records)
    cursor.close()
    if request.method=='POST':
        cursor=mysql.connection.cursor()
        Id=request.form['empCode']
        today=date.today()
        day=today.day
        month=today.month
        year=today.year
        date_today=f'{year}-{month}-{day}'
        Name=request.form['name']
        section=request.form['section']
        roomno=request.form['roomno']
        mobileno=request.form['mobileno']
        cursor.execute('select count(*) from studentcheckout where Id=%s and date=%s',[Id,date_today])
        count=int(cursor.fetchone()[0])
        if Id=="" or Name=="" or section=="" or roomno=="" or mobileno=="":
            flash('Select The student Id first')
        elif count>=1:
            flash('The student already gone outside')
        else:
            cursor=mysql.connection.cursor()
            cursor.execute('insert into studentcheckout(Id,Name,Section,Roomno,Mobile,date) values(%s,%s,%s,%s,%s,%s)',[Id,Name,section,roomno,mobileno,date_today])
            mysql.connection.commit()
            cursor.execute('SELECT * from studentcheckout')
            std_records=cursor.fetchall()
            cursor.close()
    return render_template('Check out page.html',data1=data1,data=data,details=details,std_records=std_records)
@app.route('/checkoutupdate/<date>/<id1>')
def checkoutupdate(date,id1):
    cursor=mysql.connection.cursor()
    cursor.execute('update records set checkout=current_timestamp() where date=%s and Id=%s',[date,id1])
    mysql.connection.commit()
    return redirect(url_for('checkin'))
@app.route('/checkinupdate/<date>/<id1>')
def checkinupdate(date,id1):
    cursor=mysql.connection.cursor()
    cursor.execute('update records set checkin=current_timestamp() where date=%s and Id=%s',[date,id1])
    mysql.connection.commit()
    return redirect(url_for('checkin'))

@app.route('/Delete/<sid>')
def Delete(sid):
    cursor=mysql.connection.cursor()
    cursor.execute('Delete from visitor where sid=%s',[sid])
    mysql.connection.commit()
    cursor.close()
    flash('student delete successfully')
    return redirect(url_for('Visitorrecord'))
@app.route('/Update/<sid>',methods=['GET','POST'])
def Update(sid):
    cursor=mysql.connection.cursor()
    cursor.execute('select * from visitor where sid=%s',[sid])
    data=cursor.fetchone()
    if request.method=='POST':
        sid=request.form['sid']
        visitorname=request.form['visitorname']
        visitormobile=request.form['visitormobile']
        roomno =request.form['roomno']
        cursor.execute('Update visitor set visitorname=%s,visitormobile=%s,roomno=%s where sid=%s',[visitorname,visitormobile,roomno,sid])
        mysql.connection.commit()
        return redirect(url_for('Visitorrecord'))
    return render_template('visitorupdate.html',data=data)
@app.route('/Checkoutupdate/<date>/<id1>')
def Checkoutupdate(date,id1):
    cursor=mysql.connection.cursor()
    cursor.execute('update visitorrecords set checkout=current_timestamp() where date=%s and Id=%s',[date,id1])
    mysql.connection.commit()
    return redirect(url_for('visitorcheckin'))
@app.route('/Checkinupdate/<date>/<id1>')
def Checkinupdate(date,id1):
    cursor=mysql.connection.cursor()
    cursor.execute('update visitorrecords set checkin=current_timestamp() where date=%s and Id=%s',[date,id1])
    mysql.connection.commit()
    return redirect(url_for('visitorcheckin'))

@app.route('/forgetpassword',methods=['GET','POST'])
def forget():#after clicking the forget password
    if request.method=='POST':
        userid=request.form['userid']# store the id in the rollno
        cursor=mysql.connection.cursor()#connection to mysql
        cursor.execute('select userid from admin')# fetch the rollno data in the table students
        data=cursor.fetchall()#fetching all the rollno data and store it in the "data" variable 
        if(int(userid),) in data:# if the given rollno of the user is present in tha database->data
            cursor.execute('select email from admin where userid=%s',[userid])#it fetches email related to the rollno 
            data=cursor.fetchone()[0]#fetch the only one email related to the rollno 
            print(data)
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the password using-{request.host+url_for("createpassword",token=token(userid,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user id'
    return render_template('forgot.html')
@app.route('/checkoutvisitor/<id1>')
def checkoutvisitor(id1):
    cursor=mysql.connection.cursor()
    cursor.execute('update visitor set checkout=current_timestamp() where Studentid=%s',[id1])
    mysql.connection.commit()
    return redirect(url_for('visitor'))
@app.route('/checkinvisitor/<id1>')
def checkinvisitor(id1):
    cursor=mysql.connection.cursor()
    cursor.execute('update visitor set checkin=current_timestamp() where Studentid=%s',[id1])
    mysql.connection.commit()
    return redirect(url_for('visitor'))
@app.route('/visitor',methods=['GET','POST'])
def visitor():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from students')
    data=cursor.fetchall()
    cursor.execute('Select * from visitor')
    details=cursor.fetchall()
    cursor.close()
    if request.method=="POST":
        Studentid=request.form['Studentid']
        name=request.form['Name']
        mobilenumber=request.form['MobileNumber']
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO visitor(Studentid,Name,MobileNumber) values(%s,%s,%s)',[Studentid,name,mobilenumber])
        cursor.execute('Select * from visitor')
        details=cursor.fetchall()
        mysql.connection.commit()
    return render_template('visitorcheckin.html',data=data,details=details)
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):#to create noe password and conform the password
        try:
            s=Serializer(app.config['SECRET_KEY'])
            userid=s.loads(token)['username']
            if request.method=='POST':
                npass=request.form['npassword']
                cpass=request.form['cpassword']
                if npass==cpass:
                    cursor=mysql.connection.cursor()
                    cursor.execute('update admin set password=%s where userid=%s',[npass,userid])
                    mysql.connection.commit()
                    return 'Password reset Successfull'
                else:
                    return 'Password mismatch'
            return render_template('newpassword.html')
        except Exception as e:
            print(e)
            return 'Link expired try again'
app.run(debug=True)                                                                                         


        
        

    
