# 1. Image de base
FROM python:3.10-slim

# 2. Variables d'environnement pour Poetry
ENV POETRY_VERSION=2.3.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app

# 3. Installation des dépendances système et de Poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean

# Ajouter Poetry au PATH
ENV PATH="/root/.local/bin:$PATH"

# 4. Dossier de travail
WORKDIR /app

# 5. Installation des dépendances 
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi

# 6. Copie du code source
COPY . .

# 7. Port exposé (celui de FastAPI)
EXPOSE 8000

# 8. Commande de lancement
CMD ["uvicorn", "proxy.app.main:app", "--host", "0.0.0.0", "--port", "8000"]