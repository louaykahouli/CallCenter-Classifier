#!/bin/bash

# Script de lancement complet du projet CallCenter

echo "🚀 Lancement du projet CallCenter - API Hugging Face"
echo "======================================================="
echo ""

# Vérifier qu'on est dans le bon dossier
if [ ! -d "/home/louay/Desktop/Project/CallCenter" ]; then
    echo "❌ Erreur : Dossier projet non trouvé"
    exit 1
fi

cd /home/louay/Desktop/Project/CallCenter

# Vérifier l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo "❌ Environnement virtuel non trouvé"
    echo "   Créez-le avec : python3 -m venv .venv"
    exit 1
fi

echo "✅ Environnement virtuel trouvé"

# Activer l'environnement virtuel
source .venv/bin/activate

echo "✅ Environnement virtuel activé"
echo ""

# Vérifier les dépendances critiques
echo "🔍 Vérification des dépendances..."

if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Installation de fastapi..."
    pip install fastapi uvicorn -q
fi

if ! python -c "import transformers" 2>/dev/null; then
    echo "⚠️  Installation de transformers..."
    pip install transformers -q
fi

if ! python -c "import torch" 2>/dev/null; then
    echo "⚠️  Installation de torch..."
    pip install torch --index-url https://download.pytorch.org/whl/cpu -q
fi

echo "✅ Dépendances OK"
echo ""

# Vérifier le port
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Le port 8000 est déjà utilisé"
    read -p "Voulez-vous arrêter le processus existant ? (o/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        kill $(lsof -t -i:8000) 2>/dev/null
        sleep 2
        echo "✅ Port libéré"
    else
        echo "💡 Utilisez un autre port avec : --port 8001"
    fi
fi

echo ""
echo "📋 Configuration :"
echo "   • Modèle : Hugging Face (Kahouli/callcenter-ticket-classifier)"
echo "   • Port   : 8000"
echo "   • Host   : 0.0.0.0"
echo ""
echo "⏳ Première fois : Le modèle sera téléchargé (541 MB, ~2-3 min)"
echo "   Ensuite : Démarrage instantané (cache local)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Lancement de l'API..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Lancer l'API
cd Transformer
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Si l'API s'arrête
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API arrêtée"
