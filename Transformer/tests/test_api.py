"""
Tests pour l'API de classification
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ajouter le dossier api au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

# NOTE: Ces tests nécessitent que le modèle soit déjà entraîné et placé au bon endroit
# Pour exécuter : pytest tests/test_api.py

@pytest.fixture
def client():
    """Fixture pour créer un client de test"""
    from api.main import app
    return TestClient(app)

def test_root(client):
    """Test de la route racine"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check(client):
    """Test de la vérification de santé"""
    response = client.get("/health")
    assert response.status_code in [200, 503]  # 503 si modèle pas chargé
    
def test_get_classes(client):
    """Test pour récupérer les classes disponibles"""
    response = client.get("/classes")
    if response.status_code == 200:
        data = response.json()
        assert "classes" in data
        assert "count" in data

def test_classify_single_ticket(client):
    """Test de classification d'un ticket unique"""
    payload = {
        "text": "Mon ordinateur ne démarre plus"
    }
    response = client.post("/classify", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        assert "predicted_category" in data
        assert "confidence" in data
        assert "all_predictions" in data
        assert 0 <= data["confidence"] <= 1

def test_classify_empty_text(client):
    """Test avec texte vide"""
    payload = {"text": ""}
    response = client.post("/classify", json=payload)
    assert response.status_code == 400

def test_classify_batch(client):
    """Test de classification batch"""
    payload = {
        "tickets": [
            "Mon ordinateur ne démarre plus",
            "Je n'arrive pas à me connecter",
            "Le service est très lent"
        ]
    }
    response = client.post("/classify-batch", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert "processing_time" in data
        assert len(data["results"]) == 3

def test_classify_batch_too_large(client):
    """Test avec trop de tickets"""
    payload = {
        "tickets": ["Ticket " + str(i) for i in range(101)]
    }
    response = client.post("/classify-batch", json=payload)
    assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__, "-v"])