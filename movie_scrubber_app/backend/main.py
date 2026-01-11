from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "X-RapidAPI-Key":  "38389d1d98msh79c6282fdb5bb17p119edcjsnd597f63ecc82",
    "X-RapidAPI-Host": "moviesminidatabase.p.rapidapi.com"
}

BASE_URL = "https://moviesminidatabase.p.rapidapi.com"

@app.get("/movies")
def get_movies():
    response = requests.get(
        f"{BASE_URL}/movie/order/byPopularity/",
        headers=HEADERS
    )

    data = response.json()
    movies = data.get("results", [])

    two_months_ago = datetime.now() - timedelta(days=60)
    filtered = []

    for movie in movies:
        try:
            rating = movie.get("rating", 0)
            release_date_str = movie.get("release_date")
            if not release_date_str:
                continue

            release_date = datetime.strptime(release_date_str, "%Y-%m-%d")

            if rating > 4 and release_date >= two_months_ago:
                filtered.append({
                    "title": movie.get("title"),
                    "rating": rating
                })
        except Exception:
            continue

    return filtered
