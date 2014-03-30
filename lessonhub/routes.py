from flask import Flask, g, session, jsonify, Response, request, json, render_template, redirect, current_app
from lessonhub import app
from lessonhub import api

#view homepage of user
@app.route('/user')
def home():
	user_info = api.get_user(154)
	user = {}
	user['name'] = user_info['name']
	user['username'] = ""
	user['followers_count'] = len(user_info['followers'])
	user['followees_count'] = len(user_info['following'])
	return render_template("../templates/curriculum.html", user=user)
	#user_id, firstname, last name
	#title, subject, date created, date updated


@app.route('/login', methods=['GET'])
def login_page():
    return render_template("login.html")

@app.route('/check_login', methods=['POST'])
def check_login():
    session['username'] = request.form['username']
    return redirect('/user')
    

#view profile of other user
@app.route('/user/<int:user_id>')
def user(user_id):
	user_info = api.get_user(session["user_id"])
	#first name, last name, affiliation, # of folo/lew
	return render_template("user.html", user_info)

#view curriculum
@app.route('/curriculum/<int:curriculum_id>')
def curriculum(curriculum_id):
	#//title, subject, author, created/updated
	return render_template("curriculum.html")

@app.route('/lesson/<int:lesson_id>')
def lesson(lesson_id):
	return render_template("lesson.html")

@app.route("/curriculum/add_curriculum")
def add_curriculum():
	return render_template("add_curriculum.html")


@app.route("/curriculum/<int:curriculum_id>/add_lesson")
def add_lesson():
	return render_template("add_lesson.html")
