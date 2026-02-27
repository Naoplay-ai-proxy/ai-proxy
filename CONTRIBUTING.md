# Contributing — Proxy IA gouverné

Ce dépôt suit des règles simples pour garantir : qualité ✅, intégration fluide 🔁, et traçabilité 📌.

---

## 1) Branches & stratégie

Branches principales :
- `main` : stable (release)
- `develop` : intégration continue

Branches de travail (toujours via PR vers `develop`) :
- `feature/<id>-<short>` : nouvelle fonctionnalité (ex: `feature/P1-03-validation`)
- `fix/<id>-<short>` : correction de bug (ex: `fix/P1-08-422-error`)
- `chore/<id>-<short>` : maintenance / deps / refactor non-fonctionnel (ex: `chore/deps-update`)
- `docs/<id>-<short>` : documentation (ex: `docs/api-contract`)
- `hotfix/<id>-<short>` : correctif urgent sur `main` (rare)

Règle : **pas de push direct sur `main` / `develop`** → uniquement via Pull Request (PR).

---

## 2) Commits

Conventions recommandées :
- `feat: ...`
- `fix: ...`
- `test: ...`
- `docs: ...`
- `chore: ...`

---

## 3) Pull Request (PR)

### 3.1 Quand ouvrir une PR
- Dès que le changement est cohérent et testable (même non final).
- PR petites : idéalement < ~300 lignes diff.

### 3.2 Règles de review (GitHub)
Ici “review” = **code review GitHub avant merge** (pas la colonne Kanban).

- **1 approbation minimum** pour merge.
- **2 approbations** si zone sensible :
  - contrat OpenAPI / schémas
  - auth / quotas
  - logging (risque de fuite de données)
  - sanitisation / filtres

### 3.3 Checklist avant PR (obligatoire)
À faire en local avant d’ouvrir/mettre à jour une PR :
- Lint OK :
  - `poetry run ruff check .`
- Tests OK :
  - `poetry run pytest -q`
- Si le contrat change :
  - `openapi.yaml` mis à jour
  - exemples request/response (docs) mis à jour

Règles spécifiques :
- pas de commentaires générés automatiquement sans valeur technique
- pas de copier-coller brut d’IA sans relecture
- les commentaires doivent expliquer le “pourquoi”, pas le “quoi”
- tout code proposé par IA doit être relu, testé et simplifié avant commit

---

## 4) Tests — organisation & règles

### 4.1 Organisation recommandée
On garde **2 dossiers** (niveau de test) :
- `tests/unit/` : tests sans HTTP (règles métier, validation, helpers)
- `tests/integration/` : tests via endpoint FastAPI (client de test)

💡 Les tests “abuse” (oversize, payload invalid, etc.) se classent **selon leur niveau** :
- si ça appelle l’API → `integration`
- si ça teste une règle/fonction → `unit`

### 4.2 Markers Pytest
On utilise des markers pour filtrer :
- `unit` / `integration` (niveau)
- `abuse` (catégorie/intention)

Règle : `abuse` peut exister dans `unit` **ou** `integration`.

### 4.3 Mélange de types dans un fichier
On évite de mélanger unit + integration dans le même fichier.
- Si un fichier mélange déjà : ce n’est pas bloquant, mais on **refactor progressivement** vers la structure cible.

### 4.4 Règle minimale
- **Au moins 1 test par PR** (ou justification “no test needed”).

---

## 5) Qualité & sécurité (non négociable)

- ❌ Ne jamais logger le transcript brut.
- ✅ Logs structurés, avec corrélation (request-id).
- ❌ Ne jamais commiter de secrets (.env, tokens, clés).

### Compatibilité OpenAPI
- ✅ Toute modif OpenAPI doit être **backward-compatible** si possible (ne pas casser les clients existants).
- Si un changement est **breaking** (ex: renommer un champ, changer un type, supprimer un champ/endpoint) :
  - documenter explicitement le breaking change
  - envisager un versioning (`/v2`) si nécessaire

---

## 6) Commandes essentielles (avant PR)

Installation :
- `poetry install`

Lancer l’API (smoke test) :
- `poetry run uvicorn proxy.app.main:app --reload`

Tests :
- `poetry run pytest -q`

Lint (qualité code) :
- `poetry run ruff check .`

---

## 7) Intégration & merge

### Squash merge (recommandé)
**Squash merge** = fusionner une PR en **un seul commit** dans la branche cible.

Pourquoi :
- historique plus lisible (1 PR = 1 commit)
- revert plus simple (1 commit à annuler)

Règle :
- Interdit : merge si checks/tests non passés.
- Interdit : merge si CI rouge *(à activer dès que GitHub Actions est en place)*.
