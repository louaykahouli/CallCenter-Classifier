"""
Test de l'agent Grok avec API réelle
"""

from grok_agent import GrokAgent

# Votre clé API Grok
GROK_API_KEY = "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"

# Test simple
print("🧪 Test de l'API Grok...")
print("-" * 80)

# Créer l'agent avec Grok activé
agent = GrokAgent(api_key=GROK_API_KEY, use_grok=True)

# Test avec un ticket simple
test_ticket = "Mon écran ne s'allume plus"

print(f"\n📝 Ticket: {test_ticket}")
print("\n⏳ Analyse avec Grok AI...")

try:
    result = agent.analyze_and_route(test_ticket)
    
    print("\n✅ Résultat:")
    print(f"  🎯 Modèle recommandé: {result['model'].upper()}")
    print(f"  📊 Score de complexité: {result['complexity_score']}/100")
    print(f"  🤖 Grok utilisé: {'Oui' if result['grok_used'] else 'Non'}")
    print(f"\n  💡 Analyse de Grok:")
    print(f"  {result['reasoning']}")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    print("\nPossibles causes:")
    print("  - Clé API invalide ou expirée")
    print("  - Problème de connexion internet")
    print("  - Limite de quota atteinte")
