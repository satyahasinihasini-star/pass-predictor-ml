"""
app.py
Flask backend: serves the frontend, runs ML predictions, and stores
every prediction in a SQLite database.

Run: python app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, jsonify
import pickle
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# Load trained ML model
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_hours REAL,
            attendance REAL,
            previous_marks REAL,
            result TEXT,
            probability REAL,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    study_hours = float(data["study_hours"])
    attendance = float(data["attendance"])
    previous_marks = float(data["previous_marks"])

    features = [[study_hours, attendance, previous_marks]]
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]  # probability of PASS

    result = "PASS" if prediction == 1 else "FAIL"

    # Save to database
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO predictions (study_hours, attendance, previous_marks, result, probability, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (study_hours, attendance, previous_marks, result, probability, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return jsonify({
        "result": result,
        "probability": round(probability * 100, 1)
    })


@app.route("/history")
def history():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT study_hours, attendance, previous_marks, result, probability, created_at "
        "FROM predictions ORDER BY id DESC LIMIT 10"
    ).fetchall()
    conn.close()

    history_list = [
        {
            "study_hours": r[0],
            "attendance": r[1],
            "previous_marks": r[2],
            "result": r[3],
            "probability": round(r[4] * 100, 1),
            "created_at": r[5]
        }
        for r in rows
    ]
    return jsonify(history_list)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
