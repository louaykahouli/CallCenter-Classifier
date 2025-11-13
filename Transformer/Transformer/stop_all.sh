#!/bin/bash

################################################################################
# Script d'arrêt pour CallCenterAI
# Arrête l'API FastAPI et MLflow UI
################################################################################

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Arrêt des services CallCenterAI...${NC}"
echo ""

# Arrêter via les PIDs sauvegardés
if [ -f ".api.pid" ]; then
    API_PID=$(cat .api.pid)
    if kill -0 $API_PID 2>/dev/null; then
        echo -e "${YELLOW}   Arrêt de l'API (PID: $API_PID)...${NC}"
        kill $API_PID
        echo -e "${GREEN}   ✅ API arrêtée${NC}"
    fi
    rm -f .api.pid
fi

if [ -f ".mlflow.pid" ]; then
    MLFLOW_PID=$(cat .mlflow.pid)
    if kill -0 $MLFLOW_PID 2>/dev/null; then
        echo -e "${YELLOW}   Arrêt de MLflow (PID: $MLFLOW_PID)...${NC}"
        kill $MLFLOW_PID
        echo -e "${GREEN}   ✅ MLflow arrêté${NC}"
    fi
    rm -f .mlflow.pid
fi

# Arrêter par nom de processus (au cas où)
pkill -f "uvicorn api.main:app" 2>/dev/null && echo -e "${GREEN}   ✅ Processus API arrêté${NC}"
pkill -f "mlflow ui" 2>/dev/null && echo -e "${GREEN}   ✅ Processus MLflow arrêté${NC}"

echo ""
echo -e "${GREEN}✅ Tous les services ont été arrêtés${NC}"
