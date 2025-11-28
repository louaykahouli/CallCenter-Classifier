"""
Gestionnaire de cache pour l'Agent IA Intelligent
Supporte SQLite et PostgreSQL pour la persistence
"""

import hashlib
import json
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

# Détecter le type de DB depuis l'environnement
DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()

# Import conditionnel de psycopg2
if DB_TYPE == 'postgresql':
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        logger.warning("psycopg2 non installé, fallback vers SQLite")
        DB_TYPE = 'sqlite'


class CacheManager:
    """Gestionnaire de cache en mémoire avec fallback"""
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Initialise le gestionnaire de cache
        
        Args:
            cache_ttl: Durée de vie du cache en secondes (défaut: 1 heure)
        """
        self.cache_ttl = cache_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        logger.info(f"CacheManager initialisé avec TTL={cache_ttl}s")
    
    def _generate_key(self, text: str, model: Optional[str] = None) -> str:
        """
        Génère une clé unique pour le cache basée sur le texte et le modèle
        
        Args:
            text: Texte à cacher
            model: Modèle utilisé (optionnel)
            
        Returns:
            Clé de cache (hash MD5)
        """
        key_data = f"{text}:{model}" if model else text
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, text: str, model: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Récupère une valeur du cache
        
        Args:
            text: Texte recherché
            model: Modèle utilisé (optionnel)
            
        Returns:
            Données cachées ou None si pas trouvé/expiré
        """
        key = self._generate_key(text, model)
        
        if key not in self.cache:
            logger.debug(f"Cache MISS pour clé {key[:8]}...")
            return None
        
        entry = self.cache[key]
        
        # Vérifier l'expiration
        if datetime.now() > entry['expires_at']:
            logger.debug(f"Cache EXPIRED pour clé {key[:8]}...")
            del self.cache[key]
            return None
        
        logger.info(f"Cache HIT pour clé {key[:8]}...")
        entry['hits'] += 1
        entry['last_accessed'] = datetime.now()
        return entry['data']
    
    def set(self, text: str, data: Dict[str, Any], model: Optional[str] = None) -> None:
        """
        Stocke une valeur dans le cache
        
        Args:
            text: Texte clé
            data: Données à cacher
            model: Modèle utilisé (optionnel)
        """
        key = self._generate_key(text, model)
        
        self.cache[key] = {
            'data': data,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=self.cache_ttl),
            'last_accessed': datetime.now(),
            'hits': 0
        }
        
        logger.info(f"Cache SET pour clé {key[:8]}... (TTL={self.cache_ttl}s)")
    
    def clear(self) -> int:
        """
        Vide le cache complètement
        
        Returns:
            Nombre d'entrées supprimées
        """
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cache vidé ({count} entrées supprimées)")
        return count
    
    def cleanup_expired(self) -> int:
        """
        Nettoie les entrées expirées du cache
        
        Returns:
            Nombre d'entrées supprimées
        """
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Nettoyage: {len(expired_keys)} entrées expirées supprimées")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du cache
        
        Returns:
            Dictionnaire avec les statistiques
        """
        now = datetime.now()
        total_entries = len(self.cache)
        expired_entries = sum(
            1 for entry in self.cache.values()
            if now > entry['expires_at']
        )
        total_hits = sum(entry['hits'] for entry in self.cache.values())
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_entries,
            'expired_entries': expired_entries,
            'total_hits': total_hits,
            'cache_ttl': self.cache_ttl,
            'memory_usage_mb': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """
        Estime l'utilisation mémoire du cache
        
        Returns:
            Taille estimée en MB
        """
        try:
            import sys
            total_size = sum(
                sys.getsizeof(json.dumps(entry['data']))
                for entry in self.cache.values()
            )
            return round(total_size / (1024 * 1024), 2)
        except Exception:
            return 0.0


class ConversationStore:
    """Gestionnaire de stockage des conversations avec SQLite ou PostgreSQL"""
    
    def __init__(self, db_path: str = "conversations.db"):
        """
        Initialise le gestionnaire de stockage
        
        Args:
            db_path: Chemin vers la base de données SQLite (ignoré si PostgreSQL)
        """
        self.db_type = DB_TYPE
        self.db_path = Path(db_path) if DB_TYPE == 'sqlite' else None
        
        if DB_TYPE == 'postgresql':
            self.pg_config = {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': int(os.getenv('POSTGRES_PORT', 5432)),
                'database': os.getenv('POSTGRES_DB', 'conversations'),
                'user': os.getenv('POSTGRES_USER', 'callcenter'),
                'password': os.getenv('POSTGRES_PASSWORD', 'callcenter2024')
            }
            logger.info(f"ConversationStore initialisé avec PostgreSQL ({self.pg_config['host']}:{self.pg_config['port']})")
        else:
            logger.info(f"ConversationStore initialisé avec SQLite DB={db_path}")
        
        self._init_database()
    
    def _get_connection(self):
        """Retourne une connexion selon le type de DB"""
        if self.db_type == 'postgresql':
            return psycopg2.connect(**self.pg_config)
        else:
            return sqlite3.connect(self.db_path)
    
    def _init_database(self) -> None:
        """Initialise la base de données (SQLite ou PostgreSQL)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if self.db_type == 'postgresql':
            # PostgreSQL syntax
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
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
                    probabilities JSONB
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metadata JSONB
                )
            """)
            
            # Index PostgreSQL
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id 
                ON conversations(session_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON conversations(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_used 
                ON conversations(model_used)
            """)
            
        else:
            # SQLite syntax
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    conversation_title TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    input_text TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    complexity_score REAL NOT NULL,
                    complexity_level TEXT NOT NULL,
                    response_time REAL,
                    generated_response TEXT,
                    probabilities TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Index SQLite
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id 
                ON conversations(session_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON conversations(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_used 
                ON conversations(model_used)
            """)
        
        conn.commit()
        conn.close()
        logger.info(f"Base de données {self.db_type.upper()} initialisée avec succès")
    
    def save_conversation(
        self,
        session_id: str,
        input_text: str,
        prediction: str,
        model_used: str,
        complexity_score: float,
        complexity_level: str,
        probabilities: Dict[str, float],
        response_time: Optional[float] = None,
        generated_response: Optional[str] = None,
        conversation_title: Optional[str] = None
    ) -> int:
        """
        Sauvegarde une conversation dans la base de données
        
        Args:
            session_id: ID de la session utilisateur
            input_text: Texte d'entrée
            prediction: Catégorie prédite
            model_used: Modèle utilisé (tfidf/transformer)
            complexity_score: Score de complexité
            complexity_level: Niveau de complexité
            probabilities: Probabilités par catégorie
            response_time: Temps de réponse en secondes
            generated_response: Réponse générée par Grok
            conversation_title: Titre descriptif de la conversation
            
        Returns:
            ID de la conversation créée
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if self.db_type == 'postgresql':
            # PostgreSQL - utilise RETURNING pour récupérer l'ID
            cursor.execute("""
                INSERT INTO conversations (
                    session_id, conversation_title, input_text, prediction, model_used,
                    complexity_score, complexity_level, probabilities,
                    response_time, generated_response
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                session_id,
                conversation_title,
                input_text,
                prediction,
                model_used,
                complexity_score,
                complexity_level,
                json.dumps(probabilities),  # JSONB
                response_time,
                generated_response
            ))
            conversation_id = cursor.fetchone()[0]
        else:
            # SQLite
            cursor.execute("""
                INSERT INTO conversations (
                    session_id, conversation_title, input_text, prediction, model_used,
                    complexity_score, complexity_level, probabilities,
                    response_time, generated_response
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                conversation_title,
                input_text,
                prediction,
                model_used,
                complexity_score,
                complexity_level,
                json.dumps(probabilities),
                response_time,
                generated_response
            ))
            conversation_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        logger.info(f"Conversation {conversation_id} sauvegardée (session={session_id})")
        return conversation_id
    
    def get_session_history(self, session_id: str, limit: int = 50) -> list:
        """
        Récupère l'historique d'une session
        
        Args:
            session_id: ID de la session
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des conversations
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if self.db_type == 'postgresql':
            cursor.execute("""
                SELECT * FROM conversations
                WHERE session_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (session_id, limit))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            conn.close()
            
            conversations = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                conversations.append({
                    'id': row_dict['id'],
                    'timestamp': row_dict['timestamp'].isoformat() if row_dict['timestamp'] else None,
                    'input_text': row_dict['input_text'],
                    'prediction': row_dict['prediction'],
                    'model_used': row_dict['model_used'],
                    'complexity_score': row_dict['complexity_score'],
                    'complexity_level': row_dict['complexity_level'],
                    'probabilities': row_dict['probabilities'] if isinstance(row_dict['probabilities'], dict) else {},
                    'response_time': row_dict['response_time'],
                    'generated_response': row_dict['generated_response'],
                    'conversation_title': row_dict.get('conversation_title')  # Ajout du titre
                })
        else:
            # SQLite
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            conversations = []
            for row in rows:
                conversations.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'input_text': row['input_text'],
                    'prediction': row['prediction'],
                    'model_used': row['model_used'],
                    'complexity_score': row['complexity_score'],
                    'complexity_level': row['complexity_level'],
                    'probabilities': json.loads(row['probabilities']) if row['probabilities'] else {},
                    'response_time': row['response_time'],
                    'generated_response': row['generated_response'],
                    'conversation_title': row['conversation_title'] if 'conversation_title' in row.keys() else None  # Ajout du titre
                })
        
        return conversations
    
    def get_global_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Récupère les statistiques globales
        
        Args:
            days: Nombre de jours à analyser
            
        Returns:
            Dictionnaire avec les statistiques
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Date limite
        if self.db_type == 'postgresql':
            date_limit = (datetime.now() - timedelta(days=days))
            placeholder = '%s'
        else:
            date_limit = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            placeholder = '?'
        
        # Nombre total de conversations
        cursor.execute(f"""
            SELECT COUNT(*) FROM conversations
            WHERE timestamp >= {placeholder}
        """, (date_limit,))
        total_conversations = cursor.fetchone()[0]
        
        # Répartition par modèle
        cursor.execute(f"""
            SELECT model_used, COUNT(*) as count
            FROM conversations
            WHERE timestamp >= {placeholder}
            GROUP BY model_used
        """, (date_limit,))
        model_distribution = dict(cursor.fetchall())
        
        # Répartition par catégorie
        cursor.execute(f"""
            SELECT prediction, COUNT(*) as count
            FROM conversations
            WHERE timestamp >= {placeholder}
            GROUP BY prediction
            ORDER BY count DESC
        """, (date_limit,))
        category_distribution = dict(cursor.fetchall())
        
        # Temps de réponse moyen
        cursor.execute(f"""
            SELECT AVG(response_time) as avg_time,
                   MIN(response_time) as min_time,
                   MAX(response_time) as max_time
            FROM conversations
            WHERE timestamp >= {placeholder} AND response_time IS NOT NULL
        """, (date_limit,))
        time_stats = cursor.fetchone()
        
        # Score de complexité moyen
        cursor.execute(f"""
            SELECT AVG(complexity_score) as avg_complexity
            FROM conversations
            WHERE timestamp >= {placeholder}
        """, (date_limit,))
        avg_complexity = cursor.fetchone()[0] or 0
        
        # Sessions uniques
        cursor.execute(f"""
            SELECT COUNT(DISTINCT session_id) as unique_sessions
            FROM conversations
            WHERE timestamp >= {placeholder}
        """, (date_limit,))
        unique_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'period_days': days,
            'total_conversations': total_conversations,
            'unique_sessions': unique_sessions,
            'model_distribution': model_distribution,
            'category_distribution': category_distribution,
            'response_time': {
                'avg': round(time_stats[0], 3) if time_stats[0] else None,
                'min': round(time_stats[1], 3) if time_stats[1] else None,
                'max': round(time_stats[2], 3) if time_stats[2] else None
            },
            'avg_complexity_score': round(avg_complexity, 2)
        }
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """
        Nettoie les conversations anciennes
        
        Args:
            days: Supprimer les conversations plus anciennes que X jours
            
        Returns:
            Nombre de conversations supprimées
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_limit = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            DELETE FROM conversations
            WHERE timestamp < ?
        """, (date_limit,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Nettoyage: {deleted_count} conversations supprimées (>{days} jours)")
        return deleted_count

