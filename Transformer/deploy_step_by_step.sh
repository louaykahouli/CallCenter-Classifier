#!/bin/bash

# Guide interactif - Étape par étape

echo "════════════════════════════════════════════════════════════════"
echo "🚀 DÉPLOIEMENT HUGGING FACE - GUIDE ÉTAPE PAR ÉTAPE"
echo "════════════════════════════════════════════════════════════════"
echo ""

# ÉTAPE 1
echo "📋 ÉTAPE 1/5 : Vérification du modèle"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -d "models/transformer/best_model" ]; then
    echo "❌ Erreur : Le modèle n'existe pas !"
    echo "   Entraînez d'abord avec : python3 src/train_transformer.py"
    exit 1
fi

echo "✅ Modèle trouvé !"
ls -lh models/transformer/best_model/ | grep -E "\.(bin|json|txt|safetensors)$" | awk '{print "   •", $9, "(" $5 ")"}'
echo ""

# ÉTAPE 2
echo "📋 ÉTAPE 2/5 : Compte Hugging Face"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📌 Avez-vous un compte sur Hugging Face ?"
echo "   Si NON → Créez-en un sur : https://huggingface.co/join"
echo "   Si OUI → Continuez !"
echo ""
read -p "Appuyez sur Entrée quand vous avez un compte..." dummy
echo "✅ OK !"
echo ""

# ÉTAPE 3
echo "📋 ÉTAPE 3/5 : Obtenir votre Token"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 Comment obtenir votre token :"
echo ""
echo "   1. Allez sur : https://huggingface.co/settings/tokens"
echo "   2. Cliquez sur 'Create new token'"
echo "   3. Nom du token : 'callcenter-deploy'"
echo "   4. Type : Sélectionnez 'Write' ⬅️ IMPORTANT !"
echo "   5. Cliquez 'Generate'"
echo "   6. Copiez le token (commence par hf_...)"
echo ""
echo "📋 Le token ressemble à : hf_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"
echo ""

if [ -z "$HF_TOKEN" ]; then
    read -p "Collez votre token ici : " token
    if [ -z "$token" ]; then
        echo "❌ Aucun token fourni. Abandon."
        exit 1
    fi
    export HF_TOKEN="$token"
    echo ""
    echo "✅ Token configuré !"
    echo "💡 Pour le garder, ajoutez dans ~/.bashrc :"
    echo "   export HF_TOKEN=\"$token\""
else
    echo "✅ Token déjà configuré (HF_TOKEN existe)"
fi
echo ""

# ÉTAPE 4
echo "📋 ÉTAPE 4/5 : Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Entrez votre username Hugging Face : " username

if [ -z "$username" ]; then
    echo "❌ Username requis. Abandon."
    exit 1
fi

read -p "Nom du repository [callcenter-ticket-classifier] : " repo_name
repo_name=${repo_name:-callcenter-ticket-classifier}

echo ""
echo "📝 Configuration finale :"
echo "   • Username : $username"
echo "   • Repository : $repo_name"
echo "   • URL future : https://huggingface.co/$username/$repo_name"
echo ""

# ÉTAPE 5
echo "📋 ÉTAPE 5/5 : Déploiement"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Lancer le déploiement ? (o/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[OoYy]$ ]]; then
    echo "❌ Déploiement annulé"
    exit 0
fi

echo ""
echo "🚀 Déploiement en cours..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Lancer le déploiement
python3 deploy_to_huggingface.py \
    --username "$username" \
    --repo-name "$repo_name" \
    --token "$HF_TOKEN"

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "🎉 DÉPLOIEMENT RÉUSSI !"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "📍 Votre modèle est maintenant disponible sur :"
    echo "   https://huggingface.co/$username/$repo_name"
    echo ""
    echo "🔗 API Inference (gratuite) :"
    echo "   https://api-inference.huggingface.co/models/$username/$repo_name"
    echo ""
    echo "💡 Pour tester :"
    echo "   python3 test_hf_api.py"
    echo ""
    echo "📚 Utilisation dans votre code :"
    echo ""
    echo "   from transformers import pipeline"
    echo "   classifier = pipeline('text-classification', model='$username/$repo_name')"
    echo "   result = classifier('Mon ordinateur ne démarre plus')"
    echo ""
else
    echo ""
    echo "❌ Erreur lors du déploiement"
    echo "Vérifiez les messages d'erreur ci-dessus"
fi
