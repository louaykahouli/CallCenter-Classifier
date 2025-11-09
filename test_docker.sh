#!/bin/bash

# Script de test Docker

echo "🐳 Test de la configuration Docker"
echo "===================================="
echo ""

cd /home/louay/Desktop/Project/CallCenter

# 1. Vérifier Docker
echo "📋 Étape 1/4 : Vérification de Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi
echo "✅ Docker $(docker --version)"
echo ""

# 2. Vérifier Docker Compose
echo "📋 Étape 2/4 : Vérification de Docker Compose..."
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose (intégré) $(docker compose version)"
elif command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose (standalone) $(docker-compose --version)"
else
    echo "❌ Docker Compose n'est pas disponible"
    exit 1
fi
echo ""

# 3. Vérifier les fichiers
echo "📋 Étape 3/4 : Vérification des fichiers Docker..."
FILES=("Dockerfile" "docker-compose.yml" "docker-entrypoint.sh" ".dockerignore")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file manquant"
        exit 1
    fi
done
echo ""

# 4. Tester la construction (dry-run)
echo "📋 Étape 4/4 : Validation de la configuration..."
docker compose config > /dev/null 2>&1 || docker-compose config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Configuration Docker Compose valide"
else
    echo "❌ Erreur dans docker-compose.yml"
    exit 1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Configuration Docker validée !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Pour construire et lancer :"
echo ""
echo "   # Construction de l'image (~5-10 minutes au premier lancement)"
echo "   docker compose build"
echo ""
echo "   # Lancement"
echo "   docker compose up -d"
echo ""
echo "   # Voir les logs"
echo "   docker compose logs -f"
echo ""
echo "   # Tests"
echo "   curl http://localhost:8000/health"
echo ""
echo "   # Arrêter"
echo "   docker compose down"
echo ""
