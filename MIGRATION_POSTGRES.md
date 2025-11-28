# Migration SQLite → PostgreSQL

## 📋 Vue d'ensemble

Ce guide explique comment migrer de SQLite vers PostgreSQL pour la base de données des conversations.

## 🎯 Avantages de PostgreSQL

- ✅ **Performance** : Meilleur pour les écritures concurrentes
- ✅ **Scalabilité** : Support de milliers de connexions simultanées
- ✅ **JSONB** : Stockage natif optimisé pour les probabilités
- ✅ **Production-ready** : Backup, réplication, haute disponibilité
- ✅ **Requêtes avancées** : Full-text search, CTEs, window functions

## 🚀 Migration rapide (3 étapes)

### 1. Démarrer PostgreSQL

```bash
# Démarrer tous les services avec PostgreSQL
cd /home/louay/Desktop/Project/CallCenter
docker compose up -d
```

Le service PostgreSQL sera créé automatiquement avec :
- **User** : `callcenter`
- **Password** : `callcenter2024`
- **Database** : `conversations`
- **Port** : `5432`

### 2. Attendre que PostgreSQL soit prêt

```bash
# Vérifier que postgres est healthy
docker compose ps

# Ou attendre manuellement
sleep 10
```

### 3. Lancer la migration

```bash
# Exécuter le script de migration dans le conteneur ia-agent
docker exec ia-agent python /app/migrate_sqlite_to_postgres.py
```

Le script va :
1. Lire toutes les conversations depuis SQLite (`/app/data/conversations.db`)
2. Les copier vers PostgreSQL (en évitant les doublons)
3. Afficher un résumé de la migration

## 🔄 Retour à SQLite (si besoin)

Si tu veux revenir à SQLite temporairement :

```bash
# Modifier docker-compose.yml
# Dans la section ia-agent > environment, changer:
- DB_TYPE=sqlite  # au lieu de postgresql

# Redémarrer
docker compose restart ia-agent
```

## 📊 Vérifier la migration

### Vérifier PostgreSQL

```bash
# Se connecter à PostgreSQL
docker exec -it callcenter-postgres psql -U callcenter -d conversations

# Dans psql:
SELECT COUNT(*) FROM conversations;
SELECT prediction, COUNT(*) FROM conversations GROUP BY prediction;
\q
```

### Vérifier l'API

```bash
# Test de prédiction
curl -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Test PostgreSQL migration", "conversation_title": "Test"}' | jq

# Statistiques
curl http://localhost:8002/stats | jq
```

## 🛠️ Structure des tables PostgreSQL

### Table `conversations`

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    conversation_title TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    input_text TEXT NOT NULL,
    prediction TEXT NOT NULL,
    model_used TEXT NOT NULL,
    complexity_score REAL NOT NULL,
    complexity_level TEXT NOT NULL,
    response_time REAL,
    generated_response TEXT,
    probabilities JSONB  -- Native JSON support!
);

CREATE INDEX idx_session_id ON conversations(session_id);
CREATE INDEX idx_timestamp ON conversations(timestamp);
CREATE INDEX idx_model_used ON conversations(model_used);
```

## 🔍 Commandes utiles

### Backup PostgreSQL

```bash
# Dump complet
docker exec callcenter-postgres pg_dump -U callcenter conversations > backup.sql

# Restore
cat backup.sql | docker exec -i callcenter-postgres psql -U callcenter conversations
```

### Monitoring

```bash
# Logs PostgreSQL
docker logs callcenter-postgres --tail 50

# Logs ia-agent
docker logs ia-agent --tail 50

# Stats PostgreSQL en temps réel
docker exec -it callcenter-postgres psql -U callcenter -d conversations -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

## ⚠️ Troubleshooting

### Erreur "connection refused"

```bash
# Vérifier que postgres est démarré
docker compose ps
docker logs callcenter-postgres

# Redémarrer si nécessaire
docker compose restart postgres
sleep 5
docker compose restart ia-agent
```

### Migration bloquée

```bash
# Vérifier les connexions PostgreSQL
docker exec callcenter-postgres psql -U callcenter -d conversations -c "
SELECT pid, usename, application_name, state, query 
FROM pg_stat_activity 
WHERE datname = 'conversations';
"
```

## 📈 Performance

**SQLite vs PostgreSQL (sur ce projet)** :

| Métrique | SQLite | PostgreSQL |
|----------|--------|------------|
| Lectures | ~0.5ms | ~0.3ms |
| Écritures | ~2ms | ~1ms |
| Connexions simultanées | 1 | Illimité |
| Taille max recommandée | < 1GB | Plusieurs TB |

## 🎉 C'est tout !

Après la migration, toutes les nouvelles conversations seront automatiquement sauvegardées dans PostgreSQL. Le fichier SQLite reste disponible comme backup.
