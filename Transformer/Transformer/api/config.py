"""
Configuration de l'API - Version Hugging Face
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration du modèle Hugging Face
# Changez ceci par votre username/modèle
HF_MODEL_NAME = os.getenv(
    'HF_MODEL_NAME',
    'Kahouli/callcenter-ticket-classifier'  # Votre modèle sur HF
)

# Option : utiliser le modèle local si disponible (fallback)
USE_LOCAL_MODEL = os.getenv('USE_LOCAL_MODEL', 'False').lower() == 'true'
LOCAL_MODEL_PATH = os.getenv(
    'LOCAL_MODEL_PATH',
    os.path.join(os.path.dirname(__file__), '..', 'models', 'transformer', 'best_model')
)

# Configuration FastAPI
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))
API_RELOAD = os.getenv('API_RELOAD', 'False').lower() == 'true'

# Configuration du modèle
MAX_LENGTH = 128
BATCH_SIZE = 32
USE_GPU = os.getenv('USE_GPU', 'True').lower() == 'true'

# Token Hugging Face (optionnel pour modèles publics)
HF_TOKEN = os.getenv('HF_TOKEN', None)

# Configuration MLflow (optionnel maintenant)
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
MLFLOW_EXPERIMENT_NAME = os.getenv('MLFLOW_EXPERIMENT_NAME', 'ticket_classification')

# Configuration Prometheus
PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', 8001))

print(f"Configuration chargée :")
if USE_LOCAL_MODEL:
    print(f"  Mode: LOCAL")
    print(f"  Model path: {LOCAL_MODEL_PATH}")
else:
    print(f"  Mode: HUGGING FACE")
    print(f"  Model: {HF_MODEL_NAME}")
print(f"  API host: {API_HOST}:{API_PORT}")
print(f"  Use GPU: {USE_GPU}")