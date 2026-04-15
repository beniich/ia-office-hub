#!/bin/bash

# ─── Script de Déploiement Industriel : IA Office Hub ──────────
# Auteur : Antigravity AI
# Usage : ./deploy.sh [prod|dev]

set -e # Arrête le script en cas d'erreur

MODE=${1:-prod}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🚀 Démarrage du déploiement IA Office Hub (MODE: $MODE)"

# 1. Vérification des dépendances locales
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Erreur : docker-compose n'est pas installé."
    exit 1
fi

# 2. Build du Frontend (Vite)
echo "📦 Build du Frontend Lit..."
cd "$PROJECT_ROOT/frontend"
npm install
npm run build

# 3. Préparation de l'environnement Docker
echo "🐳 Préparation des conteneurs..."
cd "$PROJECT_ROOT/infra/docker"

# Nettoyage optionnel des anciens volumes en prod? (Prudence ici)
# docker-compose down --remove-orphans

# 4. Lancement des services
echo "⚡ Démarrage des services [Backend + Apache]..."
docker-compose build
docker-compose up -d

# 5. Vérification de la santé (Health Check)
echo "🔍 Vérification du statut..."
sleep 5
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/v1/health || echo "Failed")

if [ "$STATUS" == "200" ]; then
    echo "✅ IA Office Hub est opérationnel !"
    echo "🔗 Accès : http://localhost"
else
    echo "⚠️ Attention : Le backend ne répond pas encore (Status: $STATUS)."
    echo "Logs du backend :"
    docker-compose logs backend --tail 20
fi

echo "🏁 Déploiement terminé."
