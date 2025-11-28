#!/usr/bin/env python3
"""
Test de toutes les catégories avec des exemples spécifiques
Utilise des mots-clés forts pour chaque catégorie
"""

import requests
import json
import time

API_URL = "http://localhost:8002/predict"

# Exemples spécifiques avec mots-clés forts pour chaque catégorie
TEST_CASES = {
    "Hardware": "Mon ordinateur Dell ne démarre plus, l'écran reste noir, le ventilateur tourne mais rien ne s'affiche",
    
    "HR Support": "Je souhaite poser mes congés payés du 15 au 30 décembre, merci de valider ma demande de congé dans le système RH",
    
    "Access": "J'ai besoin des droits d'accès au serveur SharePoint et à la base de données SQL, mon login est bloqué",
    
    "Purchase": "Je voudrais commander 5 licences Microsoft Office 365 et 3 claviers sans fil Logitech pour mon équipe",
    
    "Storage": "Mon espace disque réseau est plein, j'ai besoin de plus d'espace sur le drive Z: pour stocker les fichiers du projet",
    
    "Administrative rights": "J'ai besoin des droits administrateur local sur ma machine pour installer Visual Studio et Docker Desktop",
    
    "Internal Project": "Mise à jour du projet ERP SAP : planning, ressources, budget 500K€, équipe de 10 personnes, deadline Q2 2025",
    
    "Miscellaneous": "Question sur la politique de télétravail et les procédures générales de l'entreprise"
}

def test_category(category, text):
    """Test une catégorie spécifique"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {category}")
    print(f"{'='*80}")
    print(f"📝 Texte: {text[:70]}...")
    
    try:
        response = requests.post(API_URL, json={
            "text": text,
            "session_id": f"test-{category.lower().replace(' ', '-')}-{int(time.time())}",
            "conversation_title": f"Test {category}"
        }, timeout=15)
        
        response.raise_for_status()
        data = response.json()
        
        prediction = data['prediction']
        model_used = data['model_used']
        complexity = data['complexity_analysis']['score']
        
        # Vérifier si la prédiction est correcte
        is_correct = prediction == category
        symbol = "✅" if is_correct else "❌"
        
        print(f"{symbol} Prédiction: {prediction}")
        print(f"🤖 Modèle: {model_used.upper()}")
        print(f"📊 Complexité: {complexity:.1f}/100")
        
        # Afficher les top 3 probabilités
        print(f"\n📈 Top 3 probabilités:")
        sorted_probs = sorted(data['probabilities'].items(), key=lambda x: x[1], reverse=True)[:3]
        for cat, prob in sorted_probs:
            bar = "█" * int(prob * 30)
            check = "✓" if cat == category else " "
            print(f"  {check} {cat:25s} {prob:5.1%} {bar}")
        
        return is_correct
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("=" * 80)
    print("🎯 TEST DE TOUTES LES CATÉGORIES")
    print("=" * 80)
    
    results = {}
    
    for category, text in TEST_CASES.items():
        results[category] = test_category(category, text)
        time.sleep(0.5)  # Petite pause entre les tests
    
    # Résumé
    print(f"\n{'='*80}")
    print("📊 RÉSUMÉ DES RÉSULTATS")
    print(f"{'='*80}")
    
    correct = sum(results.values())
    total = len(results)
    
    for category, is_correct in results.items():
        symbol = "✅" if is_correct else "❌"
        print(f"{symbol} {category:30s} {'CORRECT' if is_correct else 'INCORRECT'}")
    
    print(f"\n🎯 Score final: {correct}/{total} ({correct*100/total:.1f}%)")
    
    if correct == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
    elif correct >= total * 0.7:
        print("⚠️  Résultats acceptables mais peut améliorer")
    else:
        print("❌ Le modèle a besoin d'améliorations")

if __name__ == "__main__":
    main()
