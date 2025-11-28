#!/usr/bin/env python3
"""
Script de test complet pour l'Agent IA Intelligent
Teste la complexité, le cache, les conversations et les titres
"""

import requests
import json
import time
from typing import Dict, List

API_URL = "http://localhost:8002"

# Couleurs pour l'affichage
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_header(text: str):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_test(name: str):
    print(f"\n{YELLOW}🧪 TEST: {name}{RESET}")

def print_success(msg: str):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg: str):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg: str):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

# =============================================================================
# Tests de complexité variée
# =============================================================================

TEST_CASES = [
    {
        "name": "Complexité FAIBLE - Ticket simple",
        "text": "Mon imprimante ne marche pas",
        "expected_complexity": "low",
        "expected_model": "tfidf",
        "category": "Hardware"
    },
    {
        "name": "Complexité MOYENNE - Demande avec contexte",
        "text": "Bonjour, j'aimerais savoir comment je peux obtenir les accès administrateur pour installer un nouveau logiciel de comptabilité sur mon poste de travail. Merci",
        "expected_complexity": "medium",
        "expected_model": "tfidf",
        "category": "Administrative rights"
    },
    {
        "name": "Complexité ÉLEVÉE - Problème technique détaillé",
        "text": """Suite à la mise à jour du système d'exploitation Windows 11 version 23H2, 
        mon ordinateur Dell Latitude 7420 rencontre des problèmes de performances critiques. 
        L'utilisation CPU atteint constamment 100% même au repos, le ventilateur tourne en permanence, 
        et plusieurs applications métier (SAP, Oracle Database Client, Microsoft Teams) crashent aléatoirement. 
        J'ai déjà essayé de désinstaller les pilotes graphiques Intel et de les réinstaller, 
        vérifié l'intégrité du système avec sfc /scannow, et désactivé les applications au démarrage, 
        mais le problème persiste. De plus, le gestionnaire de tâches montre que le processus 
        'Windows Modules Installer Worker' consomme énormément de ressources. 
        Pourriez-vous m'aider à diagnostiquer et résoudre ce problème urgent ?""",
        "expected_complexity": "high",
        "expected_model": "transformer",
        "category": "Hardware"
    },
    {
        "name": "Complexité TRÈS ÉLEVÉE - Projet complexe multi-départements",
        "text": """Nous souhaitons mettre en place un nouveau système de gestion intégrée (ERP) 
        pour notre département financier et RH. Ce projet nécessite une coordination entre 
        plusieurs équipes : IT, Finance, Ressources Humaines et Management. 
        Nous avons besoin d'une analyse des besoins, d'une évaluation des solutions disponibles 
        (SAP S/4HANA, Oracle NetSuite, Microsoft Dynamics 365), d'un planning de migration des données, 
        d'une stratégie de formation des utilisateurs (environ 150 personnes), 
        et d'un plan de reprise d'activité en cas de problème. 
        Le budget alloué est de 500K€ sur 18 mois. Nous devons également nous assurer de la conformité 
        RGPD et de l'intégration avec nos systèmes existants (CRM Salesforce, plateforme BI Tableau, 
        système de paie ADP). Pouvez-vous nous aider à structurer ce projet et identifier 
        les ressources nécessaires ?""",
        "expected_complexity": "high",
        "expected_model": "transformer",
        "category": "Internal Project"
    },
    {
        "name": "Complexité TECHNIQUE - Problème réseau et sécurité",
        "text": """Depuis ce matin, plusieurs utilisateurs du département marketing rapportent 
        des problèmes d'accès au serveur de fichiers (NAS Synology DS920+, IP 192.168.1.50). 
        Les symptômes incluent : timeouts lors de la connexion SMB, impossibilité de mapper 
        les lecteurs réseau, et erreurs "Network path not found" (0x80070035). 
        J'ai vérifié : le ping vers le NAS fonctionne (latence 2ms), le pare-feu Windows autorise 
        SMB sur les ports 445 et 139, les services "Workstation" et "TCP/IP NetBIOS Helper" 
        sont démarrés, et les credentials sont corrects. Cependant, nslookup ne résout pas 
        le nom NetBIOS du serveur (NASSYNO01). De plus, certains utilisateurs peuvent accéder 
        via l'adresse IP directe (\\\\192.168.1.50) mais pas via le nom (\\\\NASSYNO01). 
        Le DHCP est configuré avec le DNS interne (192.168.1.1). Que dois-je vérifier ?""",
        "expected_complexity": "high",
        "expected_model": "transformer",
        "category": "Hardware"
    },
    {
        "name": "Complexité ACHAT - Demande d'équipement spécifique",
        "text": """Je souhaite commander pour mon équipe de développement : 
        3 MacBook Pro 16" M3 Max (64GB RAM, 2TB SSD), 
        3 écrans Dell UltraSharp U2723DE 27" 4K IPS, 
        3 docks USB-C Thunderbolt 4 CalDigit TS4, 
        6 licences JetBrains IntelliJ IDEA Ultimate (renouvellement annuel),
        et 3 licences Adobe Creative Cloud All Apps.
        Budget total estimé : 25 000€. Code projet : DEV-2024-Q4.
        Livraison souhaitée : avant fin décembre 2024.
        Validateur : Jean Dupont (CTO).""",
        "expected_complexity": "medium",
        "expected_model": "tfidf",
        "category": "Purchase"
    }
]

def test_complexity_and_routing():
    """Test le routage intelligent basé sur la complexité"""
    print_header("TEST DE COMPLEXITÉ ET ROUTAGE INTELLIGENT")
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print_test(f"{i}/{len(TEST_CASES)} - {test_case['name']}")
        
        session_id = f"test-complexity-{i}-{int(time.time())}"
        
        # Créer un titre basé sur les premiers 50 caractères
        title = test_case['text'][:50] + "..." if len(test_case['text']) > 50 else test_case['text']
        
        payload = {
            "text": test_case['text'],
            "session_id": session_id,
            "conversation_title": title
        }
        
        print_info(f"Longueur du texte: {len(test_case['text'])} caractères")
        
        start_time = time.time()
        
        try:
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            response_time = time.time() - start_time
            
            # Extraire les informations
            complexity_score = data['complexity_analysis']['score']
            complexity_level = data['complexity_analysis']['level']
            model_used = data['model_used']
            prediction = data['prediction']
            cache_hit = data.get('cache_hit', False)
            
            print_info(f"Temps de réponse: {response_time:.2f}s")
            print_info(f"Score de complexité: {complexity_score}/100")
            print_info(f"Niveau: {complexity_level}")
            print_info(f"Modèle utilisé: {model_used.upper()}")
            print_info(f"Prédiction: {prediction}")
            print_info(f"Cache: {'HIT ⚡' if cache_hit else 'MISS'}")
            
            # Vérifications
            success = True
            
            if model_used == test_case['expected_model']:
                print_success(f"Modèle correct: {model_used}")
            else:
                print_error(f"Modèle incorrect: attendu {test_case['expected_model']}, obtenu {model_used}")
                success = False
            
            if complexity_level == test_case['expected_complexity']:
                print_success(f"Niveau de complexité correct: {complexity_level}")
            else:
                print_info(f"Niveau de complexité: attendu {test_case['expected_complexity']}, obtenu {complexity_level}")
            
            results.append({
                "test": test_case['name'],
                "success": success,
                "complexity": complexity_score,
                "model": model_used,
                "prediction": prediction,
                "response_time": response_time
            })
            
        except requests.exceptions.RequestException as e:
            print_error(f"Erreur API: {e}")
            results.append({
                "test": test_case['name'],
                "success": False,
                "error": str(e)
            })
        
        time.sleep(0.5)  # Petite pause entre les tests
    
    return results

def test_cache_performance():
    """Test les performances du cache"""
    print_header("TEST DE PERFORMANCE DU CACHE")
    
    test_text = "Mon écran ne s'allume plus depuis ce matin"
    
    print_test("Première requête (sans cache)")
    start = time.time()
    response1 = requests.post(f"{API_URL}/predict", json={"text": test_text})
    time1 = time.time() - start
    data1 = response1.json()
    
    print_info(f"Temps: {time1:.3f}s")
    print_info(f"Cache: {'HIT ⚡' if data1.get('cache_hit') else 'MISS'}")
    print_info(f"Prédiction: {data1['prediction']}")
    
    print_test("Deuxième requête (avec cache)")
    start = time.time()
    response2 = requests.post(f"{API_URL}/predict", json={"text": test_text})
    time2 = time.time() - start
    data2 = response2.json()
    
    print_info(f"Temps: {time2:.3f}s")
    print_info(f"Cache: {'HIT ⚡' if data2.get('cache_hit') else 'MISS'}")
    
    if data2.get('cache_hit'):
        speedup = time1 / time2
        improvement = ((time1 - time2) / time1) * 100
        print_success(f"Accélération: {speedup:.1f}x plus rapide ({improvement:.1f}% d'amélioration)")
    else:
        print_error("Le cache n'a pas fonctionné!")

def test_conversation_titles():
    """Test la sauvegarde des titres de conversation"""
    print_header("TEST DES TITRES DE CONVERSATION")
    
    test_messages = [
        "Comment réinitialiser mon mot de passe ?",
        "Je veux acheter un nouveau clavier mécanique",
        "Création d'un projet de refonte du site web corporate"
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print_test(f"Message {i}: {msg[:40]}...")
        
        session_id = f"test-title-{i}-{int(time.time())}"
        title = msg[:50]
        
        response = requests.post(f"{API_URL}/predict", json={
            "text": msg,
            "session_id": session_id,
            "conversation_title": title
        })
        
        data = response.json()
        print_success(f"Session créée: {session_id}")
        print_info(f"Titre envoyé: {title}")
        print_info(f"Catégorie: {data['prediction']}")
        
        time.sleep(0.3)

def test_statistics():
    """Test l'endpoint des statistiques"""
    print_header("TEST DES STATISTIQUES")
    
    response = requests.get(f"{API_URL}/stats")
    data = response.json()
    
    print_info(f"Total de conversations: {data['conversation_statistics']['total_conversations']}")
    print_info(f"Sessions uniques: {data['conversation_statistics']['unique_sessions']}")
    print_info(f"Cache - Hits: {data['cache_statistics']['hits']}")
    print_info(f"Cache - Misses: {data['cache_statistics']['misses']}")
    print_info(f"Cache - Taux de succès: {data['cache_statistics']['hit_rate']:.1f}%")
    
    print("\n📊 Distribution des catégories:")
    for category, count in data['agent_statistics']['category_distribution'].items():
        bar = "█" * min(count, 50)
        print(f"  {category:25s} {bar} {count}")

def print_summary(results: List[Dict]):
    """Affiche un résumé des résultats"""
    print_header("RÉSUMÉ DES TESTS")
    
    total = len(results)
    success = sum(1 for r in results if r.get('success', False))
    
    print(f"\n{BLUE}Tests réussis: {success}/{total}{RESET}")
    
    if success == total:
        print_success("🎉 TOUS LES TESTS SONT PASSÉS !")
    else:
        print_error(f"⚠️  {total - success} test(s) ont échoué")
    
    # Tableau des résultats
    print("\n📋 Détails des tests de complexité:")
    print(f"{'Test':<40} {'Complexité':>12} {'Modèle':>12} {'Temps':>10}")
    print("-" * 80)
    
    for r in results:
        if 'complexity' in r:
            status = "✅" if r['success'] else "❌"
            print(f"{status} {r['test'][:37]:<37} {r['complexity']:>12.1f} {r['model']:>12} {r['response_time']:>9.2f}s")

def main():
    print(f"{GREEN}")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║              TEST COMPLET - AGENT IA INTELLIGENT                          ║")
    print("║                    CallCenter Classifier                                   ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(RESET)
    
    try:
        # Vérifier que l'API est accessible
        print_info("Vérification de la connexion à l'API...")
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        print_success("API accessible ✓\n")
        
        # Exécuter les tests
        results = test_complexity_and_routing()
        test_cache_performance()
        test_conversation_titles()
        test_statistics()
        
        # Résumé
        print_summary(results)
        
    except requests.exceptions.ConnectionError:
        print_error("❌ Impossible de se connecter à l'API sur http://localhost:8002")
        print_info("Assure-toi que le conteneur ia-agent est démarré:")
        print_info("  docker compose up -d ia-agent")
        return 1
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
