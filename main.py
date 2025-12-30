from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import pandas as pd
import joblib
import os

from database import init_db, get_connection
from model_training import train_model, MODEL_PATH

# --------------------------------------------------
# APP SETUP
# --------------------------------------------------
app = FastAPI(title="🧠 AI Feedback Analysis System")

init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------
# SERVE FRONTEND FILES (ROOT)
# --------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/style.css")
def css():
    return FileResponse(os.path.join(BASE_DIR, "style.css"))

@app.get("/script.js")
def js():
    return FileResponse(os.path.join(BASE_DIR, "script.js"))

# --------------------------------------------------
# 🧠 TRAIN MODEL
# --------------------------------------------------
@app.post("/train-model")
def train(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        return JSONResponse({"error": "Only CSV files allowed"}, status_code=400)

    try:
        with open("train.csv", "wb") as f:
            f.write(file.file.read())
        train_model("train.csv")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return {"message": "✅ Model trained successfully"}

# --------------------------------------------------
# 📊 SINGLE FEEDBACK PREDICTION
# --------------------------------------------------
@app.post("/predict-feedback")
def predict(feedback: str = Form(...)):
    if not os.path.exists(MODEL_PATH):
        return JSONResponse({"error": "Train model first"}, status_code=400)

    vectorizer, model = joblib.load(MODEL_PATH)

    X = vectorizer.transform([feedback])
    probs = model.predict_proba(X)[0]

    sentiment = model.classes_[probs.argmax()]
    confidence = float(probs.max())

    conn = get_connection()
    conn.execute(
        "INSERT INTO feedback (text, sentiment, confidence) VALUES (?, ?, ?)",
        (feedback, sentiment, confidence)
    )
    conn.commit()
    conn.close()

    emoji = "😊" if sentiment == "positive" else "😡" if sentiment == "negative" else "😐"

    return {
        "sentiment": sentiment,
        "emoji": emoji,
        "confidence": round(confidence, 2)
    }

# --------------------------------------------------
# 📂 BULK FEEDBACK ANALYSIS
# --------------------------------------------------
@app.post("/upload-feedback")
def upload_feedback(file: UploadFile = File(...)):
    if not os.path.exists(MODEL_PATH):
        return JSONResponse({"error": "Train model first"}, status_code=400)

    if not file.filename.endswith(".csv"):
        return JSONResponse({"error": "Only CSV allowed"}, status_code=400)

    df = pd.read_csv(file.file)
    df.columns = df.columns.str.lower().str.strip()

    if "feedback" not in df.columns:
        return JSONResponse({"error": "CSV must contain feedback column"}, status_code=400)

    vectorizer, model = joblib.load(MODEL_PATH)

    sentiments = []
    conn = get_connection()

    for text in df["feedback"].astype(str):
        X = vectorizer.transform([text])
        probs = model.predict_proba(X)[0]
        sentiment = model.classes_[probs.argmax()]
        confidence = float(probs.max())

        sentiments.append(sentiment)

        conn.execute(
            "INSERT INTO feedback (text, sentiment, confidence) VALUES (?, ?, ?)",
            (text, sentiment, confidence)
        )

    conn.commit()
    conn.close()

    total = len(sentiments)
    pos = sentiments.count("positive")
    neu = sentiments.count("neutral")
    neg = sentiments.count("negative")

    def pct(x): return round((x / total) * 100, 2) if total else 0

    overall = "😐 Mixed"
    if pct(pos) > 60:
        overall = "😊 Mostly Positive"
    elif pct(neg) > 60:
        overall = "😡 Mostly Negative"

    return {
        "total": total,
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "positive_pct": pct(pos),
        "neutral_pct": pct(neu),
        "negative_pct": pct(neg),
        "overall": overall
    }

# --------------------------------------------------
# 🧪 TEST MODEL
# --------------------------------------------------
@app.post("/test-model")
def test(file: UploadFile = File(...)):
    if not os.path.exists(MODEL_PATH):
        return JSONResponse({"error": "Train model first"}, status_code=400)

    df = pd.read_csv(file.file)
    df.columns = df.columns.str.lower().str.strip()

    if not {"feedback", "sentiment"}.issubset(df.columns):
        return JSONResponse({"error": "CSV needs feedback & sentiment"}, status_code=400)

    vectorizer, model = joblib.load(MODEL_PATH)

    preds = [model.predict(vectorizer.transform([t]))[0]
             for t in df["feedback"].astype(str)]

    total = len(preds)
    pos = preds.count("positive")
    neu = preds.count("neutral")
    neg = preds.count("negative")

    def pct(x): return round((x / total) * 100, 2)

    overall = "😐 Mixed"
    if pct(pos) > 60:
        overall = "😊 Mostly Positive"
    elif pct(neg) > 60:
        overall = "😡 Mostly Negative"

    return {
        "total": total,
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "positive_pct": pct(pos),
        "neutral_pct": pct(neu),
        "negative_pct": pct(neg),
        "overall": overall
    }
