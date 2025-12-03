"""
API pour l'Agent IA Intelligent
Route les requêtes vers TF-IDF ou Transformer selon la complexité
Utilise Grok pour générer des réponses intelligentes
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import httpx
import logging
import os
import time
import uuid
from typing import Dict, Optional
from intelligent_agent import IntelligentAgent
from cache_manager import CacheManager, ConversationStore
from prometheus_fastapi_instrumentator import Instrumentator

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clé API Grok depuis les variables d'environnement
GROK_API_KEY = os.getenv("GROK_API_KEY", "xai-EyqPqZvWyTu8mnQiFCFyYPVuAYdNxPnnjw4z9onvzqrZ5wAjcNkJqWwKx4uc7tY5d68c1njQyeDgJwKx")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
USE_GROK = os.getenv("USE_GROK", "true").lower() == "true"

# Configuration du cache
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 heure par défaut
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Agent IA Intelligent",
    description="Router intelligent qui choisit le meilleur modèle selon la complexité du texte",
    version="2.0.0"
)

instrumentator = Instrumentator(
    should_group_status_codes=True,  # groups status codes into 2xx/4xx/5xx
    should_instrument_requests_inprogress=True
)
instrumentator.instrument(app).expose(app, endpoint="/metrics")

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

# Initialisation du cache et du stockage
cache_manager = CacheManager(cache_ttl=CACHE_TTL)
conversation_store = ConversationStore(db_path="/app/data/conversations.db")

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


async def generate_conversation_title(input_text: str, prediction: str) -> str:
    """
    Génère un titre court et significatif pour la conversation avec Grok
    
    Args:
        input_text: Le premier message de la conversation
        prediction: La catégorie prédite
        
    Returns:
        Un titre court (max 50 caractères)
    """
    if not USE_GROK or not GROK_API_KEY:
        # Fallback : utiliser les 50 premiers caractères
        title = input_text[:47] + '...' if len(input_text) > 50 else input_text
        return title.capitalize()
    
    try:
        # Créer le prompt pour Grok
        prompt = f"""Génère un titre court et descriptif (maximum 40 caractères) pour cette conversation :

MESSAGE: "{input_text}"
CATÉGORIE: {prediction}

Le titre doit :
- Être court et explicite (max 40 caractères)
- Résumer l'essentiel de la demande
- Ne pas inclure d'émoji (sera ajouté automatiquement)
- Commencer par une majuscule

Réponds UNIQUEMENT avec le titre, rien d'autre."""

        # Appeler l'API Grok
        async with httpx.AsyncClient(timeout=10.0) as client:
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
                            "content": "Tu génères des titres courts et descriptifs pour des conversations. Réponds uniquement avec le titre, sans guillemets ni ponctuation finale."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "grok-beta",
                    "stream": False,
                    "temperature": 0.5,
                    "max_tokens": 20
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                title = result['choices'][0]['message']['content'].strip()
                # Nettoyer les guillemets si présents
                title = title.strip('"').strip("'").strip()
                # Limiter à 50 caractères
                if len(title) > 50:
                    title = title[:47] + "..."
                logger.info(f"Titre Grok généré: {title}")
                return title
            else:
                logger.error(f"Erreur API Grok pour titre: {response.status_code}")
                # Fallback
                title = input_text[:47] + '...' if len(input_text) > 50 else input_text
                return title.capitalize()
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération du titre: {str(e)}")
        # Fallback
        title = input_text[:47] + '...' if len(input_text) > 50 else input_text
        return title.capitalize()


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
    session_id: Optional[str] = None  # ID de session pour le tracking
    conversation_title: Optional[str] = None  # Titre descriptif de la conversation
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        """Valider que le texte n'est pas vide"""
        if not v or not v.strip():
            raise ValueError('Le texte ne peut pas être vide')
        return v


class PredictionResponse(BaseModel):
    """Schéma de la réponse"""
    input: str
    prediction: str
    probabilities: Dict[str, float]
    model_used: str
    complexity_analysis: Dict
    reasoning: str
    generated_response: str
    session_id: str
    cache_hit: bool = False  # Indique si la réponse vient du cache
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
    selon la complexité du texte. Utilise le cache pour améliorer les performances.
    """
    start_time = time.time()
    cache_hit = False
    
    # Générer ou utiliser le session_id
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # 1. Vérifier le cache si activé
        if CACHE_ENABLED and not request.force_model:
            cached_result = cache_manager.get(request.text)
            if cached_result:
                logger.info(f"✅ Cache HIT pour session {session_id[:8]}...")
                cached_result['session_id'] = session_id
                cached_result['cache_hit'] = True
                
                # Sauvegarder quand même la conversation en DB (pour l'historique)
                try:
                    # Générer un titre si c'est une nouvelle session
                    conversation_title = request.conversation_title
                    if not conversation_title or conversation_title.strip() == "":
                        if len(request.text) > 40:
                            conversation_title = request.text[:37] + "..."
                        else:
                            conversation_title = request.text
                        conversation_title = conversation_title.capitalize()
                    
                    conversation_store.save_conversation(
                        session_id=session_id,
                        input_text=request.text,
                        prediction=cached_result['prediction'],
                        model_used=cached_result['model_used'],
                        complexity_score=cached_result['complexity_analysis']['score'],
                        complexity_level=cached_result['complexity_analysis']['level'],
                        probabilities=cached_result['probabilities'],
                        response_time=0.0,  # Temps de réponse du cache négligeable
                        generated_response=cached_result['generated_response'],
                        conversation_title=conversation_title
                    )
                    logger.info(f"💾 Conversation sauvegardée (cache hit)")
                except Exception as db_error:
                    logger.error(f"Erreur DB lors du cache hit: {db_error}")
                
                return cached_result
        
        # 2. Analyser la complexité
        routing_result = agent.route(request.text)
        complexity_score = routing_result['complexity_score']
        
        # 3. Déterminer le modèle à utiliser
        if request.force_model:
            # Si un modèle est forcé
            model_to_use = request.force_model.lower()
            logger.info(f"Modèle forcé: {model_to_use}")
        else:
            # Routage intelligent basé sur la complexité
            model_to_use = "tfidf" if complexity_score < COMPLEXITY_THRESHOLD else "transformer"
            logger.info(f"Routage automatique: complexité={complexity_score} → {model_to_use}")
        
        # 4. Appeler le modèle approprié
        prediction_result = await _call_model(model_to_use, request.text)
        
        prediction = prediction_result.get("prediction", prediction_result.get("predicted_category"))
        probabilities = prediction_result.get("probabilities", {})
        
        # 5. Générer une réponse intelligente avec Grok
        generated_response = await generate_grok_response(
            input_text=request.text,
            prediction=prediction,
            probabilities=probabilities,
            model_used=model_to_use,
            complexity_score=complexity_score,
            complexity_level=routing_result['complexity_level']
        )
        
        # 5.5. Générer un titre intelligent si pas fourni et c'est une nouvelle conversation
        conversation_title = request.conversation_title
        if not conversation_title or conversation_title.strip() == "":
            # Générer un titre simple mais descriptif (sans appeler Grok pour éviter les erreurs)
            # Format: résumé du texte + catégorie
            if len(request.text) > 40:
                conversation_title = request.text[:37] + "..."
            else:
                conversation_title = request.text
            # Capitaliser la première lettre
            conversation_title = conversation_title.capitalize()
            logger.info(f"📝 Titre généré: {conversation_title}")
        else:
            logger.info(f"📝 Titre fourni: {conversation_title}")
        
        # 6. Calculer le temps de réponse
        response_time = time.time() - start_time
        
        # 7. Construire la réponse complète
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
            "generated_response": generated_response,
            "session_id": session_id,
            "cache_hit": False
        }
        
        # 8. Sauvegarder dans le cache (seulement si pas forcé)
        if CACHE_ENABLED and not request.force_model:
            cache_manager.set(request.text, response)
            logger.info(f"💾 Réponse mise en cache")
        
        # 9. Sauvegarder la conversation dans la base de données
        try:
            conversation_store.save_conversation(
                session_id=session_id,
                input_text=request.text,
                prediction=prediction,
                model_used=model_to_use,
                complexity_score=complexity_score,
                complexity_level=routing_result['complexity_level'],
                probabilities=probabilities,
                response_time=response_time,
                generated_response=generated_response,
                conversation_title=conversation_title  # Titre généré ou fourni
            )
        except Exception as db_error:
            logger.error(f"Erreur lors de la sauvegarde en DB: {db_error}")
            # Ne pas faire échouer la requête si la DB pose problème
        
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
    Retourne les statistiques d'utilisation de l'agent incluant cache et conversations
    """
    stats = agent.get_stats()
    cache_stats = cache_manager.get_stats()
    db_stats = conversation_store.get_global_stats(days=7)
    
    return {
        "agent_statistics": stats,
        "cache_statistics": cache_stats,
        "conversation_statistics": db_stats,
        "configuration": {
            "complexity_threshold": COMPLEXITY_THRESHOLD,
            "cache_enabled": CACHE_ENABLED,
            "cache_ttl": CACHE_TTL,
            "routing_strategy": f"TF-IDF (< {COMPLEXITY_THRESHOLD}) / Transformer (≥ {COMPLEXITY_THRESHOLD})"
        }
    }


@app.get("/history/{session_id}")
async def get_session_history(session_id: str, limit: int = 50):
    """
    Récupère l'historique des conversations d'une session
    
    Args:
        session_id: ID de la session
        limit: Nombre maximum de conversations à retourner
    """
    try:
        history = conversation_store.get_session_history(session_id, limit)
        return {
            "session_id": session_id,
            "count": len(history),
            "conversations": history
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cache/clear")
async def clear_cache():
    """
    Vide complètement le cache
    """
    try:
        count = cache_manager.clear()
        return {
            "message": "Cache vidé avec succès",
            "entries_cleared": count
        }
    except Exception as e:
        logger.error(f"Erreur lors du vidage du cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cache/cleanup")
async def cleanup_cache():
    """
    Nettoie les entrées expirées du cache
    """
    try:
        count = cache_manager.cleanup_expired()
        return {
            "message": "Nettoyage effectué",
            "entries_removed": count
        }
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage du cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cache/stats")
async def get_cache_stats():
    """
    Récupère les statistiques détaillées du cache
    """
    try:
        stats = cache_manager.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats du cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
