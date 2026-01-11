from flask import Flask, render_template, request, jsonify
import requests
import PyPDF2

app = Flask(__name__)

NEWS_API_KEY = "36fc07b0360c42c1be2c99ce96f7d99e"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/check-risk", methods=["POST"])
def check_risk():
    company = request.form.get("company")
    file = request.files.get("pdf")

    if not company:
        return jsonify({"error": "Company name required"})

    news_url = f"https://newsapi.org/v2/everything?q={company}&apiKey={NEWS_API_KEY}"
    data = requests.get(news_url).json()
    articles = data.get("articles", [])

    negative_words = ["loss", "fraud", "scam", "decline", "lawsuit", "bankrupt"]
    negative = 0

    for a in articles[:10]:
        text = (a.get("title","") + a.get("description","")).lower()
        if any(w in text for w in negative_words):
            negative += 1

    if negative > 0:
        news_risk, news_score = "HIGH RISK", 100
    else:
        news_risk, news_score = "LOW RISK", 0

    pdf_risk, pdf_score = "HIGH RISK", 100

    if file and file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        content = ""
        for page in reader.pages:
            content += page.extract_text() or ""
        if "balance sheet" in content.lower():
            pdf_risk, pdf_score = "LOW RISK", 0

    avg = (news_score + pdf_score) / 2

    return jsonify({
        "news_risk": news_risk,
        "balance_risk": pdf_risk,
        "average_risk": avg
    })

if __name__ == "__main__":
    app.run(debug=True)
