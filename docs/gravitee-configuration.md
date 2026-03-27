# Configuration Gravitee

> Référence technique pour l’exposition gouvernée du backend Proxy IA via Gravitee.

## Objet du document

Ce document décrit la configuration Gravitee retenue pour exposer le backend `ai-proxy` de manière maîtrisée.

Il sert de référence de configuration. Les étapes de test détaillées et les contrôles opérationnels sont décrits dans le runbook associé.

## Périmètre

- exposition de l’API backend via Gravitee ;
- contrôle d’accès MVP ;
- limitation de débit ;
- analytics et visibilité minimale ;
- principes de journalisation compatibles avec l’exploitation.

## Architecture cible

```text
Client autorisé -> Gravitee Gateway -> Backend ai-proxy -> Fournisseur LLM
```

Principes associés :

- le client appelle Gravitee, jamais le backend directement ;
- le backend reste joignable prioritairement sur le réseau interne ;
- la gateway applique les mécanismes d’accès, de limitation et de traçabilité ;
- le choix du modèle LLM reste contrôlé côté serveur.

## Exposition du backend

Gravitee doit pointer vers le service FastAPI interne exposant au minimum :

```text
GET  /health
POST /meeting-summary
```

Exemple de cible backend :

```text
http://ai-proxy:8000
```

La stratégie de version publique est portée par Gravitee. Le backend ne doit pas imposer de préfixe public qui entre en conflit avec le routage de la gateway.

## Contrôle d’accès

Le contrôle d’accès MVP repose sur un plan Gravitee appliqué à l’API publiée.

Principes retenus :

- l’appel sans autorisation valide doit être rejeté ;
- l’appel autorisé doit transiter par la gateway ;
- le backend ne constitue pas le point principal de contrôle d’accès public.

## Limitation de débit

La limitation de débit est appliquée côté gateway afin de :

- protéger le backend ;
- encadrer l’usage ;
- rendre visibles les dépassements via les analytics et les statuts HTTP associés.

Le réglage précis peut évoluer selon l’environnement, mais le principe reste inchangé : la régulation doit être faite en amont du backend.

## Secrets et configuration sensible

Les secrets nécessaires à l’appel du fournisseur LLM ne doivent pas être stockés dans Gravitee ni exposés aux clients.

Principes retenus :

- Gravitee protège l’accès à l’API ;
- le backend récupère les secrets à l’exécution ;
- les valeurs sensibles ne doivent jamais apparaître dans le dépôt Git ou dans les configurations client.

Les détails de ce point sont décrits dans `docs/llm-secret-management.md`.

## Observabilité

La gateway doit permettre de consulter au minimum :

- le volume d’appels ;
- la latence ;
- la répartition des statuts HTTP ;
- les erreurs visibles côté API.

Cette visibilité repose sur les analytics Gravitee et leur stockage côté Elasticsearch.

Les détails sont décrits dans `docs/gravitee-observability.md`.

## Journalisation

La journalisation doit rester exploitable sans stocker le transcript brut des réunions.

Principes retenus :

- présence d’un identifiant de corrélation stable ;
- conservation des champs utiles au diagnostic ;
- exclusion des données sensibles, notamment le transcript et les secrets.

Les détails sont décrits dans `docs/structured-logging.md`.

## Points de vigilance

- vérifier que la gateway résout correctement le backend sur le réseau visé ;
- éviter les incohérences de routage entre URL publique Gravitee et routes FastAPI ;
- ne pas exposer le backend directement si Gravitee doit rester le point d’entrée unique ;
- s’assurer que les métriques et logs restent cohérents avec les exigences de gouvernance.

## Référence associée

- `docs/runbooks/gravitee-validation-runbook.md`
