# 🐳 Docker - CallCenter Classifier

Guide complet pour utiliser Docker avec le projet CallCenter.

---

## 🚀 Démarrage Rapide

### **Option 1 : Docker Compose (Recommandé)**

Lance l'API + MLflow en un seul commande :

```bash
docker-compose up -d
```

**Accès :**
- 🤖 API : http://localhost:8000
- 📚 API Docs : http://localhost:8000/docs
- 📊 MLflow : http://localhost:5000

### **Option 2 : Docker seul**

```bash
# Construire l'image
docker build -t callcenter-classifier .

# Lancer l'API
docker run -d -p 8000:8000 --name callcenter-api callcenter-classifier
```

---

## 📦 Images Docker

### **Taille de l'image**
- Image de base : ~1.5 GB (Python + PyTorch CPU)
- Avec dépendances : ~2 GB
- Le modèle HuggingFace (541 MB) est téléchargé au premier lancement

### **Optimisations incluses**
- ✅ PyTorch CPU (pas de CUDA, plus léger)
- ✅ Multi-stage build pour réduire la taille
- ✅ Cache pip désactivé
- ✅ Healthchecks automatiques

---

## 🔧 Commandes Utiles

### **Gestion des conteneurs**

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Voir les logs
docker-compose logs -f

# Logs de l'API seulement
docker-compose logs -f api

# Redémarrer
docker-compose restart

# Reconstruire après modifications
docker-compose up -d --build
```

### **État des conteneurs**

```bash
# Voir les conteneurs actifs
docker-compose ps

# Statistiques en temps réel
docker stats

# Inspecter un conteneur
docker-compose exec api bash
```

---

## 🧪 Tests avec Docker

```bash
# Tester l'API
curl http://localhost:8000/health

# Classification
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Mon ordinateur ne démarre plus"}'
```

---

## 📂 Volumes Persistants

Les données suivantes sont conservées entre les redémarrages :

- `./Transformer/mlruns` → Historique MLflow
- `./Transformer/data` → Données du projet

```bash
# Voir les volumes
docker volume ls

# Nettoyer les volumes non utilisés
docker volume prune
```

---

## 🛠️ Configuration

### **Variables d'environnement**

Modifiez `docker-compose.yml` :

```yaml
environment:
  - HF_MODEL_NAME=Kahouli/callcenter-ticket-classifier
  - USE_LOCAL_MODEL=False
  - MLFLOW_TRACKING_URI=http://mlflow:5000
```

### **Ports personnalisés**

```yaml
ports:
  - "8080:8000"  # API sur port 8080
  - "5050:5000"  # MLflow sur port 5050
```

---

## 🔍 Dépannage

### **Problème : L'API ne démarre pas**

```bash
# Voir les logs
docker-compose logs api

# Vérifier la santé
docker-compose ps
```

### **Problème : Modèle non téléchargé**

Le premier démarrage peut prendre 2-3 minutes (téléchargement du modèle 541 MB).

```bash
# Suivre le téléchargement
docker-compose logs -f api
```

### **Problème : Port déjà utilisé**

```bash
# Tuer le processus sur le port 8000
sudo lsof -ti:8000 | xargs kill -9

# Ou changer le port dans docker-compose.yml
```

### **Nettoyer complètement**

```bash
# Arrêter et supprimer tout
docker-compose down -v

# Supprimer les images
docker rmi callcenter-classifier

# Rebuild from scratch
docker-compose up -d --build
```

---

## 🚀 Déploiement en Production

### **Option 1 : Docker Compose avec Nginx**

```yaml
# Ajouter nginx comme reverse proxy
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### **Option 2 : Docker Swarm**

```bash
docker swarm init
docker stack deploy -c docker-compose.yml callcenter
```

### **Option 3 : Kubernetes**

Fichiers disponibles dans `/k8s/` (à créer si besoin).

---

## 📊 Monitoring

### **Healthchecks**

Les conteneurs vérifient automatiquement leur santé :

```bash
# Voir l'état de santé
docker-compose ps
```

### **Métriques**

```bash
# Utilisation CPU/RAM en temps réel
docker stats
```

---

## 🔐 Sécurité

### **Bonnes pratiques appliquées**

- ✅ Image Python officielle (pas d'image tierce)
- ✅ Utilisateur non-root (à ajouter si besoin)
- ✅ Pas de secrets hardcodés
- ✅ Healthchecks activés
- ✅ Restart policy configurée

### **Pour la production**

Ajoutez dans le Dockerfile :

```dockerfile
# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

---

## 📚 Ressources

- **Docker Hub** : (à créer) `docker pull louaykahouli/callcenter-classifier`
- **Documentation** : `/docs` dans l'API
- **GitHub** : https://github.com/louaykahouli/CallCenter-Classifier

---

## ✅ Checklist de Déploiement

- [ ] Image construite : `docker-compose build`
- [ ] Conteneurs démarrés : `docker-compose up -d`
- [ ] API accessible : http://localhost:8000/health
- [ ] MLflow accessible : http://localhost:5000
- [ ] Tests passés : `curl http://localhost:8000/health`
- [ ] Logs vérifiés : `docker-compose logs`
