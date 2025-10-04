# Configuration des Secrets GitHub

## Secrets requis pour le repository

Pour que l'application fonctionne correctement, vous devez configurer les secrets suivants dans GitHub :

### 1. Aller dans les paramètres du repository
1. Allez sur https://github.com/Archimed-Anderson/mobilachat
2. Cliquez sur **Settings**
3. Dans le menu de gauche, cliquez sur **Secrets and variables** → **Actions**

### 2. Ajouter les secrets suivants

#### Base de données PostgreSQL
- `POSTGRES_USER` = `chatbot_user`
- `POSTGRES_PASSWORD` = `Adan@20102016`
- `POSTGRES_SERVER` = `localhost`
- `POSTGRES_PORT` = `5432`
- `POSTGRES_DB` = `chatbot_free_mobile`

#### Supabase
- `SUPABASE_URL` = `https://dgyjxlckgzuluxgnwnnz.supabase.co`
- `SUPABASE_ANON_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRneWp4bGNrZ3p1bHV4Z253bm56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NzkwNDksImV4cCI6MjA3NTE1NTA0OX0.Me_NIxx8rZR7459G5h2E2aWeoUipRo9gFYeRnuRvb64`
- `SUPABASE_SERVICE_KEY` = `sb_secret_opVHouTwBbv1mF8kq3PM6w_YSMsMDiS`

#### Mastodon
- `MASTODON_INSTANCE_URL` = `https://mastodon.social`
- `MASTODON_CLIENT_ID` = `_KU2v_HHfbryK3G4OHEZFemWRaFXwSb2W9dvraZ7m54`
- `MASTODON_CLIENT_SECRET` = `ItxCYDtILkNdMcAEFaln4hBUWa-bYrOibIWxqlrBh5w`
- `MASTODON_ACCESS_TOKEN` = `QKoEtaWSFuZvPrxK4z7381x1rrS_7IFAfQH_P1Bt4Y`

#### Redis
- `REDIS_URL` = `redis://localhost:6379`

#### Sécurité
- `SECRET_KEY` = `votre-secret-key-super-securise-min-32-caracteres`
- `JWT_ALGORITHM` = `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES` = `30`

#### IA
- `LLM_MODEL_NAME` = `microsoft/DialoGPT-medium`
- `EMBEDDING_MODEL` = `sentence-transformers/all-MiniLM-L6-v2`

### 3. Comment ajouter un secret
1. Cliquez sur **New repository secret**
2. Entrez le nom du secret (ex: `POSTGRES_PASSWORD`)
3. Entrez la valeur du secret
4. Cliquez sur **Add secret**

## Variables d'environnement pour le développement local

Créez un fichier `.env` à la racine du projet avec ces valeurs :

```bash
# Base de données PostgreSQL
POSTGRES_USER=chatbot_user
POSTGRES_PASSWORD=Adan@20102016
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=chatbot_free_mobile

# Supabase
SUPABASE_URL=https://dgyjxlckgzuluxgnwnnz.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRneWp4bGNrZ3p1bHV4Z253bm56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NzkwNDksImV4cCI6MjA3NTE1NTA0OX0.Me_NIxx8rZR7459G5h2E2aWeoUipRo9gFYeRnuRvb64
SUPABASE_SERVICE_KEY=sb_secret_opVHouTwBbv1mF8kq3PM6w_YSMsMDiS

# Mastodon
MASTODON_INSTANCE_URL=https://mastodon.social
MASTODON_CLIENT_ID=_KU2v_HHfbryK3G4OHEZFemWRaFXwSb2W9dvraZ7m54
MASTODON_CLIENT_SECRET=ItxCYDtILkNdMcAEFaln4hBUWa-bYrOibIWxqlrBh5w
MASTODON_ACCESS_TOKEN=QKoEtaWSFuZvPrxK4z7381x1rrS_7IFAfQH_P1Bt4Y

# Redis
REDIS_URL=redis://localhost:6379

# Sécurité
SECRET_KEY=votre-secret-key-super-securise-min-32-caracteres
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# IA
LLM_MODEL_NAME=microsoft/DialoGPT-medium
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```
