# Utiliser une image Python officielle légère
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Variables d'environnement pour optimiser Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements
COPY Transformer/requirements.txt .

# Installer les dépendances Python (version CPU de PyTorch pour réduire la taille)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copier seulement le code nécessaire (pas .venv, models, mlruns)
COPY Transformer/api/ /app/api/
COPY Transformer/src/ /app/src/
COPY Transformer/tests/ /app/tests/
COPY Transformer/params.yaml /app/

# Créer les dossiers nécessaires
RUN mkdir -p /app/mlruns /app/data/processed /app/data/raw

# Exposer les ports
EXPOSE 8000 5000

# Script de démarrage
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Point d'entrée
ENTRYPOINT ["/docker-entrypoint.sh"]

# Commande par défaut : lancer l'API
CMD ["api"]
