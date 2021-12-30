import os

import inputs

from pymongo import MongoClient

from flask import abort
from flask import Flask
from flask import request
from flask import redirect
from flask import render_template


cluster = MongoClient(os.getenv("mongouri"))
db = cluster["challenges"]
usersDB = db["users"]
challengesDB = db["challenges"]

app = Flask(__name__)


@app.before_request
def before_request():
	if "/static/" not in request.path:
		user_id = request.headers.get("X-Replit-User-Id")
	
		if user_id:
			if not usersDB.find_one({ "_id": user_id }):
				usersDB.insert_one({
					"_id": user_id,
					"username": request.headers.get("X-Replit-User-Name"),
					"challenges": {},
					"last_completed": 0,
					"admin": False
				})


@app.route("/")
def main():
	user_id = request.headers.get("X-Replit-User-Id")
	
	return render_template(
		"index.html",
		authed=user_id,
		user=usersDB.find_one({ "_id": user_id }),
	)


@app.route("/challenges")
def challenges():
	user_id = request.headers.get("X-Replit-User-Id")
	
	return render_template(
		"challenges.html",
		authed=user_id,
		user=usersDB.find_one({ "_id": user_id }),
		challenges=list(challengesDB.find())
	)


@app.route("/challenge/<num>")
def challenge(num):
	num = int(num)
	user_id = request.headers.get("X-Replit-User-Id")

	if not user_id:
		return redirect("/challenges")

	user = usersDB.find_one({ "_id": user_id })

	if not user["admin"] and user["last_completed"] + 1 < num:
		return redirect("/challenges")

	return render_template(
		"challenge.html",
		authed=True,
		user=user,
		challenge=challengesDB.find_one({ "_id": num })
	)


@app.route("/challenge/<num>/input")
def get_challenge_input(num):
	user_id = request.headers.get("X-Replit-User-Id")

	if not user_id:
		return redirect("/challenges")
		
	user = usersDB.find_one({ "_id": user_id })

	if (not user["admin"] and user["last_completed"] + 1 < int(num)) or not challengesDB.find_one({ "_id": int(num) }):
		return redirect("/challenges")
	
	if num in user["challenges"]:
		return render_template(
			"input.html",
			input="\n".join(user["challenges"][num]["input"])
		)

	result, input = eval(f"inputs.challenge_{num}()")

	usersDB.update_one({ "_id": user_id }, { "$set": {
		f"challenges.{num}.input": input,
		f"challenges.{num}.result": result
	}})

	return render_template(
		"input.html",
		input="\n".join(input)
	)


@app.route("/challenge/<num>/answer", methods=["POST"])
def submit_challenge_answer(num):
	user_id = request.headers.get("X-Replit-User-Id")

	if not user_id:
		return redirect("/challenges")
		
	user = usersDB.find_one({ "_id": user_id })

	if (not user["admin"] and user["last_completed"] + 1 != int(num)) or not challengesDB.find_one({ "_id": int(num) }):
		return redirect("/challenges")
	
	if num not in user["challenges"]:
		redirect(f"/challanges/{num}")

	answer = request.form.get("answer")

	if not answer:
		return abort(400)

	correct = answer == str(user["challenges"][num]["result"])

	if correct:
		usersDB.update_one({ "_id": user_id }, { "$set":  {"last_completed": int(num) } })
		
	return render_template(
		"submitted.html",
		authed=True,
		user=user,
		correct=correct,
		challenge=num
	)
	



@app.route("/challenges/write")
def write_challenge_form():
	user_id = request.headers.get("X-Replit-User-Id")

	if not user_id:
		return redirect("/challenges")

	user = usersDB.find_one({ "_id": user_id })

	if not user["admin"]:
		return redirect("/challenges")

	return render_template(
		"write.html",
		authed=True,
		user=user,
		form_url=f"/challenges/write"
	)


@app.route("/challenges/write", methods=["POST"])
def write_challenge():
	user_id = request.headers.get("X-Replit-User-Id")

	if not user_id:
		return redirect("/challenges")

	user = usersDB.find_one({ "_id": user_id })

	if not user["admin"]:
		return redirect("/challenges")

	title = request.form.get("title")
	content = request.form.get("content")

	if not title or not content:
		return abort(400)

	next_num = list(challengesDB.find().sort("_id", -1))[0]["_id"] + 1

	challengesDB.insert_one({
		"_id": next_num,
		"title": title,
		"content": content
	})

	return redirect(f"/challenge/{next_num}")


@app.route("/challenge/<num>/edit")
def edit_challenge_form(num):
	user_id = request.headers.get("X-Replit-User-Id")

	if not user_id:
		return redirect("/challenges")

	user = usersDB.find_one({ "_id": user_id })

	if not user["admin"]:
		return redirect("/challenges")

	challenge = challengesDB.find_one({ "_id": int(num) })

	if not challenge:
		return redirect("/challenges")			  

	return render_template(
		"write.html",
		authed=True,
		user=user,
		form_url=f"/challenge/{num}/edit",
		title=challenge["title"],
		content=challenge["content"]
	)

@app.route("/challenge/<num>/edit", methods=["POST"])
def edit_challenge(num):
	user_id = request.headers.get("X-Replit-User-Id")

	if not user_id:
		return redirect("/challenges")

	user = usersDB.find_one({ "_id": user_id })

	if not user["admin"]:
		return redirect("/challenges")

	challenge = challengesDB.find_one({ "_id": int(num) })

	if not challenge:
		return redirect("/challenges")		

	title = request.form.get("title")
	content = request.form.get("content")

	if not title or not content:
		return abort(400)
	
	challengesDB.update_one({ "_id": int(num) }, { "$set": {
		"title": title,
		"content": content
	}})

	return redirect(f"/challenge/{num}")
		


app.run("0.0.0.0", port=8080)
