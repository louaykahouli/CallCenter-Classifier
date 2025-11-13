"""
Agent IA utilisant Grok (xAI) pour analyser les tickets et router intelligemment
"""

import os
import json
import logging
from typing import Dict, Optional
import requests

# Import de l'analyseur de complexité
try:
    from .complexity_analyzer import ComplexityAnalyzer
except ImportError:
    from complexity_analyzer import ComplexityAnalyzer

logger = logging.getLogger(__name__)


class GrokAgent:
    """
    Agent IA utilisant Grok pour analyser les tickets et décider du routage
    
    L'agent peut fonctionner en 2 modes:
    1. Mode Complexité seule (rapide, pas d'API call)
    2. Mode Grok enrichi (utilise l'IA pour une analyse plus fine)
    """
    
    # API endpoint Grok
    GROK_API_URL = "https://api.x.ai/v1/chat/completions"
    
    def __init__(self, 
                 api_key: str,
                 use_grok: bool = True,
                 model: str = "grok-beta"):
        """
        Initialise l'agent Grok
        
        Args:
            api_key: Clé API Grok (xAI)
            use_grok: Si False, utilise uniquement l'analyseur de complexité local
            model: Modèle Grok à utiliser (grok-beta par défaut)
        """
        self.api_key = api_key
        self.use_grok = use_grok
        self.model = model
        self.complexity_analyzer = ComplexityAnalyzer()
        
        # Statistiques
        self.stats = {
            'total_requests': 0,
            'grok_calls': 0,
            'local_analysis': 0,
            'errors': 0
        }
        
        logger.info(f"Agent Grok initialisé (mode: {'Grok AI' if use_grok else 'Local uniquement'})")
    
    def analyze_and_route(self, text: str, use_grok_analysis: bool = None) -> Dict:
        """
        Analyse un ticket et décide du routage
        
        Args:
            text: Le texte du ticket à analyser
            use_grok_analysis: Force l'utilisation de Grok (override le paramètre d'instance)
            
        Returns:
            Dict avec:
            - model: "svm" ou "transformer"
            - complexity_score: score 0-100
            - reasoning: explication du choix
            - grok_response: réponse brute de Grok (si utilisé)
        """
        self.stats['total_requests'] += 1
        
        # Décider si on utilise Grok
        should_use_grok = use_grok_analysis if use_grok_analysis is not None else self.use_grok
        
        # Analyse locale de complexité (toujours faire, c'est gratuit et rapide)
        complexity_score, complexity_details = self.complexity_analyzer.analyze(text)
        
        if should_use_grok and self.api_key:
            # Mode enrichi avec Grok
            try:
                result = self._analyze_with_grok(text, complexity_score, complexity_details)
                self.stats['grok_calls'] += 1
                return result
            except Exception as e:
                logger.warning(f"Erreur Grok, fallback sur analyse locale: {e}")
                self.stats['errors'] += 1
                # Fallback sur analyse locale
                return self._analyze_local(text, complexity_score, complexity_details)
        else:
            # Mode local uniquement
            self.stats['local_analysis'] += 1
            return self._analyze_local(text, complexity_score, complexity_details)
    
    def _analyze_local(self, text: str, complexity_score: int, details: Dict) -> Dict:
        """
        Analyse locale basée uniquement sur le score de complexité
        """
        # Règle simple: < 40 = SVM, >= 40 = Transformer
        if complexity_score < 40:
            model = "svm"
            reasoning = f"Texte simple (score {complexity_score}/100) - Routage vers SVM (rapide)"
        else:
            model = "transformer"
            reasoning = f"Texte complexe (score {complexity_score}/100) - Routage vers Transformer (précis)"
        
        return {
            'model': model,
            'complexity_score': complexity_score,
            'complexity_details': details,
            'reasoning': reasoning,
            'method': 'local_analysis',
            'grok_used': False
        }
    
    def _analyze_with_grok(self, text: str, complexity_score: int, details: Dict) -> Dict:
        """
        Analyse enrichie avec Grok AI
        """
        # Créer le prompt pour Grok
        prompt = self._create_grok_prompt(text, complexity_score, details)
        
        # Appeler l'API Grok
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Tu es un expert en classification de tickets de support IT. Tu dois analyser chaque ticket et décider s'il faut utiliser un modèle SVM (rapide mais simple) ou un Transformer (lent mais précis)."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": self.model,
            "stream": False,
            "temperature": 0
        }
        
        logger.info(f"Appel API Grok pour analyse enrichie")
        
        response = requests.post(
            self.GROK_API_URL,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        response.raise_for_status()
        grok_response = response.json()
        
        # Extraire la réponse
        grok_analysis = grok_response['choices'][0]['message']['content']
        
        # Parser la réponse de Grok pour extraire le modèle recommandé
        model = self._parse_grok_response(grok_analysis, complexity_score)
        
        return {
            'model': model,
            'complexity_score': complexity_score,
            'complexity_details': details,
            'reasoning': grok_analysis,
            'method': 'grok_analysis',
            'grok_used': True,
            'grok_raw_response': grok_response
        }
    
    def _create_grok_prompt(self, text: str, complexity_score: int, details: Dict) -> str:
        """
        Crée un prompt optimisé pour Grok
        """
        prompt = f"""Analyse ce ticket de support IT et recommande le modèle à utiliser:

TICKET: "{text}"

ANALYSE DE COMPLEXITÉ:
- Score global: {complexity_score}/100
- Longueur: {details.get('word_count', 0)} mots
- Score vocabulaire: {details.get('vocabulary_score', 0)}/100
- Score structure: {details.get('structure_score', 0)}/100
- Score ambiguïté: {details.get('ambiguity_score', 0)}/100

MODÈLES DISPONIBLES:
1. SVM + TF-IDF: Très rapide (~10ms), bonne précision pour textes simples
2. Transformer (DistilBERT): Plus lent (~100ms), excellente précision pour textes complexes

CRITÈRES DE DÉCISION:
- Utilise SVM pour: tickets courts, simples, mots-clés clairs ("souris cassée", "imprimante bloquée")
- Utilise Transformer pour: tickets longs, contexte complexe, phrases multiples, ambiguïté

RÉPONDS UNIQUEMENT:
Modèle recommandé: [SVM ou TRANSFORMER]
Raison: [explication en 1 phrase]
Confiance: [haute/moyenne/faible]"""
        
        return prompt
    
    def _parse_grok_response(self, grok_text: str, fallback_complexity: int) -> str:
        """
        Parse la réponse de Grok pour extraire le modèle
        
        Args:
            grok_text: Texte de la réponse Grok
            fallback_complexity: Score de complexité pour fallback
            
        Returns:
            "svm" ou "transformer"
        """
        grok_lower = grok_text.lower()
        
        # Chercher explicitement "svm" ou "transformer" dans la réponse
        if "svm" in grok_lower and "transformer" not in grok_lower:
            return "svm"
        elif "transformer" in grok_lower and "svm" not in grok_lower:
            return "transformer"
        else:
            # Fallback sur le score de complexité
            logger.warning(f"Réponse Grok ambiguë, fallback sur score de complexité")
            return "svm" if fallback_complexity < 40 else "transformer"
    
    def get_stats(self) -> Dict:
        """
        Retourne les statistiques d'utilisation
        """
        total = self.stats['total_requests']
        if total == 0:
            return {
                'total_requests': 0,
                'message': 'Aucune requête traitée'
            }
        
        return {
            'total_requests': total,
            'grok_calls': self.stats['grok_calls'],
            'local_analysis': self.stats['local_analysis'],
            'errors': self.stats['errors'],
            'grok_usage_rate': round(self.stats['grok_calls'] / total * 100, 2),
            'error_rate': round(self.stats['errors'] / total * 100, 2)
        }


if __name__ == "__main__":
    # Tests
    import os
    
    # Configuration
    GROK_API_KEY = "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"
    
    # Créer l'agent
    agent = GrokAgent(api_key=GROK_API_KEY, use_grok=False)  # Commencer en mode local
    
    test_cases = [
        "Souris cassée",
        "Mon ordinateur ne démarre plus après la mise à jour Windows",
        "Plusieurs utilisateurs signalent des problèmes d'accès intermittents au serveur partagé depuis l'installation du nouveau pare-feu. Pouvez-vous vérifier si cela est lié à la configuration VPN ?",
    ]
    
    print("\n" + "="*80)
    print("🤖 TEST DE L'AGENT GROK IA")
    print("="*80)
    
    print("\n>>> MODE 1: ANALYSE LOCALE (sans Grok, gratuit)")
    print("-"*80)
    
    for text in test_cases:
        result = agent.analyze_and_route(text)
        print(f"\n📝 Ticket: {text[:60]}...")
        print(f"🎯 Modèle: {result['model'].upper()}")
        print(f"📊 Complexité: {result['complexity_score']}/100")
        print(f"💡 Raisonnement: {result['reasoning']}")
    
    # Test avec Grok (si vous voulez)
    print("\n\n>>> MODE 2: ANALYSE AVEC GROK (IA enrichie)")
    print("-"*80)
    print("⚠️  Mode Grok désactivé pour éviter les coûts API")
    print("Pour l'activer: agent = GrokAgent(api_key=GROK_API_KEY, use_grok=True)")
    
    # Stats
    print("\n\n" + "="*80)
    print("📊 STATISTIQUES")
    print("="*80)
    stats = agent.get_stats()
    print(json.dumps(stats, indent=2))
