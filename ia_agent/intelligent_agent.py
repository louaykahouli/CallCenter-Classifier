"""
Agent IA Intelligent pour la classification de tickets
Route vers le modèle approprié selon la complexité du texte
"""

import logging
from typing import Dict, Tuple

# Import relatif ou absolu selon le contexte
try:
    from .complexity_analyzer import ComplexityAnalyzer
except ImportError:
    from complexity_analyzer import ComplexityAnalyzer

logger = logging.getLogger(__name__)


class IntelligentAgent:
    """
    Agent IA qui analyse la complexité d'un texte et route vers le modèle approprié
    
    Stratégie de routage:
    - Complexité 0-30: DistilBERT (léger, rapide)
    - Complexité 31-60: BERT-base (équilibré)
    - Complexité 61-100: GPT/LLM (puissant, lent)
    """
    
    # Configuration des seuils
    THRESHOLDS = {
        'simple': 30,    # Score < 30 = simple
        'medium': 60     # Score < 60 = moyen, >= 60 = complexe
    }
    
    # Mapping des modèles
    MODEL_MAPPING = {
        'simple': {
            'name': 'distilbert',
            'description': 'DistilBERT - Léger et rapide pour requêtes simples',
            'speed': 'très rapide',
            'accuracy': 'bonne'
        },
        'medium': {
            'name': 'bert-base',
            'description': 'BERT-base - Équilibre performance/vitesse',
            'speed': 'moyen',
            'accuracy': 'très bonne'
        },
        'complex': {
            'name': 'gpt-llm',
            'description': 'GPT/LLM - Maximum de performance pour textes complexes',
            'speed': 'lent',
            'accuracy': 'excellente'
        }
    }
    
    def __init__(self, use_distilbert_for_all: bool = False):
        """
        Initialise l'agent intelligent
        
        Args:
            use_distilbert_for_all: Si True, utilise toujours DistilBERT (mode par défaut actuel)
        """
        self.analyzer = ComplexityAnalyzer()
        self.use_distilbert_for_all = use_distilbert_for_all
        self.stats = {
            'total_requests': 0,
            'by_model': {
                'distilbert': 0,
                'bert-base': 0,
                'gpt-llm': 0
            },
            'by_complexity': {
                'simple': 0,
                'medium': 0,
                'complex': 0
            }
        }
        
        logger.info(f"Agent Intelligent initialisé (mode: {'DistilBERT only' if use_distilbert_for_all else 'Multi-modèle'})")
    
    def route(self, text: str) -> Dict:
        """
        Analyse un texte et décide quel modèle utiliser
        
        Args:
            text: Le texte à analyser
            
        Returns:
            Dict avec:
            - model: nom du modèle recommandé
            - complexity_score: score de complexité
            - complexity_level: niveau (simple/moyen/complexe)
            - details: détails de l'analyse
            - reasoning: explication du choix
        """
        # Analyser la complexité
        complexity_score, analysis_details = self.analyzer.analyze(text)
        
        # Déterminer le niveau de complexité
        if complexity_score < self.THRESHOLDS['simple']:
            complexity_level = 'simple'
        elif complexity_score < self.THRESHOLDS['medium']:
            complexity_level = 'medium'
        else:
            complexity_level = 'complex'
        
        # Choisir le modèle
        if self.use_distilbert_for_all:
            # Mode par défaut: toujours DistilBERT
            selected_model = 'distilbert'
            reasoning = "Mode DistilBERT-only activé (configuration par défaut)"
        else:
            # Mode intelligent: router selon la complexité
            selected_model = self.MODEL_MAPPING[complexity_level]['name']
            reasoning = self._generate_reasoning(complexity_score, complexity_level, analysis_details)
        
        # Mettre à jour les statistiques
        self._update_stats(selected_model, complexity_level)
        
        result = {
            'model': selected_model,
            'complexity_score': complexity_score,
            'complexity_level': complexity_level,
            'details': analysis_details,
            'reasoning': reasoning,
            'model_info': self.MODEL_MAPPING[complexity_level]
        }
        
        logger.info(f"Routage: {text[:50]}... → {selected_model} (complexité: {complexity_score})")
        
        return result
    
    def _generate_reasoning(self, score: int, level: str, details: Dict) -> str:
        """
        Génère une explication pour le choix du modèle
        
        Args:
            score: Score de complexité
            level: Niveau de complexité
            details: Détails de l'analyse
            
        Returns:
            Explication textuelle
        """
        word_count = details.get('word_count', 0)
        vocab_score = details.get('vocabulary_score', 0)
        structure_score = details.get('structure_score', 0)
        
        reasons = []
        
        # Raison principale basée sur le score
        if level == 'simple':
            reasons.append(f"Texte simple (score {score}/100)")
            reasons.append("Requête courte et directe")
        elif level == 'medium':
            reasons.append(f"Texte de complexité moyenne (score {score}/100)")
            reasons.append(f"{word_count} mots avec vocabulaire modéré")
        else:
            reasons.append(f"Texte complexe (score {score}/100)")
            reasons.append("Requête longue avec contexte détaillé")
        
        # Détails additionnels
        if vocab_score > 70:
            reasons.append("Vocabulaire technique important")
        
        if structure_score > 70:
            reasons.append("Structure grammaticale complexe")
        
        # Conclusion
        model_name = self.MODEL_MAPPING[level]['name']
        reasons.append(f"→ Utilisation de {model_name}")
        
        return " | ".join(reasons)
    
    def _update_stats(self, model: str, level: str):
        """Met à jour les statistiques d'utilisation"""
        self.stats['total_requests'] += 1
        self.stats['by_model'][model] += 1
        self.stats['by_complexity'][level] += 1
    
    def get_stats(self) -> Dict:
        """
        Retourne les statistiques d'utilisation
        
        Returns:
            Dict avec les stats
        """
        total = self.stats['total_requests']
        
        if total == 0:
            return {
                'total_requests': 0,
                'message': 'Aucune requête traitée'
            }
        
        return {
            'total_requests': total,
            'by_model': {
                model: {
                    'count': count,
                    'percentage': round(count / total * 100, 2)
                }
                for model, count in self.stats['by_model'].items()
            },
            'by_complexity': {
                level: {
                    'count': count,
                    'percentage': round(count / total * 100, 2)
                }
                for level, count in self.stats['by_complexity'].items()
            }
        }
    
    def adjust_thresholds(self, simple_threshold: int = None, medium_threshold: int = None):
        """
        Ajuste les seuils de complexité
        
        Args:
            simple_threshold: Nouveau seuil pour simple (défaut: 30)
            medium_threshold: Nouveau seuil pour moyen (défaut: 60)
        """
        if simple_threshold is not None:
            self.THRESHOLDS['simple'] = simple_threshold
            logger.info(f"Seuil 'simple' ajusté à {simple_threshold}")
        
        if medium_threshold is not None:
            self.THRESHOLDS['medium'] = medium_threshold
            logger.info(f"Seuil 'medium' ajusté à {medium_threshold}")


if __name__ == "__main__":
    # Tests
    agent = IntelligentAgent(use_distilbert_for_all=False)
    
    test_cases = [
        "Souris cassée",
        "Mon ordinateur ne démarre plus après la mise à jour",
        "Je ne peux pas accéder au serveur partagé depuis ce matin",
        "Plusieurs utilisateurs du département signalent des problèmes d'accès intermittents au serveur partagé depuis l'installation du nouveau pare-feu, et je me demande si cela pourrait être lié à la configuration du VPN ou aux paramètres de sécurité",
    ]
    
    print("\n=== Tests de l'Agent IA Intelligent ===\n")
    
    for text in test_cases:
        result = agent.route(text)
        
        print(f"\n{'='*80}")
        print(f"Texte: {text}")
        print(f"{'='*80}")
        print(f"Modèle sélectionné: {result['model'].upper()}")
        print(f"Complexité: {result['complexity_score']}/100 ({result['complexity_level']})")
        print(f"Raisonnement: {result['reasoning']}")
        print(f"Info modèle: {result['model_info']['description']}")
        print(f"  - Vitesse: {result['model_info']['speed']}")
        print(f"  - Précision: {result['model_info']['accuracy']}")
    
    print(f"\n\n{'='*80}")
    print("STATISTIQUES D'UTILISATION")
    print(f"{'='*80}")
    stats = agent.get_stats()
    print(f"\nTotal de requêtes: {stats['total_requests']}")
    
    print("\n📊 Répartition par modèle:")
    for model, data in stats['by_model'].items():
        print(f"  - {model}: {data['count']} ({data['percentage']}%)")
    
    print("\n📈 Répartition par complexité:")
    for level, data in stats['by_complexity'].items():
        print(f"  - {level}: {data['count']} ({data['percentage']}%)")
