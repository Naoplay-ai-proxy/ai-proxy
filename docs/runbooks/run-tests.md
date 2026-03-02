# Runbook — Lancer les tests

## 1) Pré-requis
- Python (version du projet)
- Poetry installé
- Dépendances installées : `poetry install`

## 2) Lancer les tests (standard)
- `poetry run pytest -q`

## 3) Lancer un fichier précis
- `poetry run pytest -q tests/integration/test_meeting_summary.py`

## 4) Lancer un test précis
- `poetry run pytest -q -k "nom_du_test"`

## 5) Lint (ruff)
- `poetry run ruff check .`

## 6) Erreurs courantes
### Import error / module not found
- Vérifier : `poetry install`
- Vérifier l'utilisation de l’environnement Poetry :
  - `poetry run python -c "import proxy; print('ok')"`

### Tests async
- Si on utilise `pytest.mark.asyncio`, vérifier que `pytest-asyncio` est installé/configuré.
