from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os, string, PyPDF2, docx

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

FILE_TYPES = {
    "pdf": [".pdf"],
    "word": [".doc", ".docx"],
    "excel": [".xls", ".xlsx"],
    "image": [".jpg", ".jpeg", ".png"]
}

def get_drives():
    drives = []
    for d in string.ascii_uppercase:
        path = f"{d}:\\"
        if os.path.exists(path):
            drives.append(path)
    return drives


def safe_scan(path):
    counts = {
        "total": 0,
        "pdf": 0,
        "word": 0,
        "excel": 0,
        "image": 0,
        "other": 0
    }

    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                counts["total"] += 1
                ext = os.path.splitext(f)[1].lower()

                if ext in FILE_TYPES["pdf"]:
                    counts["pdf"] += 1
                elif ext in FILE_TYPES["word"]:
                    counts["word"] += 1
                elif ext in FILE_TYPES["excel"]:
                    counts["excel"] += 1
                elif ext in FILE_TYPES["image"]:
                    counts["image"] += 1
                else:
                    counts["other"] += 1
            except PermissionError:
                continue

    return counts

def search_keyword(path, keyword):
    count = 0

    for root, dirs, files in os.walk(path):
        for f in files:
            full_path = os.path.join(root, f)

            try:
                if f.endswith(".txt"):
                    with open(full_path, "r", errors="ignore") as file:
                        count += file.read().lower().count(keyword.lower())

                elif f.endswith(".pdf"):
                    reader = PyPDF2.PdfReader(full_path)
                    for page in reader.pages:
                        count += (page.extract_text() or "").lower().count(keyword.lower())

                elif f.endswith(".docx"):
                    doc = docx.Document(full_path)
                    for p in doc.paragraphs:
                        count += p.text.lower().count(keyword.lower())

            except PermissionError:
                continue
            except Exception:
                continue

    return count


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scan")
def scan():
    return {d: safe_scan(d) for d in get_drives()}

@app.post("/search")
def search(name: str = Form(...)):
    total = sum(search_keyword(d, name) for d in get_drives())
    return {"keyword": name, "count": total}
