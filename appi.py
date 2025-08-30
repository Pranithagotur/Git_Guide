from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from utils.github_insights import get_github_data
from utils.coding_profile import get_user_data, compute_leetcode_score
# from utils.leetcode_stats import get_leetcode_data
# from utils.hackerrank_stats import get_hackerrank_data
from utils.ai_coach import get_ai_suggestions  # <- this should exist
# from utils.exporter import generate_pdf_report
from datetime import datetime
import mysql.connector
from utils.code_chef import get_codechef_data
import sqlite3
from dotenv import load_dotenv
from utils.codeforces_api import codeforces_api_bp
from utils.ai_coach import get_ai_suggestions
from flask_mail import Mail, Message
from utils.ai_plan import generate_plan  # move here

import os

load_dotenv()

app = Flask(__name__)
app.secret_key = 'YOUR SECRET KEY HERE'  # Replace with a secure key in production
from flask_mail import Mail, Message

# Add this after `app = Flask(__name__)`
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'grinkreviews@gmail.com'       # ✅ Replace
app.config['MAIL_PASSWORD'] = '045367e86ade10439a04ff9e5df9f4bca7cb2d04e0ba3b4cc4148ac470639953'          # ✅ Replace
app.config['MAIL_DEFAULT_SENDER'] = 'pranithagotur@gmail.com' # ✅ Replace

mail = Mail(app)


mysql_conn = mysql.connector.connect(
    host="localhost", user="root", password="Pranitha@6244", database="gitgrade"
)
mysql_cursor = mysql_conn.cursor()

sqlite_conn = sqlite3.connect('data.db')
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    github TEXT, leetcode TEXT, hackerrank TEXT)''')
sqlite_conn.commit()
sqlite_conn.close() 

@app.route("/")
def home():
    return render_template("opening.html")  # ✅ This is your landing page

@app.route("/dashboard")
def dashboard():
    if not session.get("github") and not session.get("leetcode"):
        return redirect(url_for("login"))
    username = session.get("leetcode") or "NeetCode"
    user_data = get_user_data(username)
    return render_template("dashboard.html", user=user_data)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["github"] = request.form.get("github")
        session["leetcode"] = request.form.get("leetcode")
        session["hackerrank"] = request.form.get("hackerrank")
        return redirect(url_for("dashboard"))
    return render_template("login.html")

# @app.route("/")
# def dashboard():
#     if not session.get("github") and not session.get("leetcode"):
#         return redirect(url_for("login"))

#     username = session.get("leetcode") or "NeetCode"
#     user_data = get_user_data(username)
    
#     return render_template("dashboard.html", user=user_data)

# # @app.route("/")
# def dashboard():
#     if not session.get("github") and not session.get("leetcode"):
#         return redirect(url_for("login"))

#     # Get user data
#     leetcode_username = session.get("leetcode", "")
#     codeforces_username = session.get("codeforces", "")
#     github_username = session.get("github", "")
    
#     # Optional: get LeetCode user data (if needed for dashboard)
#     leetcode_data = get_user_data(leetcode_username) if leetcode_username else None

#     # Render the main dashboard (change this based on your actual HTML file)
#     return render_template(
#         "dashboard.html",  # ✅ Use the correct template here
#         user=leetcode_data,
#         leetcode=leetcode_username,
#         codeforces=codeforces_username,
#         github=github_username
#     )
# app.register_blueprint(codeforces_api_bp)

@app.route("/submit", methods=["POST"])
def submit():
    github = request.form.get("github")
    leetcode = request.form.get("leetcode", "")
    hackerrank = request.form.get("hackerrank", "")

    session['github'] = github
    session['leetcode'] = leetcode
    session['hackerrank'] = hackerrank

    mysql_cursor.execute("""
        INSERT INTO users (github, leetcode, hackerrank)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE leetcode=%s, hackerrank=%s
    """, (github, leetcode, hackerrank, leetcode, hackerrank))
    mysql_conn.commit()

    return redirect(url_for('dashboard'))

@app.route("/submit_profile", methods=["POST"])
def submit_profile():
    session["github"] = request.form.get("github_username")
    session["leetcode"] = request.form.get("leetcode_username")
    session["hackerrank"] = request.form.get("hackerrank_username")
    return redirect("/github/" + session["github"])

@app.route("/api/summary")
def summary():
    github_user = session.get("github")
    leetcode_user = session.get("leetcode")
    hackerrank_user = session.get("hackerrank")

    github_score = 0
    leetcode_score = 0
    hackerrank_score = 0

    if github_user:
        try:
            github_score = get_github_data(github_user)["github_score"]
        except:
            pass

    if leetcode_user:
        try:
            leetcode_score = get_user_data(leetcode_user)["score"]
        except:
            pass

    if hackerrank_user:
        try:
            hackerrank_score = get_hackerrank_data(hackerrank_user)["score"]
        except:
            pass

    total_score = github_score + leetcode_score + hackerrank_score

    return jsonify({
        "github_score": github_score,
        "leetcode_score": leetcode_score,
        "hackerrank_score": hackerrank_score,
        "total_score": total_score
    })

@app.route("/api/github_insights")
def github_insights():
    username = session.get("github")
    return jsonify(get_github_data(username))

@app.route("/github_insights")
def github_insights_page():
    return render_template("github_insights.html")

@app.route("/github/<username>")
def github_insights_redirect(username):
    session["github"] = username
    data = get_github_data(username)
    return render_template("github_insights.html", data=data, username=username)

@app.route("/leetcode_profile")
def leetcode_profile_page():
    username = session.get("leetcode")
    if not username:
        return redirect(url_for("dashboard"))

    user_data = get_user_data(username)
    if not user_data or "solved" not in user_data:
        return "Unable to fetch LeetCode data", 500

    solved = user_data.get("solved", {})
    user_data["solved"] = {
        "easy": solved.get("easy", 0),
        "medium": solved.get("medium", 0),
        "hard": solved.get("hard", 0),
        "total": solved.get("total", 0),
    }

    ranking = user_data.get("ranking")
    user_data["ranking"] = int(ranking) if ranking and str(ranking).isdigit() else 999999

    user_data["score"] = compute_leetcode_score(
        user_data["solved"]["total"],
        user_data["ranking"],
        user_data["solved"]["easy"],
        user_data["solved"]["medium"],
        user_data["solved"]["hard"]
    )
    return render_template("coding_profile.html", user=user_data)
from datetime import datetime  # ✅ Correct import

@app.template_filter('datetimeformat')
def datetimeformat(value, format="%b %d, %Y %I:%M %p"):
    return datetime.fromtimestamp(int(value)).strftime(format)

@app.route('/api/leetcode')
def api_leetcode():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    try:
        data = get_user_data(username)
        if data:
            return jsonify(data)
        else:
            return jsonify({'error': 'LeetCode user not found'}), 404
    except Exception as e:
        print("LeetCode error:", e)
        return jsonify({'error': 'Failed to fetch LeetCode data'}), 500

@app.route('/api/ai_coach')
def ai_coach():
    github_user = session.get('github')
    leetcode_user = session.get('leetcode')
    hackerrank_user = session.get('hackerrank')

    github_score = 0
    leetcode_score = 0
    hackerrank_score = 0

    if github_user:
        try:
            github_score = get_github_data(github_user).get("github_score", 0)
        except Exception as e:
            print("❌ GitHub error:", e)

    if leetcode_user:
        try:
            leetcode_score = get_user_data(leetcode_user).get("score", 0)
        except Exception as e:
            print("❌ LeetCode error:", e)

    if hackerrank_user:
        try:
            hackerrank_score = get_hackerrank_data(hackerrank_user).get("score", 0)
        except Exception as e:
            print("❌ HackerRank error:", e)

    scores = [s for s in [github_score, leetcode_score, hackerrank_score] if s > 0] 
    readiness = int(sum(scores) / len(scores)) if scores else 0

    print("📊 Scores:", github_score, leetcode_score, hackerrank_score)
    suggestions = get_ai_suggestions(github_score, leetcode_score, hackerrank_score)

    print("🧠 Suggestions from AI:\n", suggestions)

    return jsonify({
        "github": github_score,
        "leetcode": leetcode_score,
        "hackerrank": hackerrank_score,
        "readiness": readiness,
        "suggestions": suggestions
    })

@app.route('/dashboard/ai-coach')
def ai_coach_page():
    return render_template('ai_coach.html')

@app.route("/api/codechef")
def codechef_api():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username required"}), 400

    data = get_codechef_data(username)
    return jsonify(data)

@app.route('/api/learning-plan', methods=['GET'])
def learning_plan():
    github = session.get("github_score", 0)
    leetcode = session.get("leetcode_score", 0)
    hackerrank = session.get("hackerrank_score", 0)

    plan = generate_learning_plan(github, leetcode, hackerrank)
    session['plan_text'] = plan
    return jsonify({"plan": plan})

from flask import Flask, request, jsonify
from utils.ai_plan import generate_plan  # ✅ Import from new file

@app.route("/ai-plan", methods=["POST"])
def ai_plan():
    data = request.get_json(force=True)
    print("📥 Incoming data:", data)

    try:
        plan = generate_plan(
            skill_gaps=data.get("skill_gaps", []),
            strengths=data.get("strengths", []),
            interests=data.get("interests", [])
        )
        print("✅ Generated Plan:", plan)
        return jsonify(plan)
    except Exception as e:
        print("❌ Error generating plan:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/project-ideas")
def project_ideas():
    return render_template("projId.html")


@app.route("/api/export")
def export_report():
    github_user = session.get("github")
    leetcode_user = session.get("leetcode")

    pdf_path = generate_pdf_report(github_user, leetcode_user)
    return send_file(pdf_path, as_attachment=True)

from utils.Leet import daily_questions_bp
app.register_blueprint(daily_questions_bp)
@app.route("/daily-questions")
def daily_questions_page():
    return render_template("Leet.html")

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json()
    email = data.get("email")
    questions = data.get("questions", [])

    if not email or not questions:
        return jsonify({"error": "Email and questions required"}), 400

    message_body = "Here are your LeetCode questions for today:\n\n"
    for q in questions:
        message_body += f"{q['difficulty']}: {q['title']} - {q['link']}\n"

    try:
        msg = Message("📘 Daily LeetCode Questions", sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = message_body
        mail.send(msg)
        return jsonify({"message": "Email sent successfully!"})
    except Exception as e:
        print("❌ Email error:", e)
        return jsonify({"error": "Failed to send email"}), 500
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

@app.route('/send-daily-questions', methods=['POST'])
def send_daily_questions():
    email = request.form.get("email")
    username = session.get("leetcode")

    if not email or not username:
        return jsonify({"error": "Missing email or username"}), 400

    user_data = get_user_data(username)
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    score = user_data.get("score", 0)
    questions = generate_daily_questions(score)

    question_text = "\n\n".join([f"{q['difficulty']}: {q['title']} - {q['link']}" for q in questions])

    message = Mail(
        from_email='your_verified_sendgrid_email@example.com',
        to_emails=email,
        subject=f'Daily LeetCode Questions for {username}',
        plain_text_content=question_text
    )

    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        sg.send(message)
        return jsonify({"message": "Email sent successfully!"})
    except Exception as e:
        print("SendGrid error:", e)
        return jsonify({"error": "Failed to send email"}), 500

from flask import request, jsonify
import cohere

co = cohere.Client("")  # replace with your key 

@app.route("/api/enhance-bullet", methods=["POST"])
def enhance_bullet():
    data = request.get_json()
    bullet = data.get("bullet")

    if not bullet:
        return jsonify({"error": "No input provided."}), 400

    try:
        response = co.generate(
            model='command',  # or another model name if you prefer
            prompt=f"Improve this sentence for a professional resume:\n\n\"{bullet}\"\n\nImproved:",
            max_tokens=80,
            temperature=0.7,
        )
        enhanced = response.generations[0].text.strip()
        return jsonify({"enhanced": enhanced})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
from utils.Leet import resume_bp
app.register_blueprint(resume_bp)




@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
    