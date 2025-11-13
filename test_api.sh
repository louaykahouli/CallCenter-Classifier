#!/bin/bash
# Script de test de l'API CallCenter Classifier
# Usage: ./test_api.sh

API_URL="http://localhost:8000"

echo "=========================================="
echo "🧪 Tests de l'API CallCenter Classifier"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "1️⃣  Test /health"
echo "---"
curl -s "${API_URL}/health" | jq .
echo ""
echo ""

# Test 2: Liste des classes
echo "2️⃣  Test /classes"
echo "---"
curl -s "${API_URL}/classes" | jq .
echo ""
echo ""

# Test 3: Stats MLflow
echo "3️⃣  Test /stats"
echo "---"
curl -s "${API_URL}/stats" | jq .
echo ""
echo ""

# Test 4: Classification simple - Hardware
echo "4️⃣  Test /classify - Ticket Hardware"
echo "---"
curl -s -X POST "${API_URL}/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "Mon ordinateur ne démarre plus après la mise à jour"}' | jq .
echo ""
echo ""

# Test 5: Classification simple - Purchase
echo "5️⃣  Test /classify - Ticket Purchase"
echo "---"
curl -s -X POST "${API_URL}/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "Je voudrais commander 10 souris sans fil pour léquipe"}' | jq .
echo ""
echo ""

# Test 6: Classification simple - HR Support
echo "6️⃣  Test /classify - Ticket HR Support"
echo "---"
curl -s -X POST "${API_URL}/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "Demande de congés pour la semaine prochaine"}' | jq .
echo ""
echo ""

# Test 7: Classification simple - Access
echo "7️⃣  Test /classify - Ticket Access"
echo "---"
curl -s -X POST "${API_URL}/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "Je ne peux pas accéder au dossier partagé du projet"}' | jq .
echo ""
echo ""

# Test 8: Batch classification
echo "8️⃣  Test /classify-batch - Multiple tickets"
echo "---"
curl -s -X POST "${API_URL}/classify-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "tickets": [
      "Mon écran ne fonctionne plus",
      "Je ne peux pas me connecter au VPN",
      "Demande daugmentation de salaire",
      "Besoin dacheter des câbles HDMI"
    ]
  }' | jq .
echo ""
echo ""

echo "=========================================="
echo "✅ Tests terminés!"
echo "=========================================="
echo ""
echo "📊 MLflow UI: http://localhost:5000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
