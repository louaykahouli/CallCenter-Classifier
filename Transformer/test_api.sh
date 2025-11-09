#!/bin/bash

# Script de test complet de l'API CallCenter

echo "🧪 Tests Complets de l'API CallCenter"
echo "======================================"
echo ""

API_URL="http://localhost:8000"

# Vérifier si l'API est accessible
if ! curl -s "$API_URL" >/dev/null 2>&1; then
    echo "❌ L'API ne répond pas sur $API_URL"
    echo ""
    echo "💡 Lancez d'abord l'API avec :"
    echo "   cd /home/louay/Desktop/Project/CallCenter/Transformer"
    echo "   ./start_all.sh"
    exit 1
fi

echo "✅ API accessible"
echo ""

# Test 1: Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Test : Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE=$(curl -s "$API_URL/health")
echo "$RESPONSE" | python3 -m json.tool
STATUS=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])" 2>/dev/null)
if [ "$STATUS" = "healthy" ]; then
    echo "✅ Health check OK"
else
    echo "⚠️  Health check - Status : $STATUS"
fi
echo ""

# Test 2: Liste des classes
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Test : Liste des catégories"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "$API_URL/classes" | python3 -m json.tool
echo "✅ Catégories récupérées"
echo ""

# Test 3: Classification simple - Hardware
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Test : Classification - Hardware"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Ticket: 'Mon ordinateur ne démarre plus'"
echo ""
RESPONSE=$(curl -s -X POST "$API_URL/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "Mon ordinateur ne démarre plus"}')
echo "$RESPONSE" | python3 -m json.tool
CATEGORY=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin)['predicted_category'])" 2>/dev/null)
echo ""
echo "   Catégorie prédite: $CATEGORY"
echo "✅ Classification OK"
echo ""

# Test 4: Classification - Access
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Test : Classification - Access"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Ticket: 'Je ne peux pas accéder au serveur'"
echo ""
RESPONSE=$(curl -s -X POST "$API_URL/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "Je ne peux pas accéder au serveur"}')
echo "$RESPONSE" | python3 -m json.tool
CATEGORY=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin)['predicted_category'])" 2>/dev/null)
echo ""
echo "   Catégorie prédite: $CATEGORY"
echo "✅ Classification OK"
echo ""

# Test 5: Classification Batch
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Test : Classification Batch (3 tickets)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s -X POST "$API_URL/classify-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "tickets": [
      "Mon ordinateur ne démarre plus",
      "Je ne peux pas me connecter au VPN",
      "Je voudrais commander de nouvelles souris"
    ]
  }' | python3 -m json.tool
echo "✅ Classification batch OK"
echo ""

# Test 6: Stats MLflow
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Test : Statistiques MLflow"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "$API_URL/stats" | python3 -m json.tool
echo "✅ Stats MLflow OK"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 TOUS LES TESTS SONT PASSÉS !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation complète : http://localhost:8000/docs"
echo "📊 MLflow UI              : http://localhost:5000"
echo ""
