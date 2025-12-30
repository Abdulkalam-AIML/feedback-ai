import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "sentiment_model.pkl"

def train_model(csv_file):
    df = pd.read_csv(csv_file)

    if df.empty:
        raise ValueError("Uploaded dataset is empty")

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    if "feedback" not in df.columns or "sentiment" not in df.columns:
        raise ValueError(
            f"CSV must contain columns: feedback, sentiment. Found: {list(df.columns)}"
        )

    X = df["feedback"].astype(str)
    y = df["sentiment"].astype(str)

    vectorizer = TfidfVectorizer(stop_words="english")
    X_vec = vectorizer.fit_transform(X)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_vec, y)

    joblib.dump((vectorizer, model), MODEL_PATH)
