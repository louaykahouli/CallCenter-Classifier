# 🤖 Agent IA - Module de Routage Intelligent

Module pour analyser la complexité des tickets et router intelligemment entre différents modèles de classification.

## 📁 Structure

```
ia_agent/
├── __init__.py                    # Module principal
├── complexity_analyzer.py         # Analyse la complexité des textes (0-100)
├── intelligent_agent.py           # Router multi-modèles (local)
├── grok_agent.py                  # Agent avec Grok AI (xAI)
├── test_grok_api.py              # Tests de l'API Grok
└── README.md                      # Cette documentation
```

## 🎯 Composants

### 1. ComplexityAnalyzer
Analyse la complexité d'un texte selon plusieurs critères :
- **Longueur** : nombre de mots/caractères
- **Vocabulaire** : mots techniques, termes IT
- **Structure** : ponctuation, phrases complexes
- **Ambiguïté** : questions, négations, conditions

**Sortie** : Score de 0 à 100

### 2. IntelligentAgent
Router local sans API externe :
- Simple (0-30) → Modèle léger (SVM)
- Moyen (31-60) → Modèle équilibré (BERT-base)
- Complexe (61-100) → Modèle puissant (Transformer)

### 3. GrokAgent
Agent enrichi avec Grok AI (xAI) :
- Utilise l'IA pour une analyse contextuelle
- Peut fonctionner en mode local (fallback)
- Décide entre SVM (rapide) et Transformer (précis)

## 🚀 Utilisation

### Mode 1 : Analyse de Complexité Seule
```python
from ia_agent import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()
score, details = analyzer.analyze("Mon ordinateur ne démarre plus")

print(f"Score: {score}/100")
print(f"Détails: {details}")
```

### Mode 2 : Router Intelligent (Local)
```python
from ia_agent import IntelligentAgent

agent = IntelligentAgent(use_distilbert_for_all=False)
result = agent.route("Plusieurs utilisateurs signalent des problèmes...")

print(f"Modèle: {result['model']}")
print(f"Complexité: {result['complexity_score']}/100")
print(f"Raison: {result['reasoning']}")
```

### Mode 3 : Agent Grok (IA enrichie)
```python
from ia_agent import GrokAgent

GROK_API_KEY = "gsk_..."  # Votre clé API

# Mode local (gratuit)
agent = GrokAgent(api_key=GROK_API_KEY, use_grok=False)
result = agent.analyze_and_route("Souris cassée")

# Mode Grok (payant, plus précis)
agent = GrokAgent(api_key=GROK_API_KEY, use_grok=True)
result = agent.analyze_and_route("Problème complexe...")
```

## 🧪 Tests

```bash
# Test de l'analyseur de complexité
cd ia_agent
python3 complexity_analyzer.py

# Test de l'agent intelligent
python3 intelligent_agent.py

# Test de l'agent Grok (local)
python3 grok_agent.py

# Test de l'API Grok réelle
python3 test_grok_api.py
```

## 📊 Scores de Complexité

| Score | Niveau | Modèle Recommandé | Caractéristiques |
|-------|--------|-------------------|------------------|
| 0-30 | Simple | SVM | Courts, mots-clés clairs |
| 31-60 | Moyen | BERT-base | Contexte modéré |
| 61-100 | Complexe | Transformer | Long, technique, ambigu |

## 🔑 Configuration

### Clé API Grok
Obtenir sur : https://console.x.ai/

Variables d'environnement (optionnel) :
```bash
export GROK_API_KEY="gsk_..."
```

Ou directement dans le code :
```python
agent = GrokAgent(api_key="gsk_...")
```

## 📈 Statistiques

Tous les agents trackent leurs statistiques :
```python
stats = agent.get_stats()
print(stats)
# {
#   'total_requests': 10,
#   'grok_calls': 3,
#   'local_analysis': 7,
#   'errors': 0
# }
```

## 🎓 Exemples de Routage

**Exemple 1 : Ticket Simple → SVM**
```
Input: "Souris cassée"
Complexité: 26/100
Modèle: SVM
Raison: Texte court, mot-clé clair
```

**Exemple 2 : Ticket Moyen → BERT**
```
Input: "Mon ordinateur ne démarre plus après la mise à jour"
Complexité: 31/100
Modèle: BERT-base
Raison: Contexte simple mais phrase complète
```

**Exemple 3 : Ticket Complexe → Transformer**
```
Input: "Plusieurs utilisateurs signalent des problèmes d'accès intermittents..."
Complexité: 66/100
Modèle: Transformer
Raison: Contexte riche, vocabulaire technique, phrase longue
```

## 🔧 Configuration Avancée

### Ajuster les Seuils
```python
agent = IntelligentAgent()
agent.adjust_thresholds(simple_threshold=35, medium_threshold=65)
```

### Mode Debug
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 TODO

- [ ] Entraîner le modèle SVM
- [x] Créer l'analyseur de complexité
- [x] Créer l'agent intelligent
- [x] Intégrer Grok API
- [ ] Ajouter endpoint API FastAPI
- [ ] Tests de performance SVM vs Transformer

## 🤝 Contribution

Développé pour le projet CallCenter-Classifier
