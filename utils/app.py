from flask import Flask, render_template
from codeforces_api import codeforces_api_bp

app = Flask(__name__)
app.register_blueprint(codeforces_api_bp)

@app.route('/')
def home():
    return render_template('opening.html')  # ✅ THIS LINE IS CHANGED

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/codeforces')
def codeforces_page():
    return render_template('codeforces.html')

if __name__ == '__main__':
    app.run(debug=True)
