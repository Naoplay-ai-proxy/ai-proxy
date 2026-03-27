# LLM Secret Management

> Référence technique pour la centralisation et l’utilisation sécurisée des secrets LLM avec Google Secret Manager.

## Objet du document

Ce document décrit l’approche retenue pour centraliser les secrets nécessaires à l’appel du fournisseur LLM sans les exposer dans le code, dans le dépôt Git, dans les clients ou dans l’interface de la gateway.

Il s’agit d’une référence de conception et d’exploitation. Les vérifications détaillées sont décrites dans le runbook associé.

## Principes retenus

- les secrets sont gérés au niveau de l’organisation ;
- les valeurs sensibles ne sont pas stockées dans le dépôt Git ;
- les secrets ne sont jamais exposés côté client ;
- seul le backend `ai-proxy` utilise effectivement la clé pour appeler le fournisseur LLM ;
- Gravitee protège l’API, mais ne porte pas la valeur brute des secrets applicatifs.

## Choix retenu

La source de vérité retenue est **Google Secret Manager**.

Ce choix permet :

- un stockage centralisé ;
- un contrôle d’accès via IAM ;
- une récupération à l’exécution depuis la VM ou le service applicatif ;
- une séparation claire entre configuration applicative et données sensibles.

## État actuel

À ce stade, le projet utilise **un seul secret LLM** pour l’authentification au fournisseur.

La centralisation du secret est prise en compte. En revanche, la **rotation automatisée du secret n’est pas couverte à ce stade**.

## Flux logique

```text
Google Secret Manager -> ai-proxy -> client LLM -> provider LLM
```

Le backend charge la configuration applicative, récupère le secret requis, puis construit le client LLM avec les paramètres nécessaires.

## Intégration applicative

L’organisation logique attendue repose sur une séparation simple :

```text
app/
  core/
    settings.py
    secrets.py
  llm_client.py
  main.py
```

Rôles attendus :

- `settings.py` : structure de configuration ;
- `secrets.py` : récupération du secret ;
- `main.py` : chargement au démarrage ;
- `llm_client.py` : construction du client LLM.

Si un secret obligatoire est absent ou inaccessible, le démarrage doit échouer explicitement.

## Pré requis d’accès

L’environnement d’exécution doit disposer :

- du bon projet GCP ;
- d’une identité autorisée à lire le secret ;
- des permissions IAM nécessaires ;
- d’un contexte cohérent entre développement local et exécution sur VM.

## Ce qui ne doit pas apparaître

Les éléments suivants ne doivent pas être exposés :

- valeur de clé API ;
- secret dans un fichier versionné ;
- secret dans un payload de test ;
- secret dans les logs applicatifs ou Gravitee ;
- secret dans une configuration client ou Google Chat.

## Point d’attention

La rotation manuelle d’un secret reste possible côté plateforme, mais elle n’est pas documentée ici comme une capacité déjà industrialisée.

Tant qu’un seul secret est utilisé, il faut surtout garantir :

- sa bonne lecture par l’application ;
- l’absence de fuite ;
- la clarté du diagnostic en cas d’erreur d’accès.

## Référence associée

- `docs/runbooks/llm-secret-management-runbook.md`
