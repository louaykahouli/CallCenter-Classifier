#!/bin/bash

# Script pour démarrer MLflow UI

echo "🎯 Démarrage de MLflow UI"
echo "========================="
echo ""

cd /home/louay/Desktop/Project/CallCenter

# Activer l'environnement virtuel
source .venv/bin/activate

# Vérifier si MLflow est installé
if ! python -c "import mlflow" 2>/dev/null; then
    echo "⚠️  Installation de MLflow..."
    pip install mlflow -q
fi

echo "✅ MLflow installé"
echo ""

# Vérifier si le port 5000 est libre
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Le port 5000 est déjà utilisé"
    read -p "Voulez-vous arrêter le processus existant ? (o/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        kill $(lsof -t -i:5000) 2>/dev/null
        sleep 2
        echo "✅ Port libéré"
    else
        echo "💡 MLflow utilisera le port 5000 actuel"
    fi
fi

echo ""
echo "📊 MLflow UI sera accessible sur :"
echo "   http://localhost:5000"
echo ""
echo "💡 Laissez ce terminal ouvert pour garder MLflow actif"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Lancement de MLflow UI..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Lancer MLflow UI
cd Transformer
mlflow ui --host 0.0.0.0 --port 5000

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "MLflow UI arrêté"
