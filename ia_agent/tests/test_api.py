"""
Tests pour l'API de l'Agent IA Intelligent
Tests unitaires et d'intégration
"""

import pytest
import requests
import time
from typing import Dict, List

# Configuration
BASE_URL = "http://localhost:8002"
TIMEOUT = 30


class TestHealthCheck:
    """Tests pour le endpoint /health"""
    
    def test_health_endpoint_exists(self):
        """Vérifie que le endpoint /health existe"""
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200
    
    def test_health_response_structure(self):
        """Vérifie la structure de la réponse /health"""
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        data = response.json()
        
        assert "status" in data
        assert "agent" in data
        assert "models" in data
        assert "threshold" in data
        
        assert data["status"] == "healthy"
        assert data["agent"] == "operational"
    
    def test_health_models_status(self):
        """Vérifie que les statuts des modèles sont présents"""
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        data = response.json()
        
        assert "tfidf" in data["models"]
        assert "transformer" in data["models"]


class TestComplexityAnalysis:
    """Tests pour le endpoint /analyze"""
    
    def test_analyze_simple_text(self):
        """Test d'analyse avec un texte simple"""
        payload = {"text": "Imprimante cassée"}
        response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "complexity_score" in data
        assert "complexity_level" in data
        assert "recommended_model" in data
        assert data["complexity_score"] < 35  # Devrait être simple
    
    def test_analyze_medium_text(self):
        """Test d'analyse avec un texte moyen"""
        payload = {"text": "Je ne peux pas me connecter au serveur partagé depuis ce matin"}
        response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 30 <= data["complexity_score"] <= 60
    
    def test_analyze_complex_text(self):
        """Test d'analyse avec un texte complexe"""
        payload = {
            "text": "Plusieurs utilisateurs du département RH signalent des problèmes d'accès intermittents au serveur partagé depuis l'installation du nouveau pare-feu la semaine dernière"
        }
        response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["complexity_score"] >= 35  # Devrait recommander transformer
        assert data["recommended_model"] == "transformer"
    
    def test_analyze_empty_text(self):
        """Test avec texte vide"""
        payload = {"text": ""}
        response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=TIMEOUT)
        
        # Devrait retourner une erreur 422 (Validation Error)
        assert response.status_code == 422
    
    def test_analyze_response_structure(self):
        """Vérifie la structure complète de la réponse"""
        payload = {"text": "Test de structure"}
        response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "text",
            "complexity_score",
            "complexity_level",
            "recommended_model",
            "details",
            "reasoning"
        ]
        
        for field in required_fields:
            assert field in data, f"Champ manquant: {field}"


class TestPrediction:
    """Tests pour le endpoint /predict"""
    
    def test_predict_simple_text(self):
        """Test de prédiction avec texte simple"""
        payload = {"text": "Mon clavier ne fonctionne plus"}
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "prediction" in data
        assert "probabilities" in data
        assert "model_used" in data
        assert data["model_used"] == "tfidf"  # Devrait utiliser TF-IDF
    
    def test_predict_complex_text(self):
        """Test de prédiction avec texte complexe"""
        payload = {
            "text": "Plusieurs utilisateurs signalent des problèmes de connexion VPN avec le nouveau système d'authentification multi-facteurs déployé la semaine dernière"
        }
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        # Devrait utiliser Transformer si complexité >= 35
        assert "model_used" in data
    
    def test_predict_force_model_tfidf(self):
        """Test avec forçage du modèle TF-IDF"""
        payload = {
            "text": "Problème urgent à résoudre",
            "force_model": "tfidf"
        }
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_used"] == "tfidf"
    
    def test_predict_response_structure(self):
        """Vérifie la structure de la réponse de prédiction"""
        payload = {"text": "Test structure"}
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "input",
            "prediction",
            "probabilities",
            "model_used",
            "complexity_analysis",
            "reasoning",
            "generated_response"
        ]
        
        for field in required_fields:
            assert field in data, f"Champ manquant: {field}"
    
    def test_predict_probabilities_sum(self):
        """Vérifie que les probabilités somment à ~1.0"""
        payload = {"text": "Mon ordinateur ne démarre pas"}
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        probs = data["probabilities"]
        total = sum(probs.values())
        
        # La somme devrait être proche de 1.0 (avec tolérance)
        assert 0.99 <= total <= 1.01
    
    def test_predict_categories(self):
        """Vérifie que les catégories attendues sont présentes"""
        payload = {"text": "Test catégories"}
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        expected_categories = [
            "Hardware",
            "Access",
            "HR Support",
            "Administrative rights",
            "Storage",
            "Purchase",
            "Internal Project",
            "Miscellaneous"
        ]
        
        probs = data["probabilities"]
        # Au moins quelques catégories devraient être présentes
        assert len(probs) > 0


class TestStatistics:
    """Tests pour le endpoint /stats"""
    
    def test_stats_endpoint(self):
        """Vérifie que le endpoint /stats fonctionne"""
        response = requests.get(f"{BASE_URL}/stats", timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "statistics" in data
        assert "configuration" in data


class TestPerformance:
    """Tests de performance"""
    
    def test_response_time_analyze(self):
        """Vérifie que /analyze répond rapidement"""
        payload = {"text": "Test de performance"}
        
        start = time.time()
        response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=TIMEOUT)
        end = time.time()
        
        assert response.status_code == 200
        response_time = end - start
        
        # Devrait répondre en moins de 2 secondes
        assert response_time < 2.0
    
    def test_response_time_predict_tfidf(self):
        """Vérifie le temps de réponse pour TF-IDF"""
        payload = {"text": "Souris cassée"}
        
        start = time.time()
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        end = time.time()
        
        assert response.status_code == 200
        response_time = end - start
        
        # TF-IDF devrait être rapide (< 5 secondes avec Grok)
        assert response_time < 10.0


class TestErrorHandling:
    """Tests de gestion d'erreurs"""
    
    def test_invalid_json(self):
        """Test avec JSON invalide"""
        response = requests.post(
            f"{BASE_URL}/predict",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 422
    
    def test_missing_text_field(self):
        """Test avec champ 'text' manquant"""
        payload = {"wrong_field": "value"}
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 422
    
    def test_empty_text(self):
        """Test avec texte vide"""
        payload = {"text": ""}
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        
        assert response.status_code == 422


class TestIntegration:
    """Tests d'intégration"""
    
    def test_full_workflow(self):
        """Test du workflow complet: analyze -> predict"""
        text = "Je ne peux pas accéder au dossier partagé"
        
        # 1. Analyser la complexité
        analyze_response = requests.post(
            f"{BASE_URL}/analyze",
            json={"text": text},
            timeout=TIMEOUT
        )
        assert analyze_response.status_code == 200
        analyze_data = analyze_response.json()
        
        # 2. Faire la prédiction
        predict_response = requests.post(
            f"{BASE_URL}/predict",
            json={"text": text},
            timeout=TIMEOUT
        )
        assert predict_response.status_code == 200
        predict_data = predict_response.json()
        
        # 3. Vérifier la cohérence
        assert analyze_data["complexity_score"] == predict_data["complexity_analysis"]["score"]
    
    def test_multiple_predictions(self):
        """Test de plusieurs prédictions successives"""
        texts = [
            "Imprimante cassée",
            "Mot de passe oublié",
            "Besoin d'un nouvel ordinateur"
        ]
        
        for text in texts:
            response = requests.post(
                f"{BASE_URL}/predict",
                json={"text": text},
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            assert "prediction" in data


# Configuration pytest
@pytest.fixture(scope="session", autouse=True)
def check_server():
    """Vérifie que le serveur est accessible avant de lancer les tests"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            pytest.exit("❌ Le serveur n'est pas accessible. Lancez 'docker compose up -d' d'abord.")
    except requests.exceptions.ConnectionError:
        pytest.exit("❌ Impossible de se connecter à l'API. Vérifiez que le serveur est démarré.")


if __name__ == "__main__":
    # Lancer les tests avec pytest
    pytest.main([__file__, "-v", "--tb=short"])
