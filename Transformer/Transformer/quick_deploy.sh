#!/bin/bash

# 🚀 Script de déploiement rapide sur Hugging Face
# Usage: ./quick_deploy.sh VOTRE_USERNAME VOTRE_TOKEN

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║  🚀 Déploiement Hugging Face - CallCenter AI  ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# Vérifier les arguments
if [ "$#" -lt 1 ]; then
    echo -e "${RED}❌ Erreur: Username manquant${NC}"
    echo ""
    echo "Usage: $0 VOTRE_USERNAME [VOTRE_TOKEN]"
    echo ""
    echo "Exemples:"
    echo "  $0 louay                          # Token via variable HF_TOKEN"
    echo "  $0 louay hf_xxxxxxxxxxxxx         # Token en argument"
    echo ""
    exit 1
fi

USERNAME=$1
TOKEN=${2:-$HF_TOKEN}

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Erreur: Token manquant${NC}"
    echo ""
    echo "Obtenez votre token sur: https://huggingface.co/settings/tokens"
    echo ""
    echo "Puis utilisez:"
    echo "  export HF_TOKEN=votre_token"
    echo "  $0 $USERNAME"
    echo ""
    echo "Ou:"
    echo "  $0 $USERNAME votre_token"
    echo ""
    exit 1
fi

# Configuration
REPO_NAME="callcenter-ticket-classifier"
MODEL_PATH="./models/transformer/best_model"

# Vérifier que le modèle existe
if [ ! -d "$MODEL_PATH" ]; then
    echo -e "${RED}❌ Erreur: Modèle introuvable: $MODEL_PATH${NC}"
    echo ""
    echo "Entraînez d'abord le modèle avec:"
    echo "  python src/train_transformer.py"
    echo ""
    exit 1
fi

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   Username: $USERNAME"
echo "   Repo: $REPO_NAME"
echo "   Model: $MODEL_PATH"
echo ""

# Vérifier/installer les dépendances
echo -e "${BLUE}📦 Vérification des dépendances...${NC}"
if ! python -c "import huggingface_hub" 2>/dev/null; then
    echo -e "${YELLOW}   Installation de huggingface_hub...${NC}"
    pip install -q huggingface_hub
fi
echo -e "${GREEN}   ✓ Dépendances OK${NC}"
echo ""

# Déployer
echo -e "${BLUE}🚀 Déploiement en cours...${NC}"
python deploy_to_huggingface.py \
    --username "$USERNAME" \
    --repo-name "$REPO_NAME" \
    --token "$TOKEN" \
    --model-path "$MODEL_PATH"

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════╗"
echo "║            ✅ Déploiement Réussi!             ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${BLUE}🔗 Votre modèle est disponible sur:${NC}"
echo "   https://huggingface.co/$USERNAME/$REPO_NAME"
echo ""

echo -e "${BLUE}📝 Pour l'utiliser:${NC}"
echo ""
echo "   # Python"
cat << 'EOF'
   from transformers import pipeline
   classifier = pipeline("text-classification", 
                        model="USERNAME/REPO")
   result = classifier("Mon imprimante ne fonctionne pas")
EOF
echo ""

echo -e "${BLUE}🌐 API Hugging Face:${NC}"
echo ""
cat << 'EOF'
   import requests
   
   API_URL = "https://api-inference.huggingface.co/models/USERNAME/REPO"
   headers = {"Authorization": f"Bearer {YOUR_TOKEN}"}
   
   response = requests.post(API_URL, 
                           headers=headers,
                           json={"inputs": "Votre texte"})
   print(response.json())
EOF
echo ""

echo -e "${YELLOW}💡 Prochaines étapes:${NC}"
echo "   1. Testez votre modèle sur la page Hugging Face"
echo "   2. Créez un Space pour une interface web (optionnel)"
echo "   3. Utilisez l'Inference API dans votre application"
echo ""
echo -e "${GREEN}🎉 Bravo! Votre modèle est maintenant public et utilisable!${NC}"
