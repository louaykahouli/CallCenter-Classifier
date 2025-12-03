#!/bin/bash
set -e

echo "🚀 Starting CallCenter Classifier..."

# Fonction pour démarrer l'API
start_api() {
    echo "📡 Starting API on port 8000..."
    cd /app
    exec uvicorn api.main:app --host 0.0.0.0 --port 8000
}

# Fonction pour démarrer MLflow
start_mlflow() {
    echo "📊 Starting MLflow UI on port 5000..."
    cd /app
    exec mlflow ui --host 0.0.0.0 --port 5000 --backend-store-uri /app/mlruns
}

# Fonction pour lancer les deux
start_all() {
    echo "🚀 Starting MLflow and API..."
    cd /app

    # Démarrer MLflow en arrière-plan
    mlflow ui --host 0.0.0.0 --port 5000 --backend-store-uri /app/mlruns &

    # Attendre que MLflow démarre
    sleep 5

    # Démarrer l'API
    exec uvicorn api.main:app --host 0.0.0.0 --port 8000
}

# Déterminer quelle commande exécuter
case "${1:-api}" in
    api)
        start_api
        ;;
    mlflow)
        start_mlflow
        ;;
    all)
        start_all
        ;;
    *)
        echo "Usage: $0 {api|mlflow|all}"
        exit 1
        ;;
esac
