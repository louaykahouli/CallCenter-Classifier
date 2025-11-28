"""
Tests pour le système de cache et de stockage des conversations
"""

import pytest
import requests
import time
import uuid
from typing import Dict, Any

BASE_URL = "http://localhost:8002"


class TestCache:
    """Tests du système de cache"""
    
    def test_cache_improves_response_time(self):
        """Vérifier que le cache améliore le temps de réponse"""
        # Vider le cache d'abord
        requests.post(f"{BASE_URL}/cache/clear")
        
        text = "Mon imprimante ne fonctionne plus"
        
        # Première requête (sans cache)
        start_time = time.time()
        response1 = requests.post(f"{BASE_URL}/predict", json={"text": text})
        first_time = time.time() - start_time
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["cache_hit"] is False
        
        # Deuxième requête (avec cache)
        start_time = time.time()
        response2 = requests.post(f"{BASE_URL}/predict", json={"text": text})
        second_time = time.time() - start_time
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["cache_hit"] is True
        
        # Le cache devrait être plus rapide
        print(f"\nTemps sans cache: {first_time:.3f}s")
        print(f"Temps avec cache: {second_time:.3f}s")
        print(f"Amélioration: {((first_time - second_time) / first_time * 100):.1f}%")
        
        # Le cache devrait être au moins 50% plus rapide
        assert second_time < first_time * 0.5
    
    def test_cache_stats_endpoint(self):
        """Vérifier l'endpoint des statistiques de cache"""
        response = requests.get(f"{BASE_URL}/cache/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_entries" in data
        assert "active_entries" in data
        assert "total_hits" in data
        assert "cache_ttl" in data
        assert "memory_usage_mb" in data
    
    def test_cache_clear(self):
        """Vérifier que le vidage du cache fonctionne"""
        # Créer une entrée dans le cache
        requests.post(f"{BASE_URL}/predict", json={
            "text": "Test pour le cache"
        })
        
        # Vider le cache
        response = requests.post(f"{BASE_URL}/cache/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert "entries_cleared" in data
        assert data["entries_cleared"] >= 0
        
        # Vérifier que le cache est vide
        stats = requests.get(f"{BASE_URL}/cache/stats").json()
        assert stats["total_entries"] == 0
    
    def test_cache_cleanup_expired(self):
        """Vérifier le nettoyage des entrées expirées"""
        response = requests.post(f"{BASE_URL}/cache/cleanup")
        assert response.status_code == 200
        
        data = response.json()
        assert "entries_removed" in data
        assert data["entries_removed"] >= 0
    
    def test_force_model_bypasses_cache(self):
        """Vérifier que forcer un modèle bypass le cache"""
        text = "Problème de connexion internet"
        
        # Vider le cache
        requests.post(f"{BASE_URL}/cache/clear")
        
        # Première requête normale (mise en cache)
        response1 = requests.post(f"{BASE_URL}/predict", json={"text": text})
        assert response1.json()["cache_hit"] is False
        
        # Deuxième requête avec force_model (devrait bypass le cache)
        response2 = requests.post(f"{BASE_URL}/predict", json={
            "text": text,
            "force_model": "tfidf"
        })
        assert response2.status_code == 200
        # Même si le texte est le même, force_model bypass le cache
        # donc cache_hit devrait être False
        assert response2.json()["cache_hit"] is False


class TestConversations:
    """Tests du système de stockage des conversations"""
    
    def test_session_id_generation(self):
        """Vérifier que les session_id sont générés correctement"""
        response = requests.post(f"{BASE_URL}/predict", json={
            "text": "Test de génération de session_id"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert len(data["session_id"]) > 0
        
        # Vérifier que c'est un UUID valide
        try:
            uuid.UUID(data["session_id"])
        except ValueError:
            pytest.fail("session_id n'est pas un UUID valide")
    
    def test_custom_session_id(self):
        """Vérifier qu'on peut fournir un session_id personnalisé"""
        custom_session_id = "test-session-123"
        
        response = requests.post(f"{BASE_URL}/predict", json={
            "text": "Test avec session_id personnalisé",
            "session_id": custom_session_id
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["session_id"] == custom_session_id
    
    def test_session_history(self):
        """Vérifier la récupération de l'historique d'une session"""
        session_id = str(uuid.uuid4())
        
        # Créer plusieurs conversations dans la même session
        texts = [
            "Ma souris ne fonctionne pas",
            "Comment réinitialiser mon mot de passe?",
            "Problème d'accès au réseau"
        ]
        
        for text in texts:
            requests.post(f"{BASE_URL}/predict", json={
                "text": text,
                "session_id": session_id
            })
        
        # Récupérer l'historique
        response = requests.get(f"{BASE_URL}/history/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert data["count"] >= len(texts)
        assert "conversations" in data
        
        # Vérifier la structure des conversations
        for conv in data["conversations"]:
            assert "id" in conv
            assert "timestamp" in conv
            assert "input_text" in conv
            assert "prediction" in conv
            assert "model_used" in conv
            assert "complexity_score" in conv
    
    def test_empty_session_history(self):
        """Vérifier qu'une session inexistante retourne un historique vide"""
        fake_session_id = str(uuid.uuid4())
        
        response = requests.get(f"{BASE_URL}/history/{fake_session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] == 0
        assert data["conversations"] == []


class TestEnhancedStatistics:
    """Tests des statistiques enrichies"""
    
    def test_stats_include_cache_and_conversations(self):
        """Vérifier que les stats incluent le cache et les conversations"""
        response = requests.get(f"{BASE_URL}/stats")
        assert response.status_code == 200
        
        data = response.json()
        
        # Vérifier les statistiques de l'agent
        assert "agent_statistics" in data
        
        # Vérifier les statistiques du cache
        assert "cache_statistics" in data
        cache_stats = data["cache_statistics"]
        assert "total_entries" in cache_stats
        assert "total_hits" in cache_stats
        
        # Vérifier les statistiques des conversations
        assert "conversation_statistics" in data
        conv_stats = data["conversation_statistics"]
        assert "total_conversations" in conv_stats
        assert "unique_sessions" in conv_stats
        assert "model_distribution" in conv_stats
        assert "category_distribution" in conv_stats
        
        # Vérifier la configuration
        assert "configuration" in data
        config = data["configuration"]
        assert "cache_enabled" in config
        assert "cache_ttl" in config
    
    def test_conversation_statistics_accuracy(self):
        """Vérifier l'exactitude des statistiques de conversation"""
        session_id = str(uuid.uuid4())
        
        # Créer quelques conversations
        for i in range(3):
            requests.post(f"{BASE_URL}/predict", json={
                "text": f"Test statistiques {i}",
                "session_id": session_id
            })
        
        # Récupérer les stats
        response = requests.get(f"{BASE_URL}/stats")
        data = response.json()
        
        conv_stats = data["conversation_statistics"]
        
        # Vérifier que les conversations ont été comptées
        assert conv_stats["total_conversations"] >= 3
        assert conv_stats["unique_sessions"] >= 1
        
        # Vérifier la distribution des modèles
        model_dist = conv_stats["model_distribution"]
        assert isinstance(model_dist, dict)
        
        # Au moins un modèle devrait avoir été utilisé
        total_model_uses = sum(model_dist.values())
        assert total_model_uses >= 3


class TestIntegration:
    """Tests d'intégration cache + conversations"""
    
    def test_full_workflow_with_cache_and_history(self):
        """Test du workflow complet avec cache et historique"""
        session_id = str(uuid.uuid4())
        text = "Mon ordinateur redémarre tout seul"
        
        # 1. Première prédiction (sans cache)
        response1 = requests.post(f"{BASE_URL}/predict", json={
            "text": text,
            "session_id": session_id
        })
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["cache_hit"] is False
        assert data1["session_id"] == session_id
        
        # 2. Deuxième prédiction (avec cache)
        response2 = requests.post(f"{BASE_URL}/predict", json={
            "text": text,
            "session_id": session_id
        })
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["cache_hit"] is True
        
        # 3. Vérifier l'historique
        history = requests.get(f"{BASE_URL}/history/{session_id}").json()
        assert history["count"] >= 2
        
        # 4. Vérifier les statistiques
        stats = requests.get(f"{BASE_URL}/stats").json()
        assert stats["cache_statistics"]["total_hits"] > 0
        assert stats["conversation_statistics"]["total_conversations"] >= 2
        
        print("\n✅ Workflow complet validé:")
        print(f"  - Cache hits: {stats['cache_statistics']['total_hits']}")
        print(f"  - Conversations: {stats['conversation_statistics']['total_conversations']}")
        print(f"  - Sessions uniques: {stats['conversation_statistics']['unique_sessions']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
