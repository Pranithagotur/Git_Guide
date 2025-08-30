from flask import Blueprint, request, jsonify
import requests
import datetime
import random

daily_questions_bp = Blueprint('daily_questions', __name__, url_prefix='/api')

# Fetch all problems from LeetCode
def fetch_all_leetcode_questions():
    url = "https://leetcode.com/api/problems/all/"
    headers = {
        "Referer": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return []

    data = res.json()
    return data.get("stat_status_pairs", [])

from flask import Blueprint, request, jsonify
import cohere
import os

resume_bp = Blueprint('resume_bp', __name__)

co = cohere.Client(os.getenv("COHERE_API_KEY"))  # Make sure your API key is set in .env

@resume_bp.route("/api/enhance", methods=["POST"])
def enhance_resume():
    data = request.get_json()
    sentence = data.get("sentence", "")

    if not sentence.strip():
        return jsonify({"error": "No sentence provided."}), 400

    try:
        response = co.generate(
            model='command-r-plus',
            prompt=f"Rewrite the following sentence into a strong professional resume bullet point:\n\n{sentence}",
            max_tokens=80,
            temperature=0.7,
            k=0,
            stop_sequences=["--"]
        )
        return jsonify({"enhanced": response.generations[0].text.strip()})
    except Exception as e:
        print("❌ Error from Cohere:", e)
        return jsonify({"error": "Error enhancing sentence"}), 500

# Filter and return today's 3 questions based on score
def generate_daily_questions(score):
    problems = fetch_all_leetcode_questions()
    today_seed = int(datetime.date.today().strftime("%Y%m%d"))
    random.seed(today_seed)

    def format_question(q):
        return {
            "title": q['stat']['question__title'],
            "slug": q['stat']['question__title_slug'],
            "difficulty": ["Easy", "Medium", "Hard"][q['difficulty']['level'] - 1],
            "link": f"https://leetcode.com/problems/{q['stat']['question__title_slug']}/"
        }

    if not problems:
        return []

    if score >= 85:
        # Advanced users: mix of 2 hard + 1 medium
        hard = [format_question(q) for q in problems if q['difficulty']['level'] == 3]
        medium = [format_question(q) for q in problems if q['difficulty']['level'] == 2]
        return random.sample(hard, 2) + random.sample(medium, 1)

    elif score >= 65:
        # Intermediate: 2 medium + 1 easy
        medium = [format_question(q) for q in problems if q['difficulty']['level'] == 2]
        easy = [format_question(q) for q in problems if q['difficulty']['level'] == 1]
        return random.sample(medium, 2) + random.sample(easy, 1)

    elif score >= 45:
        # Beginner-Intermediate: 2 easy + 1 medium
        easy = [format_question(q) for q in problems if q['difficulty']['level'] == 1]
        medium = [format_question(q) for q in problems if q['difficulty']['level'] == 2]
        return random.sample(easy, 2) + random.sample(medium, 1)

    else:
        # Beginners: All easy
        easy = [format_question(q) for q in problems if q['difficulty']['level'] == 1]
        return random.sample(easy, 3)

@daily_questions_bp.route("/daily")
def get_daily_questions():
    from flask import session
    from utils.coding_profile import get_user_data

    username = session.get("leetcode")
    if not username:
        return jsonify({"error": "User not logged in"}), 401

    user_data = get_user_data(username)
    if not user_data:
        return jsonify({"error": "LeetCode user not found"}), 404

    score = user_data.get("score", 0)
    questions = generate_daily_questions(score)

    return jsonify({
        "username": username,
        "score": score,
        "daily_questions": questions,
        "message": f"Based on your current score of {score}, we've selected questions to boost your problem-solving skills."
    })
