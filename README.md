# mobilachat

# 🆓 Free Mobile - Chatbot SAV Intelligent

**Plateforme complète de support client avec IA, RAG et intégration Mastodon**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Vue d'ensemble

MobiliaChat est un chatbot intelligent pour le support client Free Mobile, intégrant :
- **RAG (Retrieval-Augmented Generation)** pour des réponses précises
- **Surveillance Mastodon** pour détecter les réclamations
- **Système de ticketing** automatisé
- **Analytics** en temps réel
- **Support multi-base de données** (PostgreSQL local + Supabase cloud)

## ✨ Fonctionnalités

### 🤖 Chatbot Intelligent
- **RAG (Retrieval-Augmented Generation)** : Réponses basées sur la documentation Free Mobile
- **Détection d'intention** : Classification automatique des demandes
- **Analyse de sentiment** : Détection des réclamations et urgences
- **Escalade intelligente** : Transfert automatique vers agents humains si nécessaire
- **Multi-sources** : Support web, Mastodon, et autres canaux

### 🐘 Intégration Mastodon
- **Surveillance temps réel** des hashtags #Free, #FreeMobile, #SAVFree
- **Détection automatique** des réclamations
- **Génération de liens** de contact uniques
- **Réponses automatiques** publiques

### 📊 Analytics & Monitoring
- **Dashboard temps réel** avec KPIs clés
- **Graphiques interactifs** (conversations, tickets, satisfaction)
- **Analyse des intentions** et catégorisation
- **Métriques de performance** (temps de réponse, taux de résolution)
- **Rapports exportables** en CSV/PDF

### 🎫 Système de Ticketing
- **Création automatique** lors d'escalades
- **Priorisation intelligente** (LOW, MEDIUM, HIGH, URGENT)
- **Assignation** aux agents disponibles
- **Suivi complet** de l'état des tickets

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    UTILISATEURS                              │
│  (Web Browser, Mastodon, Mobile App)                        │
└────────────────┬────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (Streamlit)                            │
│  - Interface utilisateur                                     │
│  - Formulaire de contact                                     │
│  - Chat widget                                              │
│  - Dashboard analytics                                       │
└────────────────┬────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND API (FastAPI)                           │
│  - Gestion des conversations                                 │
│  - Gestion des tickets                                       │
│  - Authentification                                          │
│  - Analytics                                                 │
└───────┬──────────────┬──────────────┬───────────────────────┘
│              │              │
▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌────────────────┐
│  PostgreSQL  │ │  Redis   │ │  AI Engine     │
│  / Supabase  │ │  Cache   │ │  (RAG + LLM)   │
└──────────────┘ └──────────┘ └────────┬───────┘
│
▼
┌───────────────┐
│   ChromaDB    │
│ Vector Store  │
└───────────────┘
┌─────────────────────────────────────────────────────────────┐
│           SOCIAL MONITOR (Mastodon)                          │
│  - Surveillance hashtags                                     │
│  - Détection réclamations                                    │
│  - Génération liens                                          │
│  - Réponses automatiques                                     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prérequis
- **Python 3.10+**
- **Docker & Docker Compose**
- **Git**

### Installation Rapide

```bash
# 1. Cloner le repository
git clone https://github.com/votre-username/chatbot-free-mobile.git
cd chatbot-free-mobile

# 2. Exécuter le script de configuration
./scripts/setup_dev.sh

# 3. Copier et configurer .env
cp .env.example .env
# Éditez .env avec vos paramètres

# 4. Initialiser la base de données
python scripts/init_database.py local

# 5. Préparer les datasets
python data/scripts/prepare_dataset.py

# 6. Charger les données dans ChromaDB
python data/scripts/load_to_vectorstore.py

# 7. Lancer l'application avec Docker
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

## 📖 Utilisation

1. **Accédez à l'application** : http://localhost:8501
2. **Remplissez le formulaire** de contact avec vos informations
3. **Posez vos questions** au chatbot
4. **Consultez les analytics** dans le dashboard
5. **Gérez les tickets** depuis l'interface

## 🔧 Configuration

### Variables d'Environnement

```bash
# Base de données
POSTGRES_LOCAL_HOST=localhost
POSTGRES_LOCAL_USER=chatbot_user
POSTGRES_LOCAL_PASSWORD=your_password
POSTGRES_LOCAL_DB=chatbot_free_mobile

# Mastodon
MASTODON_INSTANCE_URL=https://mastodon.social
MASTODON_CLIENT_ID=your_client_id
MASTODON_CLIENT_SECRET=your_client_secret
MASTODON_ACCESS_TOKEN=your_access_token

# IA
LLM_MODEL_NAME=microsoft/DialoGPT-medium
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_STORE_PATH=./data/vector_store

# Sécurité
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
```

## 🧪 Tests

```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=apps

# Tests unitaires seulement
pytest tests/unit/

# Tests d'intégration
pytest tests/integration/
```

## 📊 Monitoring

```bash
# Statut des services
docker-compose -f infrastructure/docker/docker-compose.yml ps

# Logs en temps réel
docker-compose -f infrastructure/docker/docker-compose.yml logs -f

# Métriques de performance
curl http://localhost:8000/api/analytics
```

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

- **Documentation** : [docs/](docs/)
- **Issues** : [GitHub Issues](https://github.com/votre-username/chatbot-free-mobile/issues)
- **Discussions** : [GitHub Discussions](https://github.com/votre-username/chatbot-free-mobile/discussions)

## 🙏 Remerciements

- [FastAPI](https://fastapi.tiangolo.com/) pour l'API backend
- [Streamlit](https://streamlit.io/) pour l'interface utilisateur
- [ChromaDB](https://www.trychroma.com/) pour la base vectorielle
- [Hugging Face](https://huggingface.co/) pour les modèles IA
- [Supabase](https://supabase.com/) pour l'infrastructure cloud


