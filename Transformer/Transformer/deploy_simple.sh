#!/bin/bash

# Script simple pour déployer sur Hugging Face
# Usage: ./deploy_simple.sh

echo "════════════════════════════════════════════════════════"
echo "🚀 Déploiement sur Hugging Face - Guide Interactif"
echo "════════════════════════════════════════════════════════"
echo ""

# Vérifier si le modèle existe
if [ ! -d "models/transformer/best_model" ]; then
    echo "❌ Erreur : Le modèle n'existe pas !"
    echo "   Chemin attendu : models/transformer/best_model/"
    echo ""
    echo "   Entraînez d'abord le modèle avec :"
    echo "   python src/train_transformer.py"
    exit 1
fi

echo "✅ Modèle trouvé dans models/transformer/best_model/"
echo ""

# Vérifier le token HF
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  Token Hugging Face non trouvé"
    echo ""
    echo "📋 Pour obtenir votre token :"
    echo "   1. Allez sur : https://huggingface.co/settings/tokens"
    echo "   2. Créez un token avec droits 'Write'"
    echo "   3. Copiez le token"
    echo ""
    read -p "Collez votre token HF ici : " token
    
    if [ -z "$token" ]; then
        echo "❌ Aucun token fourni. Abandon."
        exit 1
    fi
    
    export HF_TOKEN="$token"
    echo ""
    echo "✅ Token configuré pour cette session"
    echo ""
    echo "💡 Astuce : Pour le garder, ajoutez dans ~/.bashrc :"
    echo "   export HF_TOKEN=\"$token\""
    echo ""
else
    echo "✅ Token Hugging Face trouvé"
    echo ""
fi

# Demander le username
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Entrez votre username Hugging Face : " username

if [ -z "$username" ]; then
    echo "❌ Username requis. Abandon."
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Configuration :"
echo "   • Username : $username"
echo "   • Repo    : callcenter-ticket-classifier"
echo "   • URL     : https://huggingface.co/$username/callcenter-ticket-classifier"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Confirmer le déploiement ? (o/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[OoYy]$ ]]; then
    echo "❌ Déploiement annulé"
    exit 1
fi

echo ""
echo "🚀 Lancement du déploiement..."
echo ""

# Créer un script Python temporaire avec le username
cat > /tmp/deploy_hf_temp.py << EOF
import os
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent))

# Importer et utiliser le deployer
from deploy_to_huggingface import HuggingFaceDeployer

# Configurer
deployer = HuggingFaceDeployer(
    model_path="./models/transformer/best_model",
    repo_name="callcenter-ticket-classifier",
    username="$username"
)

# Déployer
print("\n🔄 Préparation du modèle...")
deployer.prepare_model_card()

print("📤 Upload vers Hugging Face...")
try:
    deployer.deploy()
    print("\n" + "="*60)
    print("🎉 DÉPLOIEMENT RÉUSSI !")
    print("="*60)
    print(f"\n📍 Votre modèle : https://huggingface.co/$username/callcenter-ticket-classifier")
    print(f"🔗 API Inference : https://api-inference.huggingface.co/models/$username/callcenter-ticket-classifier")
    print("\n💡 Testez avec : python test_hf_api.py")
except Exception as e:
    print(f"\n❌ Erreur lors du déploiement : {e}")
    sys.exit(1)
EOF

# Lancer le déploiement
python /tmp/deploy_hf_temp.py

# Nettoyer
rm /tmp/deploy_hf_temp.py

echo ""
echo "✅ Script terminé"
