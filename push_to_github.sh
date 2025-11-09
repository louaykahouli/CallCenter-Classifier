#!/bin/bash

# Script pour créer un nouveau dépôt GitHub

echo "🚀 Configuration du nouveau dépôt GitHub"
echo "========================================="
echo ""

cd /home/louay/Desktop/Project/CallCenter

# 1. Supprimer l'ancien remote (si existe)
echo "🔧 Étape 1/5 : Suppression de l'ancien remote..."
git remote remove origin 2>/dev/null
echo "✅ Fait"
echo ""

# 2. Ajouter tous les fichiers
echo "📦 Étape 2/5 : Ajout des fichiers..."
git add .
echo "✅ Fait"
echo ""

# 3. Vérifier les fichiers ajoutés
echo "📋 Fichiers à commiter :"
git status --short
echo ""

# 4. Commit
echo "💾 Étape 3/5 : Création du commit..."
git commit -m "Initial commit - CallCenter Ticket Classifier

- Classification de tickets avec Transformer (DistilBERT)
- API FastAPI avec endpoints REST
- Monitoring MLflow intégré
- Modèle déployé sur HuggingFace: Kahouli/callcenter-ticket-classifier
- 8 catégories de classification
- Documentation complète
"
echo "✅ Fait"
echo ""

# 5. Instructions pour la suite
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Étape 4/5 : CRÉER LE DÉPÔT SUR GITHUB"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Allez sur : https://github.com/new"
echo ""
echo "2. Remplissez :"
echo "   📌 Repository name : CallCenter-Classifier"
echo "   📝 Description     : Système de classification de tickets avec Transformer et MLflow"
echo "   🔓 Visibilité      : Public (ou Private si vous préférez)"
echo ""
echo "   ⚠️  IMPORTANT : Ne cochez PAS :"
echo "      ❌ Add a README file"
echo "      ❌ Add .gitignore"
echo "      ❌ Choose a license"
echo ""
echo "3. Cliquez sur 'Create repository'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 Étape 5/5 : CONNECTER ET POUSSER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Une fois le dépôt créé, exécutez ces commandes :"
echo ""
echo "git remote add origin https://github.com/louaykahouli/CallCenter-Classifier.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 CONSEIL : Copiez ces commandes pour les exécuter après avoir créé le dépôt"
echo ""

