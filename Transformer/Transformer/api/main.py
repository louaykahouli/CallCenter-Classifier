"""
API FastAPI pour la classification de tickets Call Center
Version Hugging Face - Utilise le modèle déployé sur HF
Avec tracking MLflow intégré
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import json
import os
from typing import List, Dict
import logging
import time
from datetime import datetime
from .config import (
    HF_MODEL_NAME, USE_LOCAL_MODEL, LOCAL_MODEL_PATH, HF_TOKEN, USE_GPU,
    MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME
)

# Import de l'agent intelligent
try:
    # Preferred: import the top-level ia_agent package if available in the environment
    from ia_agent import IntelligentAgent
except Exception:
    # Fallback: try to import legacy local module under Transformer package (src.intelligent_agent)
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from src.intelligent_agent import IntelligentAgent

# Prometheus instrumentation
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration MLflow
try:
    import mlflow
    import mlflow.sklearn
    
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    
    # Créer une run persistante pour l'API
    mlflow.start_run(run_name=f"api_inference_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    MLFLOW_ENABLED = True
    logger.info(f"✅ MLflow activé - URI: {MLFLOW_TRACKING_URI}")
except Exception as e:
    MLFLOW_ENABLED = False
    logger.warning(f"⚠️  MLflow non disponible : {e}")
    logger.info("L'API fonctionnera sans tracking MLflow")

# Initialiser l'app FastAPI
app = FastAPI(
    title="Call Center Ticket Classifier API",
    description="API pour classifier automatiquement les tickets du centre d'appels",
    version="1.0.0"
)

# Ajouter instrumentation Prometheus
if PROMETHEUS_AVAILABLE:
    try:
        instrumentator = Instrumentator(
            should_group_status_codes=True,
            should_instrument_requests_inprogress=True
        )
        instrumentator.instrument(app).expose(app, endpoint="/metrics")
        logger.info("✅ Prometheus instrumentation activée")
    except Exception as e:
        logger.warning(f"⚠️  Prometheus instrumentation échouée: {e}")
else:
    logger.warning("⚠️  prometheus_fastapi_instrumentator non disponible")

# Modèles Pydantic
class TicketRequest(BaseModel):
    """Modèle pour une demande de classification de ticket"""
    text: str
    
    class Config:
        example = {"text": "Mon ordinateur ne démarre plus après la mise à jour"}

class TicketResponse(BaseModel):
    """Modèle pour la réponse de classification"""
    text: str
    predicted_category: str
    confidence: float
    all_predictions: Dict[str, float]

class BatchRequest(BaseModel):
    """Modèle pour traiter plusieurs tickets"""
    tickets: List[str]

class BatchResponse(BaseModel):
    """Modèle pour la réponse batch"""
    results: List[TicketResponse]
    processing_time: float

# Classe pour gérer le modèle
class TicketClassifier:
    def __init__(self, model_name_or_path: str, use_local: bool = False, token: str = None):
        """
        Initialise le classificateur
        
        Args:
            model_name_or_path: Nom du modèle HF (ex: 'username/model') ou chemin local
            use_local: Si True, utilise un modèle local
            token: Token HF (optionnel pour modèles publics)
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() and USE_GPU else 'cpu')
        self.use_local = use_local
        logger.info(f"Utilisation du device : {self.device}")
        
        if use_local:
            # Mode local (ancien comportement)
            logger.info(f"Chargement du modèle LOCAL depuis : {model_name_or_path}")
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path).to(self.device)
            self.model.eval()
            self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
            
            # Charger les mappings des labels
            with open(os.path.join(model_name_or_path, 'label_mappings.json'), 'r') as f:
                mappings = json.load(f)
                self.id2label = {int(k): v for k, v in mappings['id2label'].items()}
        else:
            # Mode Hugging Face (nouveau !)
            logger.info(f"Chargement du modèle depuis HUGGING FACE : {model_name_or_path}")
            
            # Utiliser le pipeline transformers (plus simple !)
            self.pipeline = pipeline(
                "text-classification",
                model=model_name_or_path,
                device=0 if self.device.type == 'cuda' else -1,
                token=token
            )
            
            # Charger aussi le modèle pour avoir les labels
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name_or_path, 
                token=token
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, token=token)
            self.id2label = self.model.config.id2label
        
        logger.info(f"Modèle chargé avec succès !")
        logger.info(f"Classes disponibles : {list(self.id2label.values())}")
    
    def predict(self, text: str) -> Dict:
        """Prédit la catégorie d'un ticket"""
        
        if self.use_local:
            # Mode local (ancien comportement)
            inputs = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
                
                pred_id = probabilities.argmax().item()
                confidence = probabilities.max().item()
                
                all_probs = {
                    self.id2label[i]: float(prob) 
                    for i, prob in enumerate(probabilities[0])
                }
                
                predicted_label = self.id2label[pred_id]
        else:
            # Mode Hugging Face (nouveau !)
            # Utilise le pipeline qui est optimisé
            result = self.pipeline(text, top_k=None)  # top_k=None pour avoir toutes les probas
            
            # Le pipeline retourne une liste de dicts avec 'label' et 'score'
            predicted_label = result[0]['label']
            confidence = result[0]['score']
            
            # Créer le dictionnaire de toutes les probabilités
            all_probs = {item['label']: item['score'] for item in result}
        
        return {
            "predicted_category": predicted_label,
            "confidence": confidence,
            "all_predictions": all_probs
        }

# Initialiser le modèle au démarrage
try:
    if USE_LOCAL_MODEL:
        logger.info(f"Mode LOCAL activé")
        classifier = TicketClassifier(
            model_name_or_path=LOCAL_MODEL_PATH,
            use_local=True
        )
    else:
        logger.info(f"Mode HUGGING FACE activé")
        classifier = TicketClassifier(
            model_name_or_path=HF_MODEL_NAME,
            use_local=False,
            token=HF_TOKEN
        )
    logger.info("✅ Classificateur initialisé avec succès")
except Exception as e:
    logger.error(f"❌ Erreur lors du chargement du modèle : {str(e)}")
    classifier = None

# Routes
@app.get("/", tags=["Health"])
async def root():
    """Route racine - vérification que l'API fonctionne"""
    return {
        "message": "Call Center Ticket Classifier API",
        "status": "running",
        "model_loaded": classifier is not None,
        "model_source": "Hugging Face" if not USE_LOCAL_MODEL else "Local",
        "model_name": HF_MODEL_NAME if not USE_LOCAL_MODEL else "Local Model",
        "mlflow_tracking": MLFLOW_ENABLED
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Vérification de la santé de l'API"""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "status": "healthy",
        "device": str(classifier.device),
        "model_loaded": True,
        "num_classes": len(classifier.id2label),
        "mlflow_enabled": MLFLOW_ENABLED,
        "mlflow_uri": MLFLOW_TRACKING_URI if MLFLOW_ENABLED else None
    }

@app.get("/classes", tags=["Info"])
async def get_classes():
    """Retourne les catégories disponibles"""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "classes": list(classifier.id2label.values()),
        "count": len(classifier.id2label)
    }

@app.post("/classify", response_model=TicketResponse, tags=["Classification"])
async def classify_ticket(request: TicketRequest):
    """Classifie un ticket unique"""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    start_time = time.time()
    
    try:
        prediction = classifier.predict(request.text)
        inference_time = time.time() - start_time
        
        # Tracking MLflow
        if MLFLOW_ENABLED:
            try:
                mlflow.log_metrics({
                    "inference_time": inference_time,
                    "confidence": prediction["confidence"],
                    "predictions_count": 1
                })
                mlflow.log_param("predicted_category", prediction["predicted_category"])
            except Exception as e:
                logger.warning(f"Erreur logging MLflow : {e}")
        
        return TicketResponse(
            text=request.text,
            **prediction
        )
    except Exception as e:
        logger.error(f"Erreur lors de la classification : {str(e)}")
        
        # Log erreur dans MLflow
        if MLFLOW_ENABLED:
            try:
                mlflow.log_metric("errors_count", 1)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify-batch", response_model=BatchResponse, tags=["Classification"])
async def classify_batch(request: BatchRequest):
    """Classifie plusieurs tickets"""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.tickets or len(request.tickets) == 0:
        raise HTTPException(status_code=400, detail="Tickets list cannot be empty")
    
    if len(request.tickets) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 tickets per request")
    
    start_time = time.time()
    
    try:
        results = []
        confidences = []
        categories = {}
        
        for text in request.tickets:
            if text.strip():  # Skip empty tickets
                prediction = classifier.predict(text)
                results.append(TicketResponse(
                    text=text,
                    **prediction
                ))
                
                # Collecter les stats pour MLflow
                confidences.append(prediction["confidence"])
                category = prediction["predicted_category"]
                categories[category] = categories.get(category, 0) + 1
        
        processing_time = time.time() - start_time
        
        # Tracking MLflow pour batch
        if MLFLOW_ENABLED and results:
            try:
                mlflow.log_metrics({
                    "batch_processing_time": processing_time,
                    "batch_size": len(results),
                    "avg_confidence": sum(confidences) / len(confidences),
                    "min_confidence": min(confidences),
                    "max_confidence": max(confidences),
                    "batch_predictions_count": len(results)
                })
                
                # Log distribution des catégories
                for category, count in categories.items():
                    mlflow.log_metric(f"category_{category}_count", count)
                    
            except Exception as e:
                logger.warning(f"Erreur logging MLflow : {e}")
        
        return BatchResponse(
            results=results,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Erreur lors de la classification batch : {str(e)}")
        
        # Log erreur dans MLflow
        if MLFLOW_ENABLED:
            try:
                mlflow.log_metric("batch_errors_count", 1)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pour les stats MLflow
@app.get("/stats", tags=["Monitoring"])
async def get_stats():
    """Retourne les statistiques de l'API"""
    if not MLFLOW_ENABLED:
        return {
            "message": "MLflow non activé",
            "mlflow_enabled": False
        }
    
    try:
        # Récupérer les métriques de la run active
        run = mlflow.active_run()
        if run:
            return {
                "mlflow_enabled": True,
                "run_id": run.info.run_id,
                "experiment_name": MLFLOW_EXPERIMENT_NAME,
                "tracking_uri": MLFLOW_TRACKING_URI,
                "message": f"Consultez MLflow UI : {MLFLOW_TRACKING_URI}"
            }
        else:
            return {
                "mlflow_enabled": True,
                "message": "Aucune run active",
                "tracking_uri": MLFLOW_TRACKING_URI
            }
    except Exception as e:
        return {
            "error": str(e),
            "mlflow_enabled": False
        }

# Gestion des erreurs
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

# Cleanup au shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Fermer proprement MLflow au shutdown"""
    if MLFLOW_ENABLED:
        try:
            mlflow.end_run()
            logger.info("✅ MLflow run terminée proprement")
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )