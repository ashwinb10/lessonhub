from flask import Flask, url_for, g, session, jsonify, Response, request, json, render_template, redirect, current_app
from lessonhub import app, db
from lessonhub import api
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
from bson.objectid import ObjectId


#view homepage of user

@app.route('/')
def home():
	if('username' in session):
		user_info = db.users.find_one({'_id': ObjectId(session["user_id"])})
		print user_info
		user = {}
		user['name'] = session["name"]
		user['username'] = session["username"]
		user['userid'] = session["user_id"]
		user['followers_count'] = len(user_info['followers'])
		user['followees_count'] = len(user_info['following'])
		print user
		return render_template("curriculum.html", user=user)
	else:
		return redirect("/login")
	#user_id, firstname, last name
	#title, subject, date created, date updated


@app.route('/login', methods=['GET'])
def login_page():
	d = {}
	return render_template("login.html", errors = d)

@app.route('/check_login', methods=['POST'])
def check_login():
	username = request.form["username"]
	password = request.form["password"]
	user_object = db.users.find_one({"username": username})
	print user_object
	if(user_object):
		if (check_password_hash(user_object['password'], password)):
			session['username'] = username
			session['name'] = user_object['name']
			print user_object['_id']
			session['user_id'] = str(user_object['_id'])
			session['logged'] = True
			print "here too"
			return redirect('/')
		return render_template("login.html", errors = {"error": 1})
	return render_template("login.html", errors={"error": 2})

@app.route('/signup', methods=['GET'])
def signup_page():
	d = {}
	return render_template("signup.html", errors = d)

@app.route('/create_user', methods=['POST'])
def create_user():
    name = request.form['name']
    affiliation = request.form['affiliation']
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    user = { 
        'name': name,
        'affiliation': affiliation,
        'username': username,
        'password': password,
        'followers' : [],
        'following' : []
    }
    user_id = db.users.insert(user)
    print user_id
    return render_template("login.html")

@app.route('/logout', methods=['GET'])
def logout():
	session['username']= ""
	session['user_id'] = ""
	session['name'] = ""
	session['logged'] = False
	return render_template("login.html", errors = {})

#view profile of other user
@app.route('/user/<int:user_id>')
def user(user_id):
	user_info = api.get_user(user_id)
	#first name, last name, affiliation, # of folo/lew
	return render_template("user.html", user_info)

#view curriculum
@app.route('/curriculum/<int:curriculum_id>')
def curriculum(curriculum_id):
	#//title, subject, author, created/updated
	return render_template("lessons.html")

@app.route('/lesson/<int:lesson_id>')
def lesson(lesson_id):
	return render_template("lesson.html")

@app.route("/curriculum/add_curriculum")
def add_curriculum():
	return render_template("add_curriculum.html")


@app.route("/curriculum/<int:curriculum_id>/add_lesson")
def add_lesson():
	return render_template("add_lesson.html")

def fork_lesson(lesson, curriculum_id):
	new_lesson = {
		'name': lesson.name,
		'subtitle': lesson.subtitle,
		'expected_duration': lesson.expected_duration,
		'parent': lesson.lesson_id,
		'children': [],
		'content': lesson.content,
		'curriculum_id': curriculum_id,
		'date_created': datetime.utcnow(),
		'last_updated': datetime.utcnow(),
		'num_forks': 0,
		'original_author': lesson.original_author,
		'comments': []
	}

	new_lesson_id = db.lessons.insert(new_lesson)
	lesson.children.append(new_lesson_id)
	return new_lesson_id

@app.route("/fork/curriculum/<int:curriculum_id>", methods=["POST"])
def fork_curriculum(curriculum_id):
    old_curriculum = db.curricula.find_one({'_id': curriculum_id})

    new_curriculum = {
    	"title": old_curriculum.title,
    	"subtitle": old_curriculum.subtitle,
    	"subject": old_curriculum.subject,
    	"lessons": [],
    	"parent_id":  old_curriculum._id,
    	"children": [],
    	"date_created": datetime.utcnow(),
    	"last_updated": datetime.utcnow(),
    	"author_id": session.get('user_id', ''),
    	"comments": []
    }

    new_curriculum_id = db.curricula.insert(new_curriculum)

    new_lessons = []

    for lesson in old_curriculum.lessons:
    	new_lesson_id = fork_lesson(lesson)
    	new_lessons.append(new_lesson_id)

    old_curriculum = db.curricula.find_one({"curriculum_id": new_curriculum_id})
    old_curriculum.lessons = new_lessons
    old_curriculum.num_forks += 1
    db.curricula.save(old_curriculum)

    return url_for('curriculum', new_curriculum_id)




