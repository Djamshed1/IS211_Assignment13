#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Week 13 Assignment 13"""

import sqlite3
from flask import Flask, request, session, g, redirect, render_template, flash

DATABASE = 'hw13.db'
DEBUG = True
SECRET_KEY = 'admin key'
USERNAME = 'uadmin'
PASSWORD = 'padmin'

app = Flask(__name__)
app.config.from_object(__name__)

def init_db():
    with app.app_context():
        db = connect_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()
        
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != USERNAME:
            error = 'Invalid username! Please enter correct username'
            return render_template('login.html', error=error)
        elif request.form['password'] != PASSWORD:
            error = 'Invalid password! Please enter correct password'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            return redirect('/dashboard')
    else:
        return render_template('login.html', error=error)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if session['logged_in'] != True:
        flash("You are not logged in. Please login with your valid username and password")
        return redirect('/login')
    else:
        x = g.db.execute('select ID, FIRST_NAME, LAST_NAME from STUDENTS order by LAST_NAME ASC')
        students = [dict(student_id=row[0], first_name=row[1], last_name=row[2]) for row in x.fetchall()]
        x = g.db.execute('select ID, SUBJECT, QUESTION_COUNT, QUIZ_DATE from QUIZZES order by ID asc')
        quizzes = [dict(quiz_id=row[0], subject=row[1], question_count=row[2], date=row[3]) for row in x.fetchall()]
        return render_template("dashboard.html", students=students, quizzes=quizzes)


@app.route('/student/add', methods=['GET', 'POST'])
def adding_students():
    if session['logged_in'] != True:
        flash("You are not logged in. Please login with your valid username and password.")
        return redirect('/login')
    else:
        if request.method == 'GET':
            return render_template('adding_students.html')
        elif request.method == 'POST':
            if request.form['first_name'] == "":
                flash("First Name, Try Again")
                return redirect('/student/add')
            elif request.form['last_name'] == "":
                flash("Last Name, Try Again")
                return redirect('/student/add')
            else:
                try:
                    g.db.execute('insert into STUDENTS (FIRST_NAME, LAST_NAME) values (?,?)',
                                 (request.form['first_name'], request.form['last_name']))
                    g.db.commit()
                    return redirect('/dashboard')
                except:
                    flash("Error Recording Results")
                    return redirect('/student/add')


@app.route('/quiz/add', methods=['GET', 'POST'])
def adding_quiz():
    if session['logged_in'] != True:
        flash("You are not logged in. Please login with your valid username and password.")
        return redirect('/login')
    else:
        if request.method == 'GET':
            return render_template('adding_quiz.html')
        elif request.method == 'POST':
            if request.form['subject'] == "":
                flash("Quiz Subject, Try Again")
                return redirect('/quiz/add')
            else:
                try:
                    g.db.execute('insert into QUIZZES (SUBJECT, QUESTION_COUNT, QUIZ_DATE) values (?,?,?)',
                                 (request.form['subject'], request.form['question_count'], request.form['date']))
                    g.db.commit()
                    return redirect('/dashboard')
                except:
                    flash("Error Recording Results")
                    return redirect('/quiz/add')


@app.route('/student/<id>', methods=['GET'])
def student_quiz(id):
    if session['logged_in'] != True:
        flash("You are not logged in. Please login with your valid username and password.")
        return redirect('/login')
    else:
        x = g.db.execute('select FIRST_NAME, LAST_NAME from STUDENTS where ID = ?', (id))
        namelist = x.fetchall()[0]
        studentname = namelist[0] + " " + namelist[1]
        x = g.db.execute('select QUIZ_ID, SCORE from RESULTS where STUDENT_ID = ?', id)
        results = [dict(quiz_id=row[0], score=row[1]) for row in x.fetchall()]
        return render_template('results.html', results=results, studentname=studentname)


@app.route('/results/add', methods=['GET', 'POST'])
def adding_results():
    if session['logged_in'] != True:
        flash("You are not logged in. Please login with your valid username and password.")
        return redirect('/login')
    else:
        if request.method == 'GET':
            x = g.db.execute('select ID, SUBJECT from QUIZZES')
            quizzes = [dict(quiz_id=row[0], subject=row[1]) for row in x.fetchall()]
            x = g.db.execute('select ID, FIRST_NAME, LAST_NAME from STUDENTS')
            students = [dict(student_id=row[0], studentname=row[1] + " " + row[2]) for row in x.fetchall()]
            return render_template('adding_results.html', quizzes=quizzes, students=students)
        elif request.method == 'POST':
            try:
                g.db.execute('insert into RESULTS (STUDENT_ID, QUIZ_ID, SCORE) values (?, ?, ?)',
                             (request.form['student_id'], request.form['quiz_id'], request.form['score']))
                g.db.commit()
                flash("Quiz Results Updated")
                return redirect("/dashboard")

            except:
                flash("Recording Data Error")
                return redirect("/results/add")


if __name__ == '__main__':
    app.run()
