"""
API pour l'Agent IA Intelligent
Route les requêtes vers TF-IDF ou Transformer selon la complexité
Utilise Grok pour générer des réponses intelligentes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import logging
import os
from typing import Dict, Optional
from intelligent_agent import IntelligentAgent

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clé API Grok depuis les variables d'environnement
GROK_API_KEY = os.getenv("GROK_API_KEY", "xai-EyqPqZvWyTu8mnQiFCFyYPVuAYdNxPnnjw4z9onvzqrZ5wAjcNkJqWwKx4uc7tY5d68c1njQyeDgJwKx")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
USE_GROK = os.getenv("USE_GROK", "true").lower() == "true"

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Agent IA Intelligent",
    description="Router intelligent qui choisit le meilleur modèle selon la complexité du texte",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation de l'agent
agent = IntelligentAgent(use_distilbert_for_all=False)

# Configuration des URLs des modèles
TFIDF_API_URL = "http://tfidf-svm:8000/predict"  # URL interne Docker
# Le service Transformer expose /classify (voir Transformer/api/main.py)
TRANSFORMER_API_URL = "http://callcenter:8000/classify"  # URL interne Docker

# Configuration des seuils de routage
COMPLEXITY_THRESHOLD = 35  # Score < 35 → TF-IDF, Score >= 35 → Transformer


async def generate_grok_response(
    input_text: str,
    prediction: str,
    probabilities: Dict[str, float],
    model_used: str,
    complexity_score: int,
    complexity_level: str
) -> str:
    """
    Génère une réponse intelligente en utilisant l'API Grok de xAI
    
    Args:
        input_text: Le texte d'entrée
        prediction: La catégorie prédite
        probabilities: Les probabilités pour chaque catégorie
        model_used: Le modèle utilisé (tfidf ou transformer)
        complexity_score: Le score de complexité
        complexity_level: Le niveau de complexité
        
    Returns:
        Une réponse générée par Grok en langage naturel
    """
    if not USE_GROK or not GROK_API_KEY:
        logger.warning("Grok désactivé ou pas de clé API, utilisation du fallback")
        return generate_fallback_response(
            input_text, prediction, probabilities, 
            model_used, complexity_score, complexity_level
        )
    
    try:
        # Préparer le contexte pour Grok
        top_predictions = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:3]
        confidence = top_predictions[0][1] * 100
        
        # Créer le prompt pour Grok
        prompt = f"""Tu es un assistant IA intelligent pour un centre d'appels IT. 

Un ticket vient d'être analysé avec les résultats suivants:

TICKET: "{input_text}"

RÉSULTATS DE L'ANALYSE:
- Catégorie prédite: {prediction}
- Confiance: {confidence:.1f}%
- Modèle utilisé: {"TF-IDF/SVM (rapide)" if model_used == "tfidf" else "Transformer (précis)"}
- Score de complexité: {complexity_score}/100 ({complexity_level})

TOP 3 PRÉDICTIONS:
{chr(10).join([f"- {cat}: {prob*100:.1f}%" for cat, prob in top_predictions])}

GÉNÈRE une réponse professionnelle et utile pour l'utilisateur qui contient:
1. Une confirmation que tu as compris sa demande
2. La catégorie identifiée et pourquoi
3. Une recommandation concrète ou prochaine étape
4. Un ton sympathique et rassurant

Réponds en français, en 3-4 phrases maximum, format texte brut (pas de markdown)."""

        # Appeler l'API Grok
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                GROK_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GROK_API_KEY}"
                },
                json={
                    "messages": [
                        {
                            "role": "system",
                            "content": "Tu es un assistant IA professionnel pour un centre d'appels IT. Réponds de manière claire, concise et utile."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "grok-beta",
                    "stream": False,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                grok_response = result['choices'][0]['message']['content']
                logger.info("Réponse Grok générée avec succès")
                return grok_response.strip()
            else:
                logger.error(f"Erreur API Grok: {response.status_code}")
                return generate_fallback_response(
                    input_text, prediction, probabilities,
                    model_used, complexity_score, complexity_level
                )
    
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à Grok: {str(e)}")
        return generate_fallback_response(
            input_text, prediction, probabilities,
            model_used, complexity_score, complexity_level
        )


def generate_fallback_response(
    input_text: str,
    prediction: str,
    probabilities: Dict[str, float],
    model_used: str,
    complexity_score: int,
    complexity_level: str
) -> str:
    """
    Génère une réponse simple sans Grok (fallback)
    """
    top_predictions = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:3]
    confidence = top_predictions[0][1] * 100
    
    category_messages = {
        "Hardware": "un problème matériel",
        "Access": "une demande d'accès ou de permissions",
        "HR Support": "une question RH",
        "Administrative rights": "une demande de droits administratifs",
        "Storage": "un problème de stockage",
        "Purchase": "une demande d'achat",
        "Internal Project": "une question de projet interne",
        "Miscellaneous": "une demande diverse"
    }
    
    category_desc = category_messages.get(prediction, "une demande")
    
    response = f"""J'ai analysé votre demande et identifié {category_desc} (catégorie: {prediction}).

Ma confiance dans cette classification est de {confidence:.1f}%.

Modèle utilisé: {"TF-IDF/SVM (analyse rapide)" if model_used == "tfidf" else "Transformer (analyse approfondie)"}.

Votre demande a été correctement catégorisée et sera traitée par le service approprié."""
    
    return response


class TextRequest(BaseModel):
    """Schéma de la requête"""
    text: str
    force_model: Optional[str] = None  # 'tfidf' ou 'transformer' pour forcer un modèle


class PredictionResponse(BaseModel):
    """Schéma de la réponse"""
    input: str
    prediction: str
    probabilities: Dict[str, float]
    model_used: str
    complexity_analysis: Dict
    reasoning: str
    generated_response: str  # Nouvelle réponse générée en langage naturel


@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "service": "Agent IA Intelligent",
        "version": "1.0.0",
        "description": "Router intelligent vers TF-IDF ou Transformer",
        "endpoints": {
            "/predict": "Prédiction avec routage intelligent",
            "/analyze": "Analyse de complexité uniquement",
            "/health": "Vérification de l'état",
            "/stats": "Statistiques d'utilisation"
        }
    }


@app.get("/health")
async def health_check():
    """Vérification de l'état de l'API"""
    # Tester la connexion aux deux modèles
    tfidf_status = "unknown"
    transformer_status = "unknown"
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Test TF-IDF
        try:
            response = await client.get("http://tfidf-svm:8000/health")
            tfidf_status = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception as e:
            tfidf_status = f"unreachable: {str(e)}"
        
        # Test Transformer
        try:
            response = await client.get("http://callcenter:8000/health")
            transformer_status = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception as e:
            transformer_status = f"unreachable: {str(e)}"
    
    return {
        "status": "healthy",
        "agent": "operational",
        "models": {
            "tfidf": tfidf_status,
            "transformer": transformer_status
        },
        "threshold": COMPLEXITY_THRESHOLD
    }


@app.post("/analyze")
async def analyze_complexity(request: TextRequest):
    """
    Analyse la complexité d'un texte sans faire de prédiction
    """
    try:
        # Analyser la complexité
        routing_result = agent.route(request.text)
        
        # Déterminer quel modèle serait utilisé
        complexity_score = routing_result['complexity_score']
        recommended_model = "tfidf" if complexity_score < COMPLEXITY_THRESHOLD else "transformer"
        
        return {
            "text": request.text[:100] + "..." if len(request.text) > 100 else request.text,
            "complexity_score": complexity_score,
            "complexity_level": routing_result['complexity_level'],
            "recommended_model": recommended_model,
            "details": routing_result['details'],
            "reasoning": routing_result['reasoning']
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse: {str(e)}")


@app.post("/predict", response_model=PredictionResponse)
async def predict_with_routing(request: TextRequest):
    """
    Prédit la catégorie d'un ticket en choisissant automatiquement le meilleur modèle
    selon la complexité du texte
    """
    try:
        # 1. Analyser la complexité
        routing_result = agent.route(request.text)
        complexity_score = routing_result['complexity_score']
        
        # 2. Déterminer le modèle à utiliser
        if request.force_model:
            # Si un modèle est forcé
            model_to_use = request.force_model.lower()
            logger.info(f"Modèle forcé: {model_to_use}")
        else:
            # Routage intelligent basé sur la complexité
            model_to_use = "tfidf" if complexity_score < COMPLEXITY_THRESHOLD else "transformer"
            logger.info(f"Routage automatique: complexité={complexity_score} → {model_to_use}")
        
        # 3. Appeler le modèle approprié
        prediction_result = await _call_model(model_to_use, request.text)
        
        prediction = prediction_result.get("prediction", prediction_result.get("predicted_category"))
        probabilities = prediction_result.get("probabilities", {})
        
        # 4. Générer une réponse intelligente avec Grok
        generated_response = await generate_grok_response(
            input_text=request.text,
            prediction=prediction,
            probabilities=probabilities,
            model_used=model_to_use,
            complexity_score=complexity_score,
            complexity_level=routing_result['complexity_level']
        )
        
        # 5. Construire la réponse complète
        response = {
            "input": request.text,
            "prediction": prediction,
            "probabilities": probabilities,
            "model_used": model_to_use,
            "complexity_analysis": {
                "score": complexity_score,
                "level": routing_result['complexity_level'],
                "details": routing_result['details']
            },
            "reasoning": routing_result['reasoning'] + f" → Modèle utilisé: {model_to_use.upper()}",
            "generated_response": generated_response
        }
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")


async def _call_model(model_name: str, text: str) -> Dict:
    """
    Appelle l'API du modèle spécifié et normalise la réponse

    Retourne un dict standardisé avec au minimum:
      - prediction: str
      - probabilities: Dict[str, float]
      - raw: la réponse brute (si besoin)
    """
    # Choisir l'URL appropriée
    if model_name == "tfidf":
        url = TFIDF_API_URL
        payload = {"text": text}
    elif model_name == "transformer":
        url = TRANSFORMER_API_URL
        payload = {"text": text}
    else:
        raise HTTPException(status_code=400, detail=f"Modèle inconnu: {model_name}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            # Normaliser selon la source
            if model_name == "tfidf":
                # tfidf API renvoie: {input, prediction, probabilities}
                return {
                    "prediction": data.get("prediction"),
                    "probabilities": data.get("probabilities", {}),
                    "raw": data
                }
            else:
                # transformer API (callcenter) renvoie: {text, predicted_category, confidence, all_predictions}
                return {
                    "prediction": data.get("predicted_category") or data.get("prediction"),
                    "probabilities": data.get("all_predictions") or data.get("probabilities") or {},
                    "confidence": data.get("confidence"),
                    "raw": data
                }

        except httpx.TimeoutException:
            logger.error(f"Timeout lors de l'appel à {model_name}")
            raise HTTPException(status_code=504, detail=f"Le modèle {model_name} n'a pas répondu à temps")

        except httpx.HTTPStatusError as e:
            body = e.response.text if e.response is not None else str(e)
            logger.error(f"Erreur HTTP {e.response.status_code} du modèle {model_name}: {body}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Erreur du modèle {model_name}: {body}")

        except Exception as e:
            logger.error(f"Erreur lors de l'appel à {model_name}: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Le modèle {model_name} est inaccessible: {str(e)}")


@app.get("/stats")
async def get_statistics():
    """
    Retourne les statistiques d'utilisation de l'agent
    """
    stats = agent.get_stats()
    return {
        "statistics": stats,
        "configuration": {
            "complexity_threshold": COMPLEXITY_THRESHOLD,
            "routing_strategy": "TF-IDF (< 50) / Transformer (≥ 50)"
        }
    }


@app.post("/config/threshold")
async def update_threshold(new_threshold: int):
    """
    Met à jour le seuil de complexité pour le routage
    
    Args:
        new_threshold: Nouveau seuil (0-100)
    """
    global COMPLEXITY_THRESHOLD
    
    if not 0 <= new_threshold <= 100:
        raise HTTPException(
            status_code=400,
            detail="Le seuil doit être entre 0 et 100"
        )
    
    old_threshold = COMPLEXITY_THRESHOLD
    COMPLEXITY_THRESHOLD = new_threshold
    
    return {
        "message": "Seuil mis à jour",
        "old_threshold": old_threshold,
        "new_threshold": new_threshold,
        "routing_strategy": f"TF-IDF (< {new_threshold}) / Transformer (≥ {new_threshold})"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
