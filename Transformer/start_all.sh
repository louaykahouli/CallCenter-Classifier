#!/bin/bash

# Script pour lancer TOUT le projet (MLflow + API)

echo "🚀 Lancement COMPLET du projet CallCenter"
echo "=========================================="
echo ""

cd /home/louay/Desktop/Project/CallCenter

# Vérifier l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo "❌ Environnement virtuel non trouvé"
    exit 1
fi

echo "✅ Projet : /home/louay/Desktop/Project/CallCenter"
echo ""

# Activer l'environnement virtuel
source .venv/bin/activate

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ÉTAPE 1/2 : Lancement de MLflow UI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier si MLflow tourne déjà
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ MLflow UI déjà en cours sur le port 5000"
else
    echo "🔄 Démarrage de MLflow UI en arrière-plan..."
    cd Transformer
    nohup mlflow ui --host 0.0.0.0 --port 5000 > ../mlflow.log 2>&1 &
    MLFLOW_PID=$!
    cd ..
    sleep 3
    
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ MLflow UI démarré (PID: $MLFLOW_PID)"
        echo "   Accessible sur: http://localhost:5000"
        echo "   Logs: mlflow.log"
    else
        echo "⚠️  Erreur démarrage MLflow (non bloquant)"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 ÉTAPE 2/2 : Lancement de l'API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier le port API
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Le port 8000 est déjà utilisé"
    read -p "Voulez-vous arrêter le processus existant ? (o/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        kill $(lsof -t -i:8000) 2>/dev/null
        sleep 2
    fi
fi

echo ""
echo "📋 Configuration :"
echo "   • API        : http://localhost:8000"
echo "   • MLflow UI  : http://localhost:5000"
echo "   • Docs API   : http://localhost:8000/docs"
echo "   • Modèle     : Hugging Face (Kahouli/callcenter-ticket-classifier)"
echo "   • Monitoring : MLflow activé"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 API en cours de démarrage..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Pour tester l'API, ouvrez un nouveau terminal et lancez :"
echo "   ./test_api_quick.sh"
echo ""
echo "📊 Pour voir les métriques en temps réel :"
echo "   http://localhost:5000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Lancer l'API (bloquant)
cd Transformer
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Cleanup si l'API s'arrête
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 API arrêtée"
echo ""
read -p "Voulez-vous arrêter MLflow aussi ? (o/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Oo]$ ]]; then
    if [ ! -z "$MLFLOW_PID" ]; then
        kill $MLFLOW_PID 2>/dev/null
    else
        kill $(lsof -t -i:5000) 2>/dev/null
    fi
    echo "✅ MLflow arrêté"
else
    echo "💡 MLflow continue sur http://localhost:5000"
fi

echo ""
echo "✅ Arrêt complet"
