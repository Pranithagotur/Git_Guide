from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# DB connection
conn = mysql.connector.connect(
    host="localhost", user="root", password="", database="gitgrade"
)
cursor = conn.cursor()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")  # Your form page

@app.route("/dashboard", methods=["POST"])
def dashboard():
    github = request.form["github_username"]
    leetcode = request.form.get("leetcode_username", "")
    hackerrank = request.form.get("hackerrank_username", "")

    # Save to DB
    cursor.execute("""
        INSERT INTO users (github, leetcode, hackerrank)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE leetcode=%s, hackerrank=%s
    """, (github, leetcode, hackerrank, leetcode, hackerrank))
    conn.commit()

    return render_template("dashboard.html", username=github)
