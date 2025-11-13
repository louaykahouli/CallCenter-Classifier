#!/bin/bash

# Script d'aide pour déployer sur Hugging Face

echo "🚀 Guide de déploiement Hugging Face"
echo "===================================="
echo ""
echo "📋 Étape 1 : Obtenir votre token"
echo "   → Allez sur : https://huggingface.co/settings/tokens"
echo "   → Créez un nouveau token avec droits 'Write'"
echo "   → Copiez le token (il commence par hf_...)"
echo ""
echo "📋 Étape 2 : Configurer le token"
echo "   → Copiez cette commande et remplacez YOUR_TOKEN :"
echo ""
echo "   export HF_TOKEN=\"YOUR_TOKEN\""
echo ""
echo "📋 Étape 3 : Modifier le username"
echo "   → Ouvrez deploy_to_huggingface.py"
echo "   → Ligne 92, changez le username par le vôtre"
echo ""
echo "📋 Étape 4 : Lancer le déploiement"
echo "   → python deploy_to_huggingface.py"
echo ""
echo "===================================="
echo ""

# Vérifier si le token est défini
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  HF_TOKEN n'est pas défini"
    echo ""
    read -p "Voulez-vous le définir maintenant ? (o/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        read -p "Entrez votre token HF: " token
        export HF_TOKEN="$token"
        echo "✅ Token défini pour cette session"
        echo ""
        echo "Pour le garder de façon permanente, ajoutez dans ~/.bashrc :"
        echo "export HF_TOKEN=\"$token\""
    fi
else
    echo "✅ HF_TOKEN est défini"
fi

echo ""
echo "Prêt à déployer ? Voici la commande :"
echo ""
echo "python deploy_to_huggingface.py"
