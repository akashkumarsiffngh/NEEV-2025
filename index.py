from flask import Flask, render_template, request, redirect, url_for, session
import random
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Load notes and quizzes
def load_data(class_level):
    notes_path = f"data/{class_level}/notes.json"
    quizzes_path = f"data/{class_level}/quizzes.json"
    try:
        with open(notes_path, 'r') as f:
            notes = json.load(f)
        with open(quizzes_path, 'r') as f:
            quizzes = json.load(f)
    except FileNotFoundError:
        notes = {}
        quizzes = {}
    return notes, quizzes

class9_notes, class9_quizzes = load_data("class9")
class10_notes, class10_quizzes = load_data("class10")

# Leaderboard data (in-memory for simplicity)
leaderboard = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/class9')
def class9():
    return render_template('class9.html', notes=class9_notes)

@app.route('/class10')
def class10():
    return render_template('class10.html', notes=class10_notes)

@app.route('/quiz/<int:class_level>/<int:quiz_id>', methods=['GET', 'POST'])
def quiz(class_level, quiz_id):
    if class_level == 9:
        quiz_data = class9_quizzes.get(str(quiz_id))
    elif class_level == 10:
        quiz_data = class10_quizzes.get(str(quiz_id))
    else:
        return "Invalid class level"

    if request.method == 'POST':
        user_answers = request.form
        score = 0
        wrong_answers = []
        for question_id, answer in user_answers.items():
            if answer == quiz_data['questions'][question_id]['answer']:
                score += 1
            else:
                wrong_answers.append(question_id)

        # Update leaderboard
        if 'username' in session:
            username = session['username']
            if username not in leaderboard:
                leaderboard[username] = 0
            leaderboard[username] = max(leaderboard[username], score)

        return render_template('quiz_results.html', score=score, 
                               wrong_answers=wrong_answers, 
                               quiz_data=quiz_data)

    return render_template('quiz.html', quiz_data=quiz_data)

@app.route('/leaderboard')
def leaderboard_view():
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    return render_template('leaderboard.html', leaderboard=sorted_leaderboard)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    
