import sqlite3
from flask import Flask, render_template, request, g, escape, url_for, redirect, session

DATABASE = './assignment3.db'
app = Flask(__name__)

access_username = ''
isadmin = True

#access_username = 'student_2'
#isadmin = False

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
    print("delete from Remarks where Username='"+user+"' and Ass_id='"+ass_id+"'")
    db_cur.execute("delete from Remarks where Username='"+user+"' and Ass_id='"+ass_id+"'")
    print("update Grades set Mark="+mark+"where Username='"+user+"' and Ass_id='"+ass_id+"'")
    db_cur.execute("update Grades set Mark="+mark+" where Username='"+user+"' and Ass_id='"+ass_id+"'")
    db.commit()

def add_remark(user, name, ass_id, mark, reason):
    db = get_db()
    db_cur = db.cursor()
    print("insert into Remarks values ('"+ user +"','"+ name +"','"+ ass_id +"','"+ mark +"','"+ reason +"')")
    db_cur.execute("insert into Remarks values ('"+ user +"','"+ name +"','"+ ass_id +"','"+ mark +"','"+ reason +"')")
    db.commit()

def remark():
    db = get_db()
    db.row_factory = make_dicts

    remarks_dict = []
    if isadmin == True:
        for want_remark in query_db('select * from Remarks'):
            remarks_dict.append(want_remark)
        db.close()
        return render_template('remark.html', remarks=remarks_dict, admin=isadmin)
    else:
        for want_remark in query_db("select Username, name, Ass_id, Mark from Grades natural join Person where username ='" + access_username +"'"):
            remarks_dict.append(want_remark)
        db.close()
        return render_template('remark.html', remarks=remarks_dict, admin=isadmin)

@app.route('/remark.html', methods=['GET', 'POST'])
def remark_change():           
    if request.method == 'POST':
        if request.form.get('Remark') == 'Remark':
            if isadmin == True:
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


@app.route('/grade')
def grade():
    db = get_db()
    db.row_factory = make_dicts
    Assid = request.args.get('Assignment')
    grades = []
    grades_search=[]
    print(Assid)
    if Assid == None:
        if isadmin == True:
            for studentGrade in query_db('select * from Grades'):
                grades.append(studentGrade)
            db.close()
            return render_template('grade.html', grade=grades, admin=isadmin)
        else:
            for studentGrade in query_db('select * from Grades where Username =? ' ,[access_username]):
                grades.append(studentGrade)
            db.close()
            return render_template('grade.html', grade=grades)
    else:
        if isadmin == True:
            for studentGrade in query_db('select * from Grades where Ass_id=?' , [Assid]):
                grades.append(studentGrade)
            db.close()
            return render_template('grade.html', grade=grades, admin=isadmin)
        else:
            grade = query_db('select * from Grades where Username==? and Ass_id=?',[access_username,Assid], one=True)
            db.close()
            return render_template('grade.html', grade=[grade])
    

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
                       return render_template('grade.html', grade=grades)


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

 
