
FROM python:3.10-slim-bullseye

# Installation de LibreOffice et des dépendances UNO
RUN apt-get update && apt-get install -y \
    libreoffice-writer libreoffice-calc libreoffice-impress \
    libreoffice-pyuno python3-uno && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Lancer OpenOffice en headless et démarrer l'app
CMD soffice --headless --accept="socket,host=localhost,port=2002;urp;" & uvicorn backend.main:app --host 0.0.0.0 --port 8000
