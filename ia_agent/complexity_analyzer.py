"""
Analyseur de complexité de texte pour l'agent IA
Calcule un score de complexité de 0 à 100 basé sur plusieurs critères
"""

import re
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """
    Analyse la complexité d'un texte et retourne un score de 0-100
    
    Critères d'analyse:
    - Longueur (nombre de mots, caractères)
    - Vocabulaire (mots techniques, rares)
    - Structure (ponctuation, phrases complexes)
    - Ambiguïté (questions, négations, conditions)
    """
    
    # Mots techniques du domaine IT
    TECHNICAL_KEYWORDS = {
        # Hardware
        'ordinateur', 'écran', 'clavier', 'souris', 'imprimante', 'serveur',
        'disque', 'ram', 'processeur', 'carte', 'câble', 'périphérique',
        
        # Software
        'logiciel', 'application', 'système', 'programme', 'base de données',
        'mise à jour', 'installation', 'configuration', 'paramètre',
        
        # Network
        'réseau', 'connexion', 'wifi', 'internet', 'vpn', 'firewall',
        'proxy', 'dns', 'routeur', 'switch', 'port',
        
        # Access/Security
        'mot de passe', 'accès', 'droits', 'permission', 'compte',
        'authentification', 'sécurité', 'token', 'certificat',
        
        # HR/Admin
        'congé', 'absence', 'salaire', 'formation', 'contrat',
        'badge', 'horaire', 'pointage', 'rh',
        
        # General IT
        'bug', 'erreur', 'problème', 'incident', 'ticket',
        'support', 'maintenance', 'dépannage'
    }
    
    # Mots de structure complexe
    COMPLEX_STRUCTURE_WORDS = {
        'cependant', 'néanmoins', 'toutefois', 'en revanche', 'malgré',
        'bien que', 'quoique', 'à condition que', 'pourvu que', 'afin que',
        'de sorte que', 'ainsi que', 'tandis que', 'alors que', 'dès lors que'
    }
    
    def __init__(self):
        """Initialise l'analyseur de complexité"""
        self.technical_keywords = self.TECHNICAL_KEYWORDS
        self.complex_structure_words = self.COMPLEX_STRUCTURE_WORDS
        
    def analyze(self, text: str) -> Tuple[int, Dict[str, float]]:
        """
        Analyse un texte et retourne un score de complexité
        
        Args:
            text: Le texte à analyser
            
        Returns:
            Tuple (score_global, détails_par_critère)
            - score_global: int de 0 à 100
            - détails: dict avec les sous-scores
        """
        if not text or not text.strip():
            return 0, {"error": "Texte vide"}
        
        text_clean = text.lower().strip()
        
        # Calculer chaque critère
        length_score = self._analyze_length(text_clean)
        vocab_score = self._analyze_vocabulary(text_clean)
        structure_score = self._analyze_structure(text_clean)
        ambiguity_score = self._analyze_ambiguity(text_clean)
        
        # Pondération des critères
        weights = {
            'length': 0.25,
            'vocabulary': 0.35,
            'structure': 0.25,
            'ambiguity': 0.15
        }
        
        # Score global pondéré
        global_score = (
            length_score * weights['length'] +
            vocab_score * weights['vocabulary'] +
            structure_score * weights['structure'] +
            ambiguity_score * weights['ambiguity']
        )
        
        # Arrondir et limiter à 0-100
        global_score = int(round(min(100, max(0, global_score))))
        
        details = {
            'length_score': round(length_score, 2),
            'vocabulary_score': round(vocab_score, 2),
            'structure_score': round(structure_score, 2),
            'ambiguity_score': round(ambiguity_score, 2),
            'weights': weights,
            'text_length': len(text_clean),
            'word_count': len(text_clean.split())
        }
        
        logger.info(f"Complexité analysée: {global_score}/100 - {details}")
        
        return global_score, details
    
    def _analyze_length(self, text: str) -> float:
        """
        Analyse la longueur du texte
        
        Règles:
        - Très court (< 5 mots): 10 points
        - Court (5-15 mots): 20-40 points
        - Moyen (15-30 mots): 40-60 points
        - Long (30-50 mots): 60-80 points
        - Très long (> 50 mots): 80-100 points
        """
        words = text.split()
        word_count = len(words)
        
        if word_count < 5:
            return 10
        elif word_count < 15:
            # Progression linéaire de 20 à 40
            return 20 + (word_count - 5) * 2
        elif word_count < 30:
            # Progression linéaire de 40 à 60
            return 40 + (word_count - 15) * 1.33
        elif word_count < 50:
            # Progression linéaire de 60 à 80
            return 60 + (word_count - 30) * 1
        else:
            # Au-delà de 50 mots, complexité max
            return min(100, 80 + (word_count - 50) * 0.5)
    
    def _analyze_vocabulary(self, text: str) -> float:
        """
        Analyse le vocabulaire (mots techniques, rares)
        
        Règles:
        - Pas de mots techniques: 20 points
        - 1-2 mots techniques: 40 points
        - 3-4 mots techniques: 60 points
        - 5+ mots techniques: 80-100 points
        """
        words = text.split()
        
        # Compter les mots techniques
        technical_count = sum(
            1 for word in words 
            if any(keyword in word for keyword in self.technical_keywords)
        )
        
        # Calculer le ratio de mots techniques
        tech_ratio = technical_count / len(words) if words else 0
        
        # Score basé sur le nombre et la densité
        if technical_count == 0:
            base_score = 20
        elif technical_count <= 2:
            base_score = 40
        elif technical_count <= 4:
            base_score = 60
        else:
            base_score = 80 + min(20, technical_count * 2)
        
        # Bonus pour haute densité de mots techniques
        if tech_ratio > 0.3:
            base_score += 10
        
        return min(100, base_score)
    
    def _analyze_structure(self, text: str) -> float:
        """
        Analyse la structure (ponctuation, phrases complexes)
        
        Règles:
        - Phrase simple: 20 points
        - Avec ponctuation: 40 points
        - Multiples phrases: 60 points
        - Structure complexe: 80-100 points
        """
        # Compter les phrases (points, points d'exclamation, questions)
        sentence_count = len(re.findall(r'[.!?]+', text))
        
        # Compter la ponctuation complexe (virgules, deux-points, etc.)
        complex_punct = len(re.findall(r'[,;:()«»"]', text))
        
        # Détecter les mots de structure complexe
        complex_words = sum(
            1 for word in self.complex_structure_words
            if word in text
        )
        
        # Score de base selon le nombre de phrases
        if sentence_count <= 1:
            base_score = 20
        elif sentence_count == 2:
            base_score = 40
        elif sentence_count == 3:
            base_score = 60
        else:
            base_score = 70 + min(30, sentence_count * 5)
        
        # Bonus pour ponctuation complexe
        punct_bonus = min(20, complex_punct * 3)
        
        # Bonus pour mots de structure complexe
        structure_bonus = min(15, complex_words * 10)
        
        return min(100, base_score + punct_bonus + structure_bonus)
    
    def _analyze_ambiguity(self, text: str) -> float:
        """
        Analyse l'ambiguïté (questions, négations, conditions)
        
        Règles:
        - Affirmation simple: 10 points
        - Avec négation: 30 points
        - Avec question: 50 points
        - Avec condition: 70 points
        - Multiple ambiguïtés: 90-100 points
        """
        score = 10  # Score de base
        
        # Questions
        if '?' in text or any(q in text for q in ['comment', 'pourquoi', 'quoi', 'où', 'quand', 'quel']):
            score += 40
        
        # Négations
        negations = len(re.findall(r'\b(ne|n\'|pas|jamais|rien|aucun|personne)\b', text))
        score += min(30, negations * 15)
        
        # Conditions
        conditions = len(re.findall(r'\b(si|sauf|excepté|à condition|en cas)\b', text))
        score += min(30, conditions * 20)
        
        # Incertitudes
        uncertainties = len(re.findall(r'\b(peut-être|probablement|possiblement|semble|paraît)\b', text))
        score += min(20, uncertainties * 15)
        
        return min(100, score)
    
    def get_complexity_level(self, score: int) -> str:
        """
        Retourne le niveau de complexité en texte
        
        Args:
            score: Score de complexité (0-100)
            
        Returns:
            Niveau: "simple", "moyen", ou "complexe"
        """
        if score < 30:
            return "simple"
        elif score < 60:
            return "moyen"
        else:
            return "complexe"
    
    def get_recommended_model(self, score: int) -> str:
        """
        Recommande un modèle selon le score de complexité
        
        Args:
            score: Score de complexité (0-100)
            
        Returns:
            Nom du modèle recommandé
        """
        if score < 30:
            return "distilbert"  # Léger et rapide
        elif score < 60:
            return "bert-base"   # Équilibre performance/vitesse
        else:
            return "gpt-llm"     # Maximum de performance


if __name__ == "__main__":
    # Tests
    analyzer = ComplexityAnalyzer()
    
    test_cases = [
        "Souris cassée",
        "Mon ordinateur ne démarre plus",
        "Je ne peux pas accéder au serveur partagé depuis ce matin",
        "Plusieurs utilisateurs du département signalent des problèmes d'accès intermittents au serveur partagé depuis l'installation du nouveau pare-feu, et je me demande si cela pourrait être lié à la configuration du VPN",
    ]
    
    print("\n=== Tests de l'analyseur de complexité ===\n")
    for text in test_cases:
        score, details = analyzer.analyze(text)
        level = analyzer.get_complexity_level(score)
        model = analyzer.get_recommended_model(score)
        
        print(f"Texte: {text[:60]}...")
        print(f"Score: {score}/100 | Niveau: {level} | Modèle: {model}")
        print(f"Détails: {details}\n")
