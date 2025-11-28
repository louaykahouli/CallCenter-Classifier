#!/usr/bin/env python3
"""
Script de migration SQLite → PostgreSQL
Copie toutes les conversations de SQLite vers PostgreSQL
"""

import sqlite3
import psycopg2
import json
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SQLITE_PATH = "/app/data/conversations.db"
PG_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'conversations'),
    'user': os.getenv('POSTGRES_USER', 'callcenter'),
    'password': os.getenv('POSTGRES_PASSWORD', 'callcenter2024')
}

def migrate_conversations():
    """Migre toutes les conversations de SQLite vers PostgreSQL"""
    
    # Vérifier que SQLite existe
    if not Path(SQLITE_PATH).exists():
        logger.warning(f"❌ Base SQLite non trouvée: {SQLITE_PATH}")
        logger.info("Aucune donnée à migrer, c'est OK si c'est une nouvelle installation.")
        return 0
    
    # Connexion SQLite
    logger.info(f"📂 Connexion à SQLite: {SQLITE_PATH}")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connexion PostgreSQL
    logger.info(f"🐘 Connexion à PostgreSQL: {PG_CONFIG['host']}:{PG_CONFIG['port']}")
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cursor = pg_conn.cursor()
    except Exception as e:
        logger.error(f"❌ Impossible de se connecter à PostgreSQL: {e}")
        logger.info("Astuce: Assure-toi que le conteneur postgres est démarré")
        return 1
    
    # Compter les conversations dans SQLite
    sqlite_cursor.execute("SELECT COUNT(*) FROM conversations")
    total_sqlite = sqlite_cursor.fetchone()[0]
    logger.info(f"📊 Conversations dans SQLite: {total_sqlite}")
    
    if total_sqlite == 0:
        logger.info("✅ Aucune conversation à migrer")
        return 0
    
    # Compter les conversations dans PostgreSQL
    pg_cursor.execute("SELECT COUNT(*) FROM conversations")
    total_pg = pg_cursor.fetchone()[0]
    logger.info(f"📊 Conversations dans PostgreSQL: {total_pg}")
    
    # Récupérer toutes les conversations SQLite
    sqlite_cursor.execute("""
        SELECT 
            session_id, conversation_title, timestamp, input_text, 
            prediction, model_used, complexity_score, complexity_level,
            response_time, generated_response, probabilities
        FROM conversations
        ORDER BY id
    """)
    
    conversations = sqlite_cursor.fetchall()
    migrated = 0
    skipped = 0
    
    logger.info(f"🔄 Migration de {len(conversations)} conversations...")
    
    for row in conversations:
        try:
            # Parser les probabilities (JSON)
            probabilities = json.loads(row['probabilities']) if row['probabilities'] else {}
            
            # Vérifier si la conversation existe déjà (éviter les doublons)
            pg_cursor.execute("""
                SELECT id FROM conversations 
                WHERE session_id = %s AND input_text = %s AND timestamp = %s
            """, (row['session_id'], row['input_text'], row['timestamp']))
            
            if pg_cursor.fetchone():
                skipped += 1
                continue
            
            # Insérer dans PostgreSQL
            pg_cursor.execute("""
                INSERT INTO conversations (
                    session_id, conversation_title, timestamp, input_text,
                    prediction, model_used, complexity_score, complexity_level,
                    response_time, generated_response, probabilities
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['session_id'],
                row['conversation_title'],
                row['timestamp'],
                row['input_text'],
                row['prediction'],
                row['model_used'],
                row['complexity_score'],
                row['complexity_level'],
                row['response_time'],
                row['generated_response'],
                json.dumps(probabilities)  # JSONB
            ))
            
            migrated += 1
            
            if migrated % 100 == 0:
                logger.info(f"  ⏳ {migrated}/{len(conversations)} migrées...")
        
        except Exception as e:
            logger.error(f"❌ Erreur lors de la migration d'une conversation: {e}")
            continue
    
    # Commit
    pg_conn.commit()
    
    # Fermer les connexions
    sqlite_conn.close()
    pg_conn.close()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Migration terminée!")
    logger.info(f"   📊 Total SQLite: {total_sqlite}")
    logger.info(f"   ✅ Migrées: {migrated}")
    logger.info(f"   ⏭️  Ignorées (doublons): {skipped}")
    logger.info(f"   🐘 Total PostgreSQL: {total_pg + migrated}")
    logger.info(f"{'='*60}\n")
    
    return 0

if __name__ == "__main__":
    exit(migrate_conversations())
