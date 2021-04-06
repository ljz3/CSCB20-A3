import sqlite3
from flask import Flask, render_template, request, g, escape, url_for, redirect, session

DATABASE = './assignment3.db'
app = Flask(__name__)

access_username = ''
isadmin = True

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

@app.route('/remark.html')
def remark():
    db = get_db()
    db.row_factory = make_dicts

    remarks_dict = []
    if isadmin == True:
        for want_remark in query_db('select * from Remarks'):
            remarks_dict.append(want_remark)
        db.close()
        return render_template('remark.html', remarks=remarks_dict)
    else:
        for want_remark in query_db('select * from Remarks where userneme =' + access_username):
            remarks_dict.append(want_remark)
        db.close()
        return render_template('remark.html', remarks=remarks_dict)
    if request.method == 'POST':
        if request.form['submit_button'] == 'Remark':
            return render_template('home.html')
            
    


@app.route('/grade')
def get_assid_grade():
    db = get_db()
    db.row_factory = make_dicts
    Assid = request.args.get('Assignment')
    if isadmin == True:
        grade = query_db('select * from Grades where Username==' + access_username + 'and Ass_id==?' , [Assid], one=True)
        db.close()
        return render_template('grade.html', grade=[grade])


@app.route('/')
def grade():
    db = get_db()
    db.row_factory = make_dicts

    grades = []
    if isadmin == True:
        for studentGrade in query_db('select * from Grades where Username==?' 
                                                        ,[access_username]):
            grades.append(studentGrade)
        db.close()
        return render_template('grade.html', grade=grades)
    

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        sql = """
	    SELECT *
	    FROM Login NATURAL JOIN Person
	    """
        results = query_db(sql, args=(), one=False)
        for result in results:
            if result[1]==request.form['Username']:
                if result[2]==request.form['Password']:
                    isadmin = result[3]
        return render_template('index.html')


@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/assignments.html')
def assignments():
    return render_template('assignments.html')

@app.route('/courseteam.html')
def courseteam():
    return render_template('courseteam.html')

@app.route('/feedback.html')
def feedback():
    return render_template('feedback.html')

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

@app.route('/login.html')
def loginpg():
    return render_template('login.html')
 
