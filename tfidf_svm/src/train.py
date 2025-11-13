# src/train.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
import joblib
import mlflow
import os

DATA_PATH = "data/processed.csv"
MODEL_PATH = "models/tfidf_svm.joblib"

def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["Document", "Topic_group"])
    return df

def train_model():
    print("📚 Loading cleaned dataset...")
    df = load_data()
    X = df["Document"].astype(str)
    y = df["Topic_group"]

    print("✂️ Splitting train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("🧠 Building TF-IDF + SVM pipeline...")
    vectorizer = TfidfVectorizer(max_features=20000, ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    svm = LinearSVC(random_state=42, max_iter=10000)
    clf = CalibratedClassifierCV(svm)  # adds predict_proba support

    mlflow.start_run()
    print("🚀 Training model...")
    clf.fit(X_train_tfidf, y_train)

    preds = clf.predict(X_test_tfidf)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds, average="weighted")

    print(f"✅ Accuracy: {acc:.4f}")
    print(f"✅ F1-Score: {f1:.4f}")
    print(classification_report(y_test, preds))

    mlflow.log_metric("accuracy", acc)
    mlflow.log_metric("f1_weighted", f1)

    os.makedirs("models", exist_ok=True)
    joblib.dump({"vectorizer": vectorizer, "model": clf}, MODEL_PATH)
    mlflow.log_artifact(MODEL_PATH)
    mlflow.end_run()

    print(f"💾 Model saved to: {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
