#!/bin/bash
# start_oo_headless.sh
# Lance LibreOffice en mode headless pour accepter les connexions PyUNO
# SOC 2 : Le processus est isolé dans un container Docker dédié

echo "[INFO] Démarrage LibreOffice Headless sur le port 2002..."

soffice \
  --headless \
  --norestore \
  --nofirststartwizard \
  --accept="socket,host=localhost,port=2002,tcpNoDelay=1;urp;StarOffice.ServiceManager" &

LIBREOFFICE_PID=$!
echo "[INFO] LibreOffice démarré (PID: $LIBREOFFICE_PID)"
echo "[INFO] Socket ouvert sur localhost:2002"

# Attente que le socket soit prêt avant de lancer l'API FastAPI
sleep 3

echo "[INFO] Démarrage de l'API FastAPI..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000