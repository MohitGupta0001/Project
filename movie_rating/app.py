from flask import Flask, jsonify, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

MOVIES = [
    {"name": "The Last Horizon", "rating": 8.2, "release_date": "2026-01-05"},
    {"name": "Neon Skies", "rating": 7.9, "release_date": "2025-12-28"},
    {"name": "Crimson Dawn", "rating": 8.5, "release_date": "2025-12-20"},
    {"name": "Echoes of Time", "rating": 7.8, "release_date": "2025-12-15"},
    {"name": "Silent Vow", "rating": 8.0, "release_date": "2025-12-10"},
    {"name": "Iron Legacy", "rating": 7.6, "release_date": "2025-11-30"},
    {"name": "Frozen Pulse", "rating": 7.5, "release_date": "2025-11-25"},
    {"name": "Midnight Protocol", "rating": 8.1, "release_date": "2025-11-20"},
    {"name": "Quantum Drift", "rating": 8.3, "release_date": "2025-11-18"},
    {"name": "Solar Reign", "rating": 7.7, "release_date": "2025-11-15"},
    {"name": "Urban Mythos", "rating": 7.4, "release_date": "2025-10-25"},
    {"name": "Broken Signal", "rating": 7.9, "release_date": "2025-10-20"},
    {"name": "Hidden Frequency", "rating": 8.0, "release_date": "2025-10-10"},
    {"name": "Steel Mirage", "rating": 7.6, "release_date": "2025-09-28"},
    {"name": "Afterlight", "rating": 7.8, "release_date": "2025-09-20"},
    {"name": "Black Ember", "rating": 8.4, "release_date": "2025-09-15"},
    {"name": "White Noise City", "rating": 7.3, "release_date": "2025-09-10"},
    {"name": "Night Circuit", "rating": 7.5, "release_date": "2025-09-05"},
    {"name": "Final Descent", "rating": 8.1, "release_date": "2025-08-28"},
    {"name": "Static Hearts", "rating": 7.6, "release_date": "2025-08-20"},
]

@app.route("/movies")
def get_recent_movies():
    today = datetime.today()
    two_months_ago = today - timedelta(days=60)

    recent_movies = [
        movie for movie in MOVIES
        if datetime.strptime(movie["release_date"], "%Y-%m-%d") >= two_months_ago
    ]

    return jsonify(recent_movies)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
