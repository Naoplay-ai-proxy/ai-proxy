# Configuration Gravitee

> Référence technique pour l’exposition gouvernée du backend Proxy IA via Gravitee.

## Objet du document

Ce document décrit la configuration côté Gravitee utilisée pour exposer le backend Proxy IA dans un cadre maîtrisé. Il est rédigé pour être intégré au dépôt Git comme documentation durable, indépendante du découpage interne du backlog.

L’objectif est de fournir une référence claire sur le fonctionnement attendu de l’exposition API, les garde-fous de sécurité appliqués à la passerelle, ainsi que les points de contrôle nécessaires pour l’exploitation.

## Portée

| Élément | Description |
|---|---|
| Objectif | Documenter la configuration Gravitee et fournir une procédure de validation reproductible pour l'exposition gouvernée du backend Proxy IA. |
| Périmètre | API `/meeting-summary`, contrôle d'accès MVP, limitation de débit, analytics, logs structurés et vérifications d'exploitation. |

## Vue d’ensemble de l’architecture

- Google Chat, ou tout autre client autorisé, appelle Gravitee et non le backend directement.
- Gravitee Gateway applique l’entrée HTTP, le contrôle d’accès par plan, la limitation de débit, la collecte analytics et la journalisation.
- Le backend est un service FastAPI exposant au minimum les routes `/health` et `/meeting-summary`.
- Le backend appelle le fournisseur LLM au travers d’une abstraction interne ; le choix du modèle reste contrôlé côté serveur.
- Les secrets sont injectés à l’exécution et ne doivent jamais apparaître dans le code client, l’interface ou le dépôt Git.

### Flux de référence

```text
Client autorisé -> Gravitee Gateway -> Backend FastAPI -> Fournisseur LLM
                   -> réponse backend -> Gravitee -> client
```

## Principes de configuration

- La version publique de l’API est gérée par Gravitee. Le backend ne doit pas imposer un préfixe public qui entre en conflit avec la stratégie de routage de la gateway.
- Le backend doit rester accessible uniquement depuis le réseau interne partagé avec Gravitee lorsque l’infrastructure le permet.
- Le contrôle d’accès doit être appliqué à la gateway avant l’introduction de mécanismes d’identité plus avancés.
- L’observabilité doit être suffisante pour le monitoring et l’audit sans capturer le transcript brut des réunions.
- La corrélation entre requêtes, métriques et logs doit être possible via la propagation d’un `request-id` stable.

## Exposition du backend via Gravitee

L’API Gravitee doit être configurée avec un endpoint backend pointant vers le service FastAPI interne. La gateway doit pouvoir résoudre le nom DNS interne du service sur le réseau Docker partagé ou sur le réseau interne de l’infrastructure.

La connectivité de base se valide avec un `GET /health`. Le chemin fonctionnel se valide avec un `POST /meeting-summary`. Les consommateurs ne doivent pas pouvoir contourner Gravitee pour atteindre directement le backend ou le fournisseur LLM.

### Cible backend type

```text
http://ai-proxy:8000
```

### Routes applicatives attendues

```text
GET  /health
POST /meeting-summary
```

## Secrets et configuration d’exécution

- Les identifiants LLM doivent être stockés dans un coffre-fort ou un gestionnaire de secrets contrôlé par l’organisation, puis chargés au runtime par le backend.
- Le dépôt Git peut contenir des noms de variables ou des structures de configuration, mais jamais les valeurs secrètes.
- Aucune clé LLM ne doit apparaître dans la configuration Google Chat, dans un front ou dans des fichiers commités.
- Le design doit permettre la rotation des secrets sans réécriture de l’application.
- Le démarrage du backend doit échouer explicitement si un secret obligatoire est absent.

## Gestion des erreurs du provider

Le mapping des erreurs doit rester prévisible afin de garder une lecture cohérente côté client et côté analytics Gravitee.

| Source ou scénario | Statut HTTP | Comportement attendu |
|---|---:|---|
| Erreur backend non gérée | `500` | Retourner une réponse d’erreur backend contrôlée, sans fuite d’informations internes vers le client. |
| Erreur côté provider | `502` | Exposer un échec amont visible par la gateway avec un corps de réponse normalisé. |
| Indisponibilité amont temporaire | `503` | Signaler l’indisponibilité du service en gardant un comportement de retry explicite et borné. |
| Timeout provider ou appel externe | `504` | Retourner un code de timeout distinct des erreurs internes génériques. |

## Contrôle d’accès

- À ce stade, le contrôle d’accès est assuré par un plan Gravitee, typiquement un plan API key interne.
- Une requête sans mécanisme d’accès attendu doit être rejetée.
- Un plan keyless doit être évité si cela affaiblit le modèle de protection.
- Le comportement d’échec doit rester cohérent, avec un `401` ou un `403` selon la configuration active.
- La configuration retenue doit rester compatible avec une évolution future vers des contrôles basés sur l’identité.

## Quota et limitation de débit

Une limitation de débit globale permet de maîtriser la charge et le coût. En cas de dépassement, le comportement attendu côté gateway est un HTTP `429`.

Le seuil doit être ajustable dans Gravitee sans redéploiement du backend.

Une séparation future par utilisateur peut s’appuyer sur un identifiant temporaire transmis en en-tête, par exemple `X-User-Id`, tant qu’un vrai jeton d’identité n’est pas encore disponible.

## Analytics et métriques

Les analytics Gravitee doivent rendre l’usage de l’API visible dans la console et dans Elasticsearch. Les indicateurs les plus utiles à interpréter sont le nombre total d’appels, les buckets de statuts, les volumes `4xx` et `5xx`, ainsi que la latence moyenne de la gateway.

Indicateurs minimum à suivre :

- Volume d’appels
- Latence moyenne
- Répartition des codes de statut
- Taux d’erreur et pics d’activité

### Point de vigilance Docker

Si les analytics n’apparaissent pas, vérifier que les composants Gravitee utilisent des noms de services résolus dans le réseau de conteneurs, et non `localhost`, pour Elasticsearch et MongoDB dans un environnement Docker.

### Requêtes utiles côté Elasticsearch

```bash
docker exec -it gio_apim_elasticsearch sh
curl "http://localhost:9200/_cat/indices/gravitee-*?v"

curl -X GET "http://localhost:9200/gravitee-v4-metrics-*/_search"   -H "Content-Type: application/json"   -d '{
    "size": 0,
    "query": {
      "range": {
        "@timestamp": {
          "gte": "now-24h",
          "lte": "now"
        }
      }
    },
    "aggs": {
      "status_codes": { "terms": { "field": "status", "size": 10 } },
      "errors_4xx": { "filter": { "range": { "status": { "gte": 400, "lt": 500 } } } },
      "errors_5xx": { "filter": { "range": { "status": { "gte": 500 } } } },
      "avg_latency": { "avg": { "field": "gateway-response-time-ms" } }
    }
  }'
```

## Logs structurés sans stockage du transcript

La journalisation structurée doit conserver des champs opérationnels stables comme le `request-id`, le timestamp, le statut et la latence. Le suivi du modèle utilisé est optionnel et peut être porté par un header dédié ou par une métrique personnalisée.

Les documents de métriques sont généralement présents dans des index de type `gravitee-v4-metrics-*`.

Les documents de logs sont généralement présents dans des index de type `gravitee-v4-logs-*` ou `gravitee-v4-log-*` selon le déploiement.

- La capture du payload brut doit être désactivée pour éviter le stockage du transcript de réunion.
- Dans l’interface Gravitee, il faut vérifier la configuration de reporting ou de logs de l’API et désactiver la capture du contenu de requête.

### Contrôles rapides sur les index

```bash
curl -X GET "http://localhost:9200/gravitee-v4-metrics-*/_search?pretty"   -H "Content-Type: application/json"   -d '{
    "size": 1,
    "sort": [{ "@timestamp": "desc" }]
  }'

curl -X GET "http://localhost:9200/gravitee-v4-logs-*/_search?pretty"   -H "Content-Type: application/json"   -d '{
    "size": 1,
    "sort": [{ "@timestamp": "desc" }]
  }'
```

## Stratégie de corrélation

La corrélation repose sur la présence d’un même `request-id` entre les réponses HTTP, les métriques et, si activés, les logs. Cela permet de suivre un appel de bout en bout sans conserver les données sensibles du transcript.

```bash
curl -X GET "http://localhost:9200/gravitee-v4-*/_search?pretty"   -H "Content-Type: application/json"   -d '{
    "query": {
      "term": {
        "request-id": "replace-with-request-id"
      }
    }
  }'
```

## Éléments de preuve à conserver

- Une réponse `POST /meeting-summary` réussie via Gravitee
- Un appel rejeté sans mécanisme d’accès attendu
- Une réponse `429` après dépassement du quota
- Des analytics visibles dans la console Gravitee
- Des requêtes Elasticsearch montrant la présence des métriques utiles et la corrélation par `request-id`
- Une recherche négative prouvant qu’une chaîne de transcript de test n’est pas stockée
