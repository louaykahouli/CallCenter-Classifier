# src/test_model.py
"""
Quick test script to verify that the trained TF-IDF + SVM model works correctly.
It loads the model, runs a few example predictions, and prints the results.
"""

import joblib
import os

MODEL_PATH = os.path.join("models", "tfidf_svm.joblib")

def main():
    print("🔍 Loading trained model from:", MODEL_PATH)
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"❌ Model not found at {MODEL_PATH}. Please train it first.")

    # Load saved model components
    model_data = joblib.load(MODEL_PATH)
    vectorizer = model_data["vectorizer"]
    model = model_data["model"]

    # Sample test tickets
    test_tickets = [
        "I forgot my password and cannot access my account.",
        "My laptop screen is cracked and needs replacement.",
        "The HR portal is not showing my salary information.",
        "I need additional storage for my project files.",
        "Can you help me with the VPN connection issue?",
    ]

    print("\n🧠 Running predictions...\n")
    for text in test_tickets:
        X = vectorizer.transform([input()])
        label = model.predict(X)[0]
        print(f"→ Predicted category: {label}\n")

    print("✅ Model test completed successfully.")

if __name__ == "__main__":
    main()
