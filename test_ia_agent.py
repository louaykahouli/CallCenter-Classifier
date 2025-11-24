#!/usr/bin/env python3
"""
Script de test pour l'Agent IA Intelligent
"""

import requests
import json

# URL de l'agent IA
IA_AGENT_URL = "http://localhost:8002"

def test_health():
    """Test du endpoint /health"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    response = requests.get(f"{IA_AGENT_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_analyze(text):
    """Test du endpoint /analyze"""
    print("\n" + "="*80)
    print("TEST 2: Analyse de complexité")
    print("="*80)
    print(f"Texte: {text}")
    print("-"*80)
    
    response = requests.post(
        f"{IA_AGENT_URL}/analyze",
        json={"text": text}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"\n📊 Complexité: {result['complexity_score']}/100 ({result['complexity_level']})")
    print(f"🤖 Modèle recommandé: {result['recommended_model'].upper()}")
    print(f"💡 Raisonnement: {result['reasoning']}")
    print(f"\nDétails:")
    print(json.dumps(result['details'], indent=2, ensure_ascii=False))


def test_predict(text, force_model=None):
    """Test du endpoint /predict"""
    print("\n" + "="*80)
    print("TEST 3: Prédiction avec routage intelligent")
    print("="*80)
    print(f"Texte: {text}")
    if force_model:
        print(f"Modèle forcé: {force_model}")
    print("-"*80)
    
    payload = {"text": text}
    if force_model:
        payload["force_model"] = force_model
    
    response = requests.post(
        f"{IA_AGENT_URL}/predict",
        json=payload
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"\n🎯 Prédiction: {result['prediction']}")
    print(f"🤖 Modèle utilisé: {result['model_used'].upper()}")
    print(f"📊 Complexité: {result['complexity_analysis']['score']}/100")
    print(f"💡 Raisonnement: {result['reasoning']}")
    
    print(f"\n📈 Probabilités:")
    for category, prob in sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {category}: {prob:.2%}")


def test_stats():
    """Test du endpoint /stats"""
    print("\n" + "="*80)
    print("TEST 4: Statistiques d'utilisation")
    print("="*80)
    
    response = requests.get(f"{IA_AGENT_URL}/stats")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Exemples de textes avec différentes complexités
    exemples = [
        "Imprimante cassée",  # Simple → TF-IDF
        "Je n'arrive pas à me connecter au VPN de l'entreprise depuis ce matin",  # Moyen
        "Plusieurs utilisateurs du département RH signalent des problèmes d'accès intermittents au serveur partagé depuis l'installation du nouveau pare-feu la semaine dernière",  # Complexe → Transformer
    ]
    
    print("\n" + "🤖 "*20)
    print("TEST DE L'AGENT IA INTELLIGENT")
    print("🤖 "*20)
    
    # Test 1: Health check
    try:
        test_health()
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2 & 3: Pour chaque exemple
    for i, text in enumerate(exemples, 1):
        print(f"\n\n{'='*80}")
        print(f"EXEMPLE {i}")
        print(f"{'='*80}")
        
        try:
            # Analyse de complexité
            test_analyze(text)
            
            # Prédiction avec routage automatique
            test_predict(text)
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    # Test avec forçage du modèle
    print(f"\n\n{'='*80}")
    print(f"TEST AVEC FORÇAGE DU MODÈLE")
    print(f"{'='*80}")
    try:
        test_predict("Mon ordinateur ne démarre plus", force_model="transformer")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 4: Statistiques
    try:
        test_stats()
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*80)
    print("✅ Tests terminés!")
    print("="*80)
