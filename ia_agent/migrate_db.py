#!/usr/bin/env python3
"""
Script de migration pour ajouter la colonne conversation_title à la base de données
"""
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database(db_path: str = "/app/data/conversations.db"):
    """
    Ajoute la colonne conversation_title si elle n'existe pas
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'conversation_title' not in columns:
            logger.info("🔄 Ajout de la colonne 'conversation_title'...")
            cursor.execute("""
                ALTER TABLE conversations 
                ADD COLUMN conversation_title TEXT
            """)
            conn.commit()
            logger.info("✅ Colonne 'conversation_title' ajoutée avec succès!")
        else:
            logger.info("✅ La colonne 'conversation_title' existe déjà")
        
        conn.close()
        logger.info("🎉 Migration terminée!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration: {e}")
        raise

if __name__ == "__main__":
    migrate_database()
