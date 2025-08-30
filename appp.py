from flask import Flask, request, jsonify, session, send_file
from utils.learning_plan import generate_learning_plan
# from utils.exporter import generate_pdf_report
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env variables like OPENAI_API_KEY

app = Flask(__name__)
app.secret_key ='YOUR SECRET KEY HERE'  # Required for session
from utils.learning_plan import generate_learning_plan

@app.route('/api/learning-plan', methods=['GET'])
def learning_plan():
    github = session.get("github_score", 0)
    leetcode = session.get("leetcode_score", 0)
    hackerrank = session.get("hackerrank_score", 0)

    plan = generate_learning_plan(github, leetcode, hackerrank)

    return jsonify({"plan": plan})
if __name__ == "__main__":
    app.run(debug=True)
