# 🔒 Politique de Sécurité de l'Information (ISO 27001)
**AI Office Hub - Système de Management de la Sécurité de l'Information (SMSI)**

## 1. Objectif de la Politique
L'objectif de cette politique est de protéger les informations de l'organisation et de ses clients contre toute menace, qu'elle soit interne ou externe, délibérée ou accidentelle.
AI Office Hub traite des données financières sensibles ; leur confidentialité, intégrité et disponibilité doivent être assurées selon les exigences de la norme ISO/IEC 27001:2022.

## 2. Classification des Données (A.8.2)
Toutes les données transitant par l'application sont classées selon leur niveau de sensibilité :
- **Strictement Confidentiel :** Fichiers `.ods` et `.odp` contenant des données financières, Variables d'environnement (`.env`), clés de chiffrement AES.
- **Usage Interne :** Structure de la base de données, code source backend et frontend.
- **Public :** Documentation utilisateur, interfaces publiques sans données.

## 3. Chiffrement et Cryptographie (A.10.1.1)
- **Données au repos :** Tous les documents stockés par les utilisateurs sont chiffrés sur le disque en utilisant AES-256 (via la librairie Python `cryptography.fernet`). La clé de chiffrement est stockée hors du code source.
- **Données en transit :** Toutes les communications entre le réseau frontend et l'API backend sont encapsulées dans TLS 1.3 via le terminateur de sécurité (Apache Reverse Proxy).

## 4. Politique de Contrôle d'Accès (A.9)
L'accès aux API et aux documents est géré par un mécanisme RBAC (Role-Based Access Control) couplé à des JSON Web Tokens (JWT).
*   **Admin :** Droit de suppression et d'audit intégral (Read/Write/Delete).
*   **Manager :** Peut lancer l'IA et générer des rapports (Read/Write).
*   **Viewer :** Consultation en lecture seule.
L'authentification est protégée contre le vol d'identifiant et les attaques par force brute (blocage des IPs après 5 échecs consécutifs).

## 5. Sécurité liée aux Fournisseurs (IA) (A.15)
L'utilisation de modèles d'IA externes pour les diagnostics financiers (OpenAI API) suit ces règles :
1.  **Désidentification :** Seules les métriques quantitatives (chiffres et intitulés de postes) sont transmises au LLM. Les Informations Personnelles (PII) doivent être purgées avant l'appel à l'API.
2.  **No Training Clause :** L'entreprise s'assure par contrat commercial (via Enterprise API) que les données envoyées à l'IA ne sont pas utilisées pour l'entraînement des modèles.

## 6. Journalisation et Surveillance (A.12.4)
Toute interaction avec la plateforme, en particulier les actions déclenchant l'intelligence artificielle et l'écriture de documents via OpenOffice, génère un événement dans la table `ai_logs`. Ces journaux sont :
- Immuables (aucune route API pour les supprimer).
- Horodatés (UTC synchronisé via NTP).
- Reliés à un identifiant d'utilisateur unique.

**Validation :** [Signature du CTO]  
**Date d'entrée en vigueur :** 2026-04-14