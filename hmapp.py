from flask import Flask,flash,redirect,render_template,url_for,request,session
from flask_session import Session
from flask_mysqldb import MySQL
from datetime import date
from datetime import datetime
import smtplib
app=Flask(__name__)
app.secret_key='*67@hjyjhk'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Admin'
app.config['MYSQL_DB']='hms'
Session(app)
mysql=MySQL(app)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/adminregister', methods=["GET","POST"])
def registration():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        email=request.form.get('email')
        passcode=request.form.get('passcode')
        #define college code
        code='sdmsmk$#23'
        if code==passcode:
            cursor=mysql.connection.cursor()
            cursor.execute('SELECT email from admin')
            edata=cursor.fetchall()
            #print(data)
            if (email,) in edata:
                flash('Email id already  exists')
                return render_template('registration.html')
        cursor=mysql.connection.cursor()
        cursor.execute('insert into admin(username,password,email,passcode) values(%s,%s,%s,%s)',[username,password,email,passcode])
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template('Registration.html')
@app.route('/login')
def login():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT username,password from admin')
    books=cursor.fetchall()
    cursor.close()
    return render_template('Admin-login.html')
@app.route('/validate',methods=['POST'])
def validate():
    username=request.form['username']
    password=request.form['password']
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT username,password from admin')
    data=cursor.fetchall()[0]
    userid=data[0]
    password=data[1]
    cursor.close()
    if username==username and password==password:
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
        mobile=request.form['mobileno']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into students(Id,Name,Section,roomno,mobile) values(%s,%s,%s,%s,%s)',[id1,name,section,room,mobile])
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('studentrecord'))
    return render_template('Add-student.html')
@app.route('/studentrecord',methods=['GET','POST'])
def studentrecord():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from students')
    data=cursor.fetchall()
    cursor.close()
    
    return render_template('Student Record.html',data=data)
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
        room =request.form['Room']
        mobile=request.form['mobile']
        section=request.form['section']
        cursor.execute('update students set Name=%s,roomno=%s,mobile=%s,section=%s where id=%s',[name,room,mobile,section,id])
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
    cursor.execute('SELECT date,id,name,roomno,section,mobile,checkin,checkout from records')
    std_records=cursor.fetchall()
    cursor.close()
    if request.method=='POST':
        cursor=mysql.connection.cursor()
        Id=request.form['empCode']
        today=date.today()
        day=today.day
        month=today.month
        year=today.year
        today_date=datetime.strptime(f'{year}-{month}-{day}','%Y-%m-%d')
        date_today=datetime.strftime(today_date,'%Y-%m-%d')
        Name=request.form['name']
        section=request.form['section']
        roomno=request.form['roomno']
        mobileno=request.form['mobileno']
        cursor.execute('select count(*) from records where Id=%s and date=%s',[Id,date_today])
        count=int(cursor.fetchone()[0])
        if Id=="" or Name=="" or section=="" or roomno=="" or mobileno=="":
            flash('Select The student Id first')
        elif count>=1:
            flash('The student already gone outside')
        else:
            cursor=mysql.connection.cursor()
            cursor.execute('insert into records(Id,Name,section,roomno,mobile,checkin,checkout,date) values(%s,%s,%s,%s,%s,%s,%s,%s)',[Id,Name,section,roomno,mobileno,None,None,date_today])
            mysql.connection.commit()
            cursor.execute('SELECT date,Id,Name,section,roomno,mobile,checkin,checkout from records')
            std_records=cursor.fetchall()
            cursor.close()
    return render_template('Check in-page.html',data1=data1,data=data,details=details,std_records=std_records)
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
@app.route('/Visitorrecord',methods=['GET','POST'])
def Visitorrecord():
    cursor=mysql.connection.cursor()
    cursor.execute('select * from visitor')
    data=cursor.fetchall()
    cursor.close()
    return render_template('visitorrecords.html',data=data)
@app.route('/addvisitor',methods=['GET','POST'])
def addvisitor():
    if request.method=='POST':
        sid=request.form['sid']
        visitorname=request.form['visitorname']
        visitormobile=request.form['visitormobile']
        roomno=request.form['roomno']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into visitor(sid,visitorname,visitormobile,roomno) values(%s,%s,%s,%s)',[sid,visitorname,visitormobile,roomno])
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('Visitorrecord'))
    return render_template('hostelrecords.html')
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
@app.route('/visitorcheckin',methods=['GET','POST'])
def visitorcheckin():
    details=None
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from visitor')
    data=cursor.fetchall()
    data1=request.args.get('name') if request.args.get('name') else 'empty'
    print(data1)
    cursor.execute('SELECT * from visitor where sid=%s',[data1])
    details=cursor.fetchone()
    cursor.execute('SELECT date,Id,visitorname,visitormobile,roomno,checkin,checkout from visitorrecords')
    std_records=cursor.fetchall()
    cursor.close()
    if request.method=='POST':
        cursor=mysql.connection.cursor()
        sid=request.form['empCode']
        today=date.today()
        day=today.day
        month=today.month
        year=today.year
        today_date=datetime.strptime(f'{year}-{month}-{day}','%Y-%m-%d')
        date_today=datetime.strftime(today_date,'%Y-%m-%d')
        visitorname=request.form['visitorname']
        visitormobile=request.form['visitormobile']
        roomno=request.form['roomno']
        cursor.execute('select count(*) from visitor where sid=%s and date=%s',[sid,date_today])
        count=int(cursor.fetchone()[0])
        if sid=="" or visitorname=="" or visitormobile=="" or roomno=="" or date=="":
            flash('Select The student Id first')
        elif count>=1:
            flash('The student already gone outside')
        else:
            cursor=mysql.connection.cursor()
            cursor.execute('insert into visitorrecords(Id,visitorname,visitormobile,roomno,checkin,checkout,date) values(%s,%s,%s,%s,%s,%s,%s)',[sid,visitorname,visitormobile,roomno,None,None,date_today])
            mysql.connection.commit()
            cursor.execute('select date,Id,visitorname,visitormobile,roomno,checkin,checkout from visitorrecords')
            std_records=cursor.fetchall()
            cursor.close()
    return render_template('visitorcheckin.html',data1=data1,data=data,details=details,std_records=std_records)
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
app.run(debug=True)                                                                                         


        
        

    

app.py
Displaying app.py.
