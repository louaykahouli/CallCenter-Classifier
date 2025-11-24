from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import prometheus_client
from prometheus_client import Counter, Histogram
import re
import os

# -----------------------------
# Load Model
# -----------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "tfidf_svm.joblib")
model_data = joblib.load(MODEL_PATH)
vectorizer = model_data["vectorizer"]
clf = model_data["model"]

# -----------------------------
# Prometheus Metrics
# -----------------------------
REQUEST_COUNT = Counter("api_requests_total", "Total API requests", ["endpoint"])
REQUEST_LATENCY = Histogram("api_request_latency_seconds", "Request latency", ["endpoint"])

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="MLOps Text Classifier API")

# -----------------------------
# Request Body
# -----------------------------
class TextRequest(BaseModel):
    text: str

# -----------------------------
# Utility: PII Scrubber
# -----------------------------
def scrub_pii(text: str) -> str:
    text = re.sub(r"\b\d{9,}\b", "[REDACTED]", text)       # redact long numbers
    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[REDACTED]", text)  # emails
    return text

# -----------------------------
# Health Check Endpoint
# -----------------------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": "TF-IDF + SVM",
        "model_loaded": clf is not None and vectorizer is not None
    }

# -----------------------------
# TF-IDF Prediction Endpoint
# -----------------------------
@app.post("/predict")
def predict_tfidf(request: TextRequest):
    REQUEST_COUNT.labels(endpoint="/predict").inc()
    with REQUEST_LATENCY.labels(endpoint="/predict").time():
        text_clean = scrub_pii(request.text)
        X_vect = vectorizer.transform([text_clean])
        probs = clf.predict_proba(X_vect)[0]
        labels = clf.classes_
        result = {label: float(prob) for label, prob in zip(labels, probs)}
        best_label = labels[np.argmax(probs)]
        return {
            "input": request.text,
            "prediction": best_label,
            "probabilities": result
        }

# -----------------------------
# Prometheus Metrics Endpoint
# -----------------------------
@app.get("/metrics")
def metrics():
    return prometheus_client.generate_latest()

