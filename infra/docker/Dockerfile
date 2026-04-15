# ─── Dockerfile Production : IA Office Hub ────────────────────
# Image de base légère avec Python
FROM python:3.10-slim-bullseye

# Évite la création de fichiers .pyc et active le flushing des logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installation de LibreOffice et des dépendances UNO (SOC 2 Compliant)
RUN apt-get update && apt-get install -y \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    libreoffice-pyuno \
    python3-uno \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation des dépendances Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des dossiers pour les logs et uploads avec permissions restreintes
RUN mkdir -p /app/logs /app/uploads /app/output && \
    chmod -R 755 /app/logs /app/uploads /app/output

# Exposition du port API
EXPOSE 8000

# Script d'entrée pour lancer LibreOffice Headless + Gunicorn
# On utilise Gunicorn avec le worker Uvicorn pour la robustesse en prod.
CMD soffice --headless --accept="socket,host=0.0.0.0,port=2002;urp;" --nodefault --nofirststartwizard & \
    gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
