# Dockerfile pour l'Agent IA Intelligent
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code de l'agent
COPY *.py .

# Créer le dossier pour la base de données
RUN mkdir -p /app/data

EXPOSE 8002

# Lancer l'API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8002"]
