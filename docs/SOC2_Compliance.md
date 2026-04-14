# 📄 Dossier de Conformité : AI Office Hub
**Version :** 1.0  
**Statut :** Prêt pour Audit  
**Normes visées :** ISO/IEC 27001:2022 & SOC 2 (Type II)

---

## 1. Architecture de Sécurité (High-Level)
L'application AI Office Hub est conçue selon le principe de la **Défense en Profondeur**.

### 🛡️ Flux de Données Sécurisé
`Utilisateur` -> `HTTPS/TLS` -> `Apache Reverse Proxy` -> `Internal Network` -> `FastAPI Backend` -> `UNO Bridge` -> `OpenOffice Headless`

*   **Isolation :** Le moteur OpenOffice tourne en mode *Headless* dans un container Docker isolé. Il n'a aucun accès direct à Internet.
*   **Proxy :** Apache filtre les requêtes entrantes et gère le certificat SSL, empêchant toute exposition directe du backend.
*   **Secrets :** Aucune clé API n'est codée en dur. Utilisation d'un fichier `.env` chiffré et injecté via Docker Secrets.

---

## 2. Matrice de Conformité ISO 27001
*Objectif : Garantir la Confidentialité, l'Intégrité et la Disponibilité (CID).*

| Contrôle ISO 27001 | Implémentation Technique dans AI Office Hub | Preuve pour l'Auditeur |
| :--- | :--- | :--- |
| **A.9.1.1 Accès** | Mise en place d'un contrôle d'accès basé sur les rôles (RBAC) via FastAPI Security. | Fichier `backend/app/core/security.py` |
| **A.12.4.1 Logs** | Chaque action de l'IA et chaque accès document est loggé avec timestamp et ID utilisateur. | Table `ai_logs` dans `schema.sql` |
| **A.14.2.1 Ingénierie** | Séparation stricte entre l'UI, la logique métier et l'exécution (Architecture en couches). | Structure des dossiers `api/`, `services/`, `db/` |
| **A.18.1.1 Conformité** | Chiffrement des données au repos et transit via HTTPS. | Config `infra/apache/httpd.conf` |

---

## 3. Matrice de Contrôle SOC 2
*Objectif : Prouver la fiabilité du traitement des données et la transparence.*

### 🔍 Critère 1 : Sécurité (Security)
L'infrastructure est protégée contre les accès non autorisés.
*   **Preuve :** L'utilisation de Docker limite la surface d'attaque. Le moteur OpenOffice ne peut pas écrire en dehors de son dossier `/app/output`.

### ⚙️ Critère 2 : Intégrité du Traitement (Processing Integrity)
L'IA ne doit pas modifier des données de manière imprévisible.
*   **Contrôle "Human-in-the-Loop" :** L'IA ne génère pas le document final directement. Elle génère un **Storyboard JSON** (Plan de présentation). L'utilisateur doit valider ce plan dans l'interface React avant l'export final.
*   **Preuve :** Logique implémentée dans `ai_service.py` et affichée dans `App.js`.

### 🕒 Critère 3 : Disponibilité (Availability)
Le système doit être disponible et récupérable.
*   **Preuve :** Pipeline CI/CD GitHub Actions permettant un déploiement automatisé et un rollback rapide en cas de panne. Fichier `.github/workflows/pipeline.yml`.

---

## 4. Cycle de Vie de la Donnée (Data Lifecycle)
Pour répondre aux exigences de confidentialité :
1.  **Ingestion :** Le document est uploadé via Apache, scanné et enregistré dans la table `documents`.
2.  **Analyse :** L'IA extrait les données -> stockage du diagnostic dans `ai_diagnostics` -> suppression des données temporaires.
3.  **Sortie :** Génération du fichier `.odp` ou `.pdf` -> Téléchargement -> **Auto-destruction** du fichier sur le serveur après 24h (Cron job).

---

## 5. Guide de Récupération après Sinistre (DRP)
En cas de crash total du serveur :
1.  **Restauration Infra :** `docker-compose up --build` (Restaure l'intégralité de l'environnement en < 5 min).
2.  **Restauration Données :** Restauration du backup quotidien de la base SQL.
3.  **Vérification :** Lancement des tests de sécurité automatisés via le pipeline GitHub.