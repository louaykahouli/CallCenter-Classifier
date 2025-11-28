# 🎯 Guide des Fonctionnalités - Agent IA Intelligent

## 📦 Système de Stockage des Conversations

### 1. Base de Données SQLite
L'agent IA stocke **toutes les conversations** dans une base de données SQLite persistante :

**Localisation** : `/app/data/conversations.db` (dans le conteneur Docker)
**Mappé vers** : `./ia_agent/data/conversations.db` (sur votre machine)

**Structure de la table `conversations`** :
```sql
- id: ID unique auto-incrémenté
- session_id: ID de session utilisateur
- timestamp: Date et heure de la conversation
- input_text: Texte envoyé par l'utilisateur
- prediction: Catégorie prédite
- model_used: Modèle utilisé (tfidf/transformer)
- complexity_score: Score de complexité (0-100)
- complexity_level: Niveau (simple/medium/complex)
- response_time: Temps de réponse en secondes
- generated_response: Réponse générée par Grok
- probabilities: Probabilités par catégorie (JSON)
```

### 2. Système de Cache en Mémoire

**Performance** :
- ⚡ **98% plus rapide** pour les requêtes répétées
- Sans cache : ~4 secondes
- Avec cache : ~0.09 secondes

**Configuration** :
- TTL par défaut : 3600 secondes (1 heure)
- Stockage : En mémoire (RAM)
- Clé : Hash MD5 du texte + modèle

---

## 🚀 Fonctionnalités Frontend

### 1. Nommage Automatique des Conversations
✅ Chaque conversation prend automatiquement le nom de la **première catégorie prédite**

**Icônes par catégorie** :
- 🖥️ Hardware
- 🔐 Access
- 🛒 Purchase
- 👥 HR Support
- 📁 Internal Project
- ⚙️ Administrative rights
- 💾 Storage
- 📝 Miscellaneous

**Exemple** : "🖥️ Hardware" pour un problème d'imprimante

### 2. Badge de Cache
⚡ Un badge **"Depuis le cache"** s'affiche quand la réponse provient du cache

### 3. Session Tracking
Chaque conversation a un `session_id` unique :
- Format : `session-{timestamp}`
- Persisté dans la base de données
- Permet de récupérer l'historique complet

### 4. Panneau de Statistiques
Cliquez sur **"Statistiques"** en haut à droite pour voir :

**Cache Performance** :
- Entrées totales/actives
- Nombre de cache hits
- Utilisation mémoire
- Bouton "Vider le cache"

**Conversations** :
- Total des conversations (7 derniers jours)
- Sessions uniques
- Complexité moyenne

**Distribution des Modèles** :
- Nombre d'utilisations TF-IDF vs Transformer
- Graphique visuel

**Top Catégories** :
- Les 5 catégories les plus fréquentes

**Temps de Réponse** :
- Moyen / Min / Max

**Configuration** :
- Seuil de complexité
- État du cache

---

## 🔌 API Endpoints

### Nouveaux Endpoints

#### 1. Récupérer l'historique d'une session
```bash
GET /history/{session_id}?limit=50
```

**Exemple** :
```bash
curl http://localhost:8002/history/session-1234567890
```

**Réponse** :
```json
{
  "session_id": "session-1234567890",
  "count": 5,
  "conversations": [
    {
      "id": 1,
      "timestamp": "2025-11-27 10:30:00",
      "input_text": "Mon imprimante ne fonctionne pas",
      "prediction": "Hardware",
      "model_used": "tfidf",
      "complexity_score": 30,
      "complexity_level": "medium",
      "probabilities": {...},
      "response_time": 3.45,
      "generated_response": "..."
    }
  ]
}
```

#### 2. Statistiques du cache
```bash
GET /cache/stats
```

**Réponse** :
```json
{
  "total_entries": 10,
  "active_entries": 8,
  "expired_entries": 2,
  "total_hits": 15,
  "cache_ttl": 3600,
  "memory_usage_mb": 0.5
}
```

#### 3. Vider le cache
```bash
POST /cache/clear
```

#### 4. Nettoyer les entrées expirées
```bash
POST /cache/cleanup
```

#### 5. Statistiques enrichies
```bash
GET /stats
```

**Inclut maintenant** :
- `agent_statistics` : Stats de l'agent
- `cache_statistics` : Stats du cache
- `conversation_statistics` : Stats des conversations
- `configuration` : Configuration actuelle

---

## 📊 Utilisation

### Exemple 1 : Créer une conversation avec session_id
```bash
curl -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mon imprimante ne fonctionne pas",
    "session_id": "user-session-123"
  }'
```

**Réponse** :
```json
{
  "prediction": "Hardware",
  "cache_hit": false,
  "session_id": "user-session-123",
  ...
}
```

### Exemple 2 : Même requête (cache)
```bash
# Même requête - réponse instantanée depuis le cache
curl -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mon imprimante ne fonctionne pas",
    "session_id": "user-session-123"
  }'
```

**Réponse** :
```json
{
  "cache_hit": true,  ⚡ Depuis le cache !
  ...
}
```

### Exemple 3 : Récupérer l'historique
```bash
curl http://localhost:8002/history/user-session-123
```

---

## 🎨 Frontend - Démonstration

### 1. Ouvrir le frontend
```bash
http://localhost:3000
```

### 2. Envoyer un message
Exemple : "Mon ordinateur ne démarre plus"

**Résultat** :
- 🖥️ Le nom de la conversation devient **"🖥️ Hardware"**
- 💬 La réponse s'affiche avec tous les détails
- 💾 La conversation est sauvegardée en base de données

### 3. Renvoyer le même message
**Résultat** :
- ⚡ Badge **"Depuis le cache"** affiché
- ⚡ Réponse **instantanée** (0.09s au lieu de 4s)

### 4. Voir les statistiques
- Cliquer sur **"Statistiques"** en haut à droite
- Voir le cache, les conversations, la distribution

### 5. Vider le cache
- Dans le panneau des statistiques
- Cliquer sur **"Vider le cache"**

---

## 🗄️ Persistance des Données

### Données Persistées
✅ **Conversations** : Stockées dans `ia_agent/data/conversations.db`
✅ **Volume Docker** : Mappé dans docker-compose.yml
✅ **Survit aux redémarrages** : Oui

### Données en Mémoire
⚠️ **Cache** : Perdu au redémarrage du conteneur
⚠️ **Stats du cache** : Remises à zéro

### Nettoyage Automatique
La base de données peut être nettoyée avec :
```python
conversation_store.cleanup_old_conversations(days=30)
```

---

## 📈 Métriques de Performance

### Tests Réels

**Sans Cache** :
- Temps : 4.113 secondes
- Appel aux modèles : Oui
- Appel à Grok : Oui

**Avec Cache** :
- Temps : 0.090 secondes
- Appel aux modèles : Non
- Appel à Grok : Non
- **Amélioration : 98% plus rapide (45x)**

---

## 🧪 Tests Automatisés

Lancer les tests du cache et des conversations :
```bash
cd /home/louay/Desktop/Project/CallCenter
source ia_agent/tests/.venv/bin/activate
pytest ia_agent/tests/test_cache_and_conversations.py -v
```

**Tests inclus** :
- ✅ Cache améliore les temps de réponse
- ✅ Statistiques du cache
- ✅ Vidage du cache
- ✅ Génération de session_id
- ✅ Historique des sessions
- ✅ Statistiques enrichies
- ✅ Workflow complet

---

## 🔧 Configuration

### Variables d'Environnement

```yaml
# docker-compose.yml
environment:
  - CACHE_ENABLED=true        # Activer/désactiver le cache
  - CACHE_TTL=3600            # Durée de vie du cache (secondes)
  - GROK_API_KEY=...          # Clé API Grok
  - USE_GROK=true             # Utiliser Grok pour les réponses
```

### Modifier le TTL du Cache
```bash
# Dans docker-compose.yml
CACHE_TTL=7200  # 2 heures au lieu de 1
```

---

## 🎯 Résumé

**Fonctionnalités Ajoutées** :
1. ✅ Cache en mémoire (98% plus rapide)
2. ✅ Base de données SQLite pour les conversations
3. ✅ Session tracking avec session_id
4. ✅ Historique complet par session
5. ✅ Statistiques enrichies (cache + conversations)
6. ✅ Nommage automatique des conversations
7. ✅ Icônes par catégorie
8. ✅ Badge de cache dans le frontend
9. ✅ Panneau de statistiques interactif
10. ✅ API endpoints pour la gestion

**Impact** :
- 🚀 Performance : 45x plus rapide avec cache
- 💾 Persistance : Toutes les conversations sauvegardées
- 📊 Monitoring : Stats complètes en temps réel
- 🎨 UX : Interface améliorée avec feedback visuel
