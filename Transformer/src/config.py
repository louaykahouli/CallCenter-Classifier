
import os
from pathlib import Path

# Chemins du projet
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
TRANSFORMER_MODEL_DIR = MODELS_DIR / "transformer"

# Configuration du modèle Transformer
TRANSFORMER_CONFIG = {
    "model_name": "distilbert-base-multilingual-cased",
    "max_length": 128,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "num_epochs": 3,
    "weight_decay": 0.01,
    "warmup_steps": 500,
}

# Configuration MLflow
MLFLOW_CONFIG = {
    "tracking_uri": os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"),
    "experiment_name": "CallCenterAI-Transformer",
    "registered_model_name": "CallCenterAI-Transformer"
}

# Configuration des données
DATA_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "min_text_length": 10,  # Longueur minimale d'un ticket
}

# Configuration API
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8001,
    "title": "CallCenterAI Transformer API",
    "description": "API de classification de tickets avec Transformer",
    "version": "1.0.0"
}

# Configuration Prometheus
PROMETHEUS_CONFIG = {
    "port": 9091,
    "metrics_path": "/metrics"
}

# Catégories de tickets (sera mis à jour dynamiquement)
TICKET_CATEGORIES = [
    "Hardware",
    "HR Support",
    "Access",
    "Miscellaneous",
    "Storage",
    "Purchase",
    "Network",
    "Software"
]