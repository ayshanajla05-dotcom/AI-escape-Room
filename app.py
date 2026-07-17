from flask import Flask, render_template, request, jsonify, session,redirect
import random
from ai_chat import get_ai_hint
from ai_chat import generate_puzzle
import json
import os
from datetime import datetime
from time import time

app = Flask(__name__)
app.secret_key = "escape_room_secret"

TOTAL_LEVELS = 5




@app.route("/level")
def level():

    level = session.get("level", 0)

    if level >= TOTAL_LEVELS:
        return render_template(
            "result.html",
            score=session.get("score", 0),
            total=TOTAL_LEVELS * 20
        )


    # Previous questions
    used_questions = session.get("used_questions", [])


    # Generate AI puzzle
    ai = generate_puzzle(used_questions)


    print("==============================")
    print("AI RESPONSE:")
    print(repr(ai))
    print("==============================")


    try:

        # Remove markdown if AI sends it
        ai = ai.replace("```json", "")
        ai = ai.replace("```", "")
        ai = ai.strip()


        puzzle = json.loads(ai)


    except Exception as e:

        print("JSON ERROR:", e)

        puzzle = {
            "question": "What is AI?",
            "answer": "Artificial Intelligence",
            "hint": "It helps computers learn."
        }



    # Prevent duplicate questions
    attempts = 0

    while puzzle["question"] in used_questions and attempts < 5:

        print("Duplicate question detected")

        ai = generate_puzzle(used_questions)

        ai = ai.replace("```json", "")
        ai = ai.replace("```", "")
        ai = ai.strip()

        puzzle = json.loads(ai)

        attempts += 1



    # Save question history

    used_questions.append(puzzle["question"])

    session["used_questions"] = used_questions


    # Save current puzzle

    session["current_puzzle"] = puzzle



    return render_template(
        "level.html",
        puzzle=puzzle,
        level=level + 1,
        total_levels=TOTAL_LEVELS,
        score=session.get("score",0)
    )
    
@app.route("/check",methods=["POST"])
def check():

    answer=request.form["answer"].strip().lower()

    puzzle=session.get("current_puzzle")

    if not puzzle:

        return jsonify({

            "correct":False,

            "message":"No puzzle found."

        })

    if answer==puzzle["answer"].lower():

        session["score"]+=20

        session["level"]+=1

        return jsonify({

            "correct":True,

            "next":"/level"

        })

    return jsonify({

        "correct":False,

        "message":"Wrong Answer!"

    })

@app.route("/hint")
def hint():

    session["hints_used"] = session.get("hints_used", 0) + 1

    puzzle=session.get("current_puzzle")

    if not puzzle:

        return jsonify({

            "hint":"No puzzle."

        })

    return jsonify({

        "hint":puzzle["hint"]

    })


@app.route("/restart")
def restart():

    session["level"] = 0
    session["score"] = 0

    return render_template("index.html")

@app.route("/generate")
def generate():

    puzzle = generate_puzzle()

    return jsonify({

        "puzzle": puzzle

    })

@app.route("/save",methods=["POST"])
def save():

    name=request.form["name"]

    score=session["score"]

    with open("leaderboard.json","r") as f:

        data=json.load(f)

    data.append({

        "name":name,

        "score":score

    })

    data=sorted(data,key=lambda x:x["score"],reverse=True)

    with open("leaderboard.json","w") as f:

        json.dump(data,f,indent=4)

    return "Saved"



# -------------------------------
# Save Score
# -------------------------------

@app.route("/save_score", methods=["POST"])
def save_score():

    name = request.form.get("name")

    score = session.get("score", 0)

    # Calculate time taken
    elapsed = int(time() - session.get("start_time", time()))

    minutes = elapsed // 60
    seconds = elapsed % 60

    time_taken = f"{minutes}:{seconds:02d}"

    if not name:
        name = "Anonymous"

    leaderboard_file = "leaderboard.json"

    # Read existing scores
    if os.path.exists(leaderboard_file):

        with open(leaderboard_file, "r") as file:
            leaderboard = json.load(file)

    else:
        leaderboard = []

    # Handle duplicate names
    existing_player = None

    for player in leaderboard:

        if player["name"].lower() == name.lower():
            existing_player = player
            break

    if existing_player:

        # Keep highest score
        if score > existing_player["score"]:
            existing_player["score"] = score
            existing_player["time"] = time_taken
            existing_player["hints"] = session.get("hints_used", 0)
            existing_player["date"] = str(datetime.now().date())

    else:

        leaderboard.append({
            "name": name,
            "score": score,
            "time": time_taken,
            "hints": session.get("hints_used", 0),
            "date": str(datetime.now().date())
        })

    # Convert mm:ss to seconds
    def time_to_seconds(t):
        m, s = map(int, t.split(":"))
        return m * 60 + s

    # Sort by score, hints, then time
    leaderboard = sorted(
        leaderboard,
        key=lambda x: (
            -x["score"],
            x["hints"],
            time_to_seconds(x["time"])
        )
    )

    # Keep only top 10
    leaderboard = leaderboard[:10]

    # Save leaderboard
    with open(leaderboard_file, "w") as file:
        json.dump(leaderboard, file, indent=4)

    return redirect("/leaderboard")
# -------------------------------

@app.route("/leaderboard")
def leaderboard():


    if os.path.exists("leaderboard.json"):

        with open("leaderboard.json","r") as file:

            players=json.load(file)

    else:

        players=[]



    return render_template(
        "leaderboard.html",
        players=players
    )

@app.route("/skip")
def skip():

    # Move to the next level
    session["level"] = session.get("level", 0) + 1

    # Remove the current puzzle
    session.pop("current_puzzle", None)

    return redirect("/level")

@app.route("/")
def home():

    session["level"] = 0
    session["score"] = 0
    session["used_questions"] = []
    session["hints_used"] = 0
    session["start_time"] = time()

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)