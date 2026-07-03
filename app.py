from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
import joblib
import os
import sqlite3
import requests
import time
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI

API_KEY = os.environ.get("NEWSAPI_KEY", "01005f5f946a4d8b9c232a8ee206c88d")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_KEY", ""))

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)


app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    conn.commit()
    conn.close()

# ---------------- LOAD MODEL ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "model", "model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "model", "vectorizer.pkl")

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        hashed_password = generate_password_hash(password, method='pbkdf2')

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )

        conn.commit()
        conn.close()

        flash("Registered successfully!")
        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        try:
            password_ok = user and check_password_hash(user[2], password)
        except ValueError:
            password_ok = False

        if password_ok:
            session['user'] = username
            return redirect('/')
        else:
            flash("Invalid login")

    return render_template('login.html')

# ---------------- HOME ----------------
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template("index.html")

# ---------------- NEWS ----------------
@app.route('/news')
def news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"
        res = requests.get(url)
        data = res.json()

        articles = data.get('articles', [])

        return render_template("news.html", articles=articles)

    except Exception as e:
        return f"Error loading news: {str(e)}"

# ---------------- VERIFY (Websearch) ----------------
@app.route('/verify', methods=['POST'])
def verify():
    news = request.form['news']

    if not OPENROUTER_API_KEY:
        return render_template("index.html", prediction=None, confidence=None, verification="Error: OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable.")

    try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                     model="poolside/laguna-xs.2:free",
                    messages=[
                        {
                            "role": "user",
                            "content": f"Analyze this news claim and determine if it's real or fake. Search the web for corroborating evidence and provide a detailed analysis:\n\n{news}"
                        }
                    ],
                    tools=[
                        {
                            "type": "openrouter:web_search"
                        }
                    ]
                )
                verification = response.choices[0].message.content or ""
                return render_template("index.html", prediction=None, confidence=None, verification=verification)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                raise
    except Exception as e:
        return render_template("index.html", prediction=None, confidence=None, verification=f"Verification error: {str(e)}")

# ---------------- PREDICT ----------------
@app.route('/predict', methods=['POST'])
def predict():
    news = request.form['news']
    use_verification = request.form.get('use_verification', 'false').lower() == 'true'

    if use_verification:
        return verify()

    vector = vectorizer.transform([news])
    prediction = model.predict(vector)[0]

    prob = model.predict_proba(vector)[0]
    confidence = round(max(prob) * 100, 2)

    result = "Fake News" if prediction == 0 else "Real News"

    return render_template("index.html", prediction=result, confidence=confidence)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ---------------- PWA ASSETS ----------------
@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'manifest.json', mimetype='application/json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sw.js', mimetype='application/javascript')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'icon-192.png', mimetype='image/png')

# ---------------- RUN ----------------
init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000 ,debug=True)