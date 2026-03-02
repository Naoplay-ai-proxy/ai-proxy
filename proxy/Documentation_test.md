# Documentation de la Suite de Tests - Proxy IA

Ce document décrit l'organisation, la typologie et les procédures d'exécution des tests automatisés du projet. Les tests sont implémentés avec le framework **pytest** et couvrent l'ensemble du cycle de vie de la requête, de la validation unitaire à l'appel réel au modèle de langage (LLM).

## 1. Vue d'ensemble et Configuration

Les tests sont situés dans le répertoire `proxy/test/`. La configuration globale est définie dans le fichier `pytest.ini` à la racine du projet.

### Prérequis
Le projet utilise Poetry pour la gestion des dépendances et de l'environnement virtuel.

1.  **Installer Poetry** (si non présent) :
    ```bash
    curl -sSL [https://install.python-poetry.org](https://install.python-poetry.org) | python3 -
    ```

2.  **Installer la version Python cible** (via `pyenv`) :
    ```bash
    pyenv install 3.10.14
    pyenv local 3.10.14
    ```

3.  **Installer les dépendances du projet** :
    ```bash
    poetry install
    ```

### Organisation des Marqueurs (Markers)
Le projet utilise des marqueurs `pytest` pour catégoriser les tests selon leur nature et leur impact (vitesse, coût, dépendances).

| Marqueur | Description | Usage |
| :--- | :--- | :--- |
| **`unitaire`** | Tests isolés vérifiant la logique interne des fonctions et classes sans dépendances externes. | Validation des schémas Pydantic, génération de prompts. |
| **`integration`** | Tests de bout en bout (End-to-End) simulant des appels API HTTP complets. | Vérification du routage, des codes HTTP et du format de réponse. Utilise souvent des Mocks. |
| **`abuse`** | Tests de sécurité, de robustesse et de conformité (Security & Governance). | Tentatives d'injection de prompt, XSS, dépassement de quotas, validation des entrées. |
| **`ai_call`** | Tests effectuant un appel réel vers le fournisseur LLM (OpenAI, Anthropic, etc.). | Vérification finale de la connexion. **Nécessite une clé API valide et engendre des coûts.** |

---

## 2. Description détaillée des fichiers de tests

### A. Tests Unitaires (`unitaire`)

Ces tests sont rapides et ne nécessitent aucun contexte API complexe.

*   **`proxy/test/test_validation.py`**
    *   **Objectif :** Valider les règles métier imposées par les modèles de données (Schémas).
    *   **Couverture :** Vérification des types, des champs obligatoires et des formats attendus pour `MeetingSummaryRequest`.

*   **`proxy/test/test_prompt.py`**
    *   **Objectif :** Valider la logique de construction des prompts système.
    *   **Couverture :** Vérification de l'injection correcte de la langue cible et de la présence des instructions de sécurité (règles de non-hallucination, format JSON strict).

*   **`proxy/test/test_llm_client_mock.py`**
    *   **Objectif :** Tester la logique interne du client LLM, spécifiquement le nettoyage et le parsing de la réponse.
    *   **Méthode :** Utilise `unittest.mock` pour simuler une réponse brute de la librairie `litellm` et vérifier que la méthode `ask_structured` retourne un dictionnaire propre.

### B. Tests de Sécurité (`abuse`)

Ces tests visent à garantir la robustesse de l'application face aux tentatives de manipulation.

*   **`proxy/test/test_abuse.py`**
    *   **Objectif :** Validation statique des entrées malveillantes via Pydantic.
    *   **Cas testés :**
        *   Injection de commandes dans l'ID de réunion (Regex).
        *   Détection de motifs XSS (`<script>`).
        *   Déni de service (DoS) via des payloads trop volumineux.
        *   Utilisation de mots-clés interdits ("Ignore previous instructions").

*   **`proxy/test/test_abuse_mock.py`**
    *   **Objectif :** Validation dynamique du "Sandboxing" (confinement).
    *   **Méthode :** Utilise un client "Espion" (`SpyLLMClient`) injecté via `app.dependency_overrides`.
    *   **Vérification :** S'assure que même si un texte malveillant passe la validation statique, il est correctement encapsulé entre les balises `TRANSCRIPT START` et `TRANSCRIPT END` avant d'être envoyé au LLM, rendant l'attaque inopérante.

### C. Tests d'Intégration (`integration`)

Ces tests valident le fonctionnement global de l'API (Routeur + Client + Modèles).

*   **`proxy/test/test_integration_mock.py`**
    *   **Objectif :** Valider le cycle complet de requête/réponse sans dépendre du fournisseur LLM.
    *   **Méthode :** Utilise une *fixture* `client_mocked` qui remplace le `LLMClient` réel par un `FakeLLMClient` renvoyant une réponse fixe.
    *   **Avantage :** Permet de tester le code HTTP 200, la sérialisation JSON et la structure de réponse sans latence ni coût.

*   **`proxy/test/test_integration.py`** (Partie Validation)
    *   Certains tests dans ce fichier vérifient également le comportement de l'API face à des requêtes invalides (Code 422), sans appeler le LLM.

### D. Tests avec Appel Réel (`ai_call`)

*   **`proxy/test/test_integration.py`**
    *   **Objectif :** Valider la connexion réelle avec le fournisseur tiers.
    *   **Prérequis :** La variable d'environnement `LLM_API_KEY` doit être valide.
    *   **Fonctionnement :** Envoie une transcription réelle, attend la réponse du modèle (GPT/Claude) et vérifie la pertinence sémantique du retour (ex: présence de mots-clés attendus dans le résumé).

---

## 3. Guide d'exécution

Les tests s'exécutent via la commande `pytest` à la racine du projet. Voici les commandes courantes :

### Exécuter toute la suite de tests (sauf appels IA si configuré par défaut)
```bash
poetry run pytest
```

### Exécuter uniquement les tests unitaires et d'intégration (Développement rapide)
Cette commande est recommandée pour le développement quotidien (CI/CD) car elle est rapide et gratuite.
```bash
poetry run pytest -m "not ai_call"
```

### Exécuter uniquement les tests de sécurité
Pour vérifier la robustesse et les règles de gouvernance.
```bash
poetry pytest -m abuse
```

### Exécuter les tests avec appel réel au LLM
À utiliser avec parcimonie pour valider la configuration finale. Assurez-vous d'avoir configuré votre fichier `.env`.
```bash
poetry run pytest -m ai_call
```

### Exécuter un fichier spécifique
```bash
poetry run pytest proxy/test/test_integration_mock.py
```

## 4. Architecture de Mocking

Pour assurer l'indépendance des tests, le projet utilise le système d'injection de dépendances de FastAPI.

1.  **Dependency Override :** Dans les fichiers `*_mock.py`, l'attribut `app.dependency_overrides` est utilisé pour remplacer la classe `LLMClient` par des classes simulées (`FakeLLMClient` ou `SpyLLMClient`).
2.  **Fixtures Pytest :** L'utilisation de fixtures (ex: `client_mocked` ou `spy_client`) garantit que ces remplacements sont appliqués avant le test et nettoyés immédiatement après (`teardown`), évitant ainsi les effets de bord entre les différents fichiers de tests.