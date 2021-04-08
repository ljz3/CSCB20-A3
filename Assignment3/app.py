import sqlite3
from flask import Flask, render_template, request, g, escape, url_for, redirect, session

DATABASE = './assignment3.db'
app = Flask(__name__)
app.secret_key = 'any random string'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()    


def remove_remark(user, ass_id, mark):
    db = get_db()
    db_cur = db.cursor()
    #print("delete from Remarks where Username='"+user+"' and Ass_id='"+ass_id+"'")
    db_cur.execute("delete from Remarks where Username='"+user+"' and Ass_id='"+ass_id+"'")
    #print("update Grades set Mark="+mark+"where Username='"+user+"' and Ass_id='"+ass_id+"'")
    db_cur.execute("update Grades set Mark="+mark+" where Username='"+user+"' and Ass_id='"+ass_id+"'")
    db.commit()

def add_remark(user, name, ass_id, mark, reason):
    db = get_db()
    db_cur = db.cursor()
    #print("insert into Remarks values ('"+ user +"','"+ name +"','"+ ass_id +"','"+ mark +"','"+ reason +"')")
    db_cur.execute("insert into Remarks values ('"+ user +"','"+ name +"','"+ ass_id +"','"+ mark +"','"+ reason +"')")
    db.commit()

def remark():
    db = get_db()
    db.row_factory = make_dicts

    remarks_dict = []
    if session['isadmin'] == True:
        for want_remark in query_db('select * from Remarks'):
            remarks_dict.append(want_remark)
        db.close()
        return render_template('remark.html', remarks=remarks_dict, admin=session['isadmin'])
    else:
        for want_remark in query_db("select Username, name, Ass_id, Mark from Grades natural join Person where username ='" + session['access_username'] +"'"):
            remarks_dict.append(want_remark)
        db.close()
        return render_template('remark.html', remarks=remarks_dict, admin=session['isadmin'])

@app.route('/')
def default():
    session['access_username'] = ''
    session['isadmin'] = False
    return render_template('login.html')


@app.route('/remark.html', methods=['GET', 'POST'])
def remark_change():           
    if request.method == 'POST':
        if request.form.get('Remark') == 'Remark':
            if session['isadmin'] == True:
                user = request.form.get('Username')
                ass_id = request.form.get('Ass_id')
                new_mark = request.form.get('new_mark')
                remove_remark(user, ass_id, new_mark)
            else:
                user = request.form.get('Username')
                name = request.form.get('name')
                ass_id = request.form.get('Ass_id')
                mark = request.form.get('Mark')
                reason = request.form.get('Reason')
                add_remark(user, name, ass_id, mark, reason)
            return remark()
        else:
            return remark()
    else:
        return remark()

@app.route('/logout.html')
def logout():
    session['isadmin'] == None
    session['access_username'] = ''
    return render_template("logout.html")

@app.route('/add_grade.html', methods=['GET', 'POST'])
def add_grade():
    db = get_db()
    db.row_factory = make_dicts
    if request.method == 'POST':
        Assid = request.form.get('Assignment')
        Name = request.form.get('Name')
        Grade = request.form.get('Grade')

        db_cur = db.cursor()
        db_cur.execute("insert into Grades values ('"+ Name +"','"+ Assid +"','"+ Grade +"')")
        db.commit()
    return render_template('add_grade.html', isadmin = session['isadmin'])

@app.route('/grade')
@app.route('/grade.html')
def grade():
    db = get_db()
    db.row_factory = make_dicts
    Assid = request.args.get('Assignment')
    grades = []
    grades_search=[]

    if Assid == None:
        if session['isadmin'] == True:
            for studentGrade in query_db('select * from Grades'):
                grades.append(studentGrade)
            db.close()
            return render_template('grade.html', grade=grades, admin=session['isadmin'])
        else:
            for studentGrade in query_db('select * from Grades where Username =? ' ,[session['access_username']]):
                grades.append(studentGrade)
            db.close()
            return render_template('grade.html', grade=grades)
    else:
        if session['isadmin'] == True:
            for studentGrade in query_db('select * from Grades where Ass_id=?' , [Assid]):
                grades.append(studentGrade)
            db.close()
            return render_template('grade.html', grade=grades, admin=session['isadmin'])
        else:
            grade = query_db('select * from Grades where Username==? and Ass_id=?',[session['access_username'],Assid], one=True)
            db.close()
            return render_template('grade.html', grade=[grade])


@app.route('/login.html',methods=['GET','POST'])
@app.route('/login')
def login():
    db = get_db()
    db.row_factory = make_dicts
    login_dict = []
    if request.method=='POST':
        if request.form.get("signup"):
            return render_template("signup.html")
        elif request.form.get("signin"):
            user = query_db("SELECT * FROM Login NATURAL JOIN Person WHERE Username = ? AND Password = ?",
                            [request.form['username'], request.form['password']])
            
            if bool(user) is True:
                session['access_username'] = request.form['username']
                session['isadmin'] = bool(user[0]['type'])
                print(session['isadmin'])
                return render_template('index.html')
            else:
                return render_template('login.html')
    elif request.method=='GET':
        return render_template('login.html')

    # return render_template('login.html')

@app.route('/signup.html',methods=['GET','POST'])
def signup():
    print("here")
    db = get_db()
    db.row_factory = make_dicts
    signup_dict = []
    if request.method=='POST':
        if request.form.get("su_student"):
            username = request.form.get('username')
            password = request.form.get('password')
            name = request.form.get('name')
            add_user(username, password, name, '0')
            session['isadmin'] == False
            session['access_username'] = username
        elif request.form.get("su_instructor"):
            username = request.form.get('username')
            password = request.form.get('password')
            name = request.form.get('name')
            add_user(username, password, name, '1')
            session['isadmin'] == True
            session['access_username'] = username
        return render_template("login.html")
    elif request.method=='GET':
        return render_template('signup.html')
    

def add_user(username, password, name, type_of):
    db = get_db()
    db_cur = db.cursor()
    db_cur.execute("insert into Login values ('"+ username +"','"+ password +"')")
    db.commit()
    db = get_db()
    db_cur = db.cursor()
    db_cur.execute("insert into Person values ('"+ username +"','"+ name +"','"+ type_of +"')")
    db.commit()


@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/assignments.html')
def assignments():
    return render_template('assignments.html')

@app.route('/courseteam.html')
def courseteam():
    return render_template('courseteam.html')

def add_feedback(name, like, dislike, see):
    db = get_db()
    db_cur = db.cursor()
    #print("insert into Remarks values ('"+ user +"','"+ name +"','"+ ass_id +"','"+ mark +"','"+ reason +"')")
    db_cur.execute("insert into Feedbacks values ('"+ name +"','"+ like +"','"+ dislike +"','"+ see +"')")
    db.commit()

@app.route('/feedback.html', methods=['GET','POST'])
def feedback():
    db = get_db()
    db.row_factory = make_dicts
    feedback_dict = []
    if session['isadmin'] == True:
        for want_remark in query_db('select * from Feedbacks'):
            feedback_dict.append(want_remark)
        db.close()
        return render_template('feedback.html', feedbacks=feedback_dict, admin=session['isadmin'])
    else:
        if request.method == 'POST':
            if request.form.get('feedback') == 'Submit Feedback':
                name = request.form.get('name')
                like = request.form['like']
                dislike = request.form['dislike']
                see = request.form['see']
                add_feedback(name, like, dislike, see)
    return render_template('feedback.html', feedbacks=feedback_dict, admin=session['isadmin'])

@app.route('/labs.html')
def labs():
    return render_template('labs.html')

@app.route('/markus.html')
def markus():
    return render_template('markus.html')

@app.route('/piazza.html')
def piazza():
    return render_template('piazza.html')

@app.route('/syllabus.html')
def syllabus():
    return render_template('syllabus.html')

 
