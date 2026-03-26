# Gravitee Validation Runbook

> Guide opérationnel pas à pas pour valider le routage, le contrôle d’accès, les quotas, les analytics et la journalisation.

## Objet du runbook

Ce runbook fournit une séquence de validation exploitable sans dépendre du contexte de mise en œuvre initial. Il est pensé comme un guide d’exécution orienté résultats attendus, vérifications et éléments de preuve.

Chaque contrôle peut être exécuté indépendamment, mais l’ordre proposé est recommandé pour diagnostiquer rapidement un défaut de routage, de plan, de quota ou de journalisation.

## Portée

| Élément | Description |
|---|---|
| Objectif | Documenter la configuration Gravitee et fournir une procédure de validation reproductible pour l'exposition gouvernée du backend Proxy IA. |
| Périmètre | API `/meeting-summary`, contrôle d'accès MVP, limitation de débit, analytics, logs structurés et vérifications d'exploitation. |

## Pré-requis

- L’API Gravitee est déployée et publiée.
- Le backend est joignable depuis la gateway.
- Un mécanisme d’accès valide existe, par exemple une API key.
- Elasticsearch est joignable depuis la stack Gravitee.
- L’opérateur dispose d’un accès à la console Gravitee et, si nécessaire, d’un shell sur l’infrastructure.

## Variables de travail

```bash
export GATEWAY_URL="https://<gateway-host>/meeting-summary"
export HEALTH_URL="https://<gateway-host>/health"
export API_KEY="<api-key-if-required>"
export TEST_USER_1="user-alpha"
export TEST_USER_2="user-beta"
```

## Séquence de validation

- Valider d’abord la connectivité et la santé de service.
- Valider ensuite le succès fonctionnel sur `/meeting-summary`.
- Tester le refus d’accès sans mécanisme attendu.
- Pousser les appels jusqu’au seuil de rate limit pour observer le `429`.
- Contrôler la visibilité des analytics dans Gravitee.
- Vérifier dans Elasticsearch la présence des métriques attendues, l’absence du transcript et la corrélation `request-id`.

## Synthèse des contrôles

| # | Contrôle | Résultat attendu | Preuve |
|---:|---|---|---|
| 1 | Route de santé | `200` | Corps de réponse et en-têtes |
| 2 | Appel fonctionnel | `200` | Payload de résumé via Gravitee |
| 3 | Appel non autorisé | `401` ou `403` | Requête refusée sans accès valide |
| 4 | Dépassement de quota | `429` | Appels répétés au-delà du seuil configuré |
| 5 | Analytics | Visible | Appels visibles dans la console Gravitee |
| 6 | Index de métriques | Visible | Sortie de requête Elasticsearch |
| 7 | Absence de transcript stocké | Absent | Recherche à zéro hit sur une chaîne de test connue |
| 8 | Corrélation | Visible | `request-id` retrouvable dans les données stockées |

## Contrôle 1 — Santé et connectivité

Objectif : confirmer que Gravitee peut joindre le backend et renvoyer une réponse de santé cohérente.

```bash
curl -i "$HEALTH_URL"   -H "X-Gravitee-Api-Key: $API_KEY"
```

- Résultat attendu : HTTP `200` avec un corps de santé cohérent.
- En cas d’échec, distinguer rapidement un problème de routage gateway, d’application de plan ou d’indisponibilité backend.

## Contrôle 2 — Succès fonctionnel sur `/meeting-summary`

Envoyer un payload de test minimal et conforme.

```bash
curl -i "$GATEWAY_URL"   -H "Content-Type: application/json"   -H "X-Gravitee-Api-Key: $API_KEY"   -d '{
    "meeting_id": "m-001",
    "transcript": "Projet validé. Alice prépare la démonstration. Bob met à jour la documentation.",
    "language": "fr"
  }'
```

- Résultat attendu : HTTP `200`.
- Conserver la réponse et noter le `request-id` si l’en-tête est disponible.

## Contrôle 3 — Refus d’accès non autorisé

Répéter l’appel sans le mécanisme d’accès attendu.

```bash
curl -i "$GATEWAY_URL"   -H "Content-Type: application/json"   -d '{
    "meeting_id": "m-unauthorized",
    "transcript": "Test accès refusé",
    "language": "fr"
  }'
```

- Résultat attendu : HTTP `401` ou `403` selon le plan configuré.
- Si la requête aboutit, revoir immédiatement les plans actifs et la publication.

## Contrôle 4 — Dépassement du quota global

Lancer des appels répétés jusqu’au seuil configuré.

```bash
for i in $(seq 1 20); do
  curl -s -o /dev/null -w "%{http_code}
" "$GATEWAY_URL"     -H "Content-Type: application/json"     -H "X-Gravitee-Api-Key: $API_KEY"     -d "{"meeting_id":"m-$i","transcript":"test quota $i","language":"fr"}"
done
```

- Résultat attendu : apparition d’un HTTP `429` après dépassement du seuil.
- Noter à partir de quel ordre de grandeur le `429` apparaît pour comparer ensuite avec les analytics.

## Contrôle 5 — Préparation à une séparation par consommateur

À utiliser uniquement si un header d’identification consommateur est déjà prévu.

```bash
curl -i "$GATEWAY_URL"   -H "Content-Type: application/json"   -H "X-Gravitee-Api-Key: $API_KEY"   -H "X-User-Id: $TEST_USER_1"   -d '{"meeting_id":"m-user-1","transcript":"test user 1","language":"fr"}'

curl -i "$GATEWAY_URL"   -H "Content-Type: application/json"   -H "X-Gravitee-Api-Key: $API_KEY"   -H "X-User-Id: $TEST_USER_2"   -d '{"meeting_id":"m-user-2","transcript":"test user 2","language":"fr"}'
```

- Résultat attendu : le mécanisme permet d’isoler logiquement les consommateurs sans exposer de donnée sensible.

## Contrôle 6 — Visibilité analytics dans Gravitee

Ouvrir la console Gravitee, accéder à l’API cible puis à la vue analytics ou monitoring.

- Résultat attendu : les appels du runbook sont visibles.
- Vérifier au minimum le volume d’appels, la latence moyenne et le taux d’erreur.

> Si les analytics sont absents, commencer par vérifier la configuration analytics sur la gateway et le câblage de l’endpoint Elasticsearch utilisé par les conteneurs Gravitee.

## Contrôle 7 — Vérification des index et métriques Elasticsearch

Lister les index récents puis exécuter une requête simple sur les métriques.

```bash
docker exec -it gio_apim_elasticsearch sh
curl "http://localhost:9200/_cat/indices/gravitee-*?v"
```

```bash
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

- Résultat attendu : les index existent et l’agrégation remonte au moins les statuts et la latence moyenne.

## Contrôle 8 — Prouver l’absence de stockage du transcript

Envoyer une requête contenant une chaîne très identifiable, puis rechercher cette chaîne dans les index Gravitee.

```bash
curl -X GET "http://localhost:9200/gravitee-v4-*/_search?pretty"   -H "Content-Type: application/json"   -d '{
    "query": {
      "query_string": {
        "query": "PHRASE_TEST_CONFIDENTIELLE"
      }
    }
  }'
```

- Résultat attendu : `total = 0`.
- Si la chaîne apparaît, revoir immédiatement la configuration de capture de payload dans Gravitee.

## Contrôle 9 — Corrélation par `request-id`

Réutiliser un `request-id` récupéré lors d’une réponse précédente et le rechercher dans les données Gravitee.

```bash
curl -X GET "http://localhost:9200/gravitee-v4-*/_search?pretty"   -H "Content-Type: application/json"   -d '{
    "query": {
      "term": {
        "request-id": "replace-with-request-id"
      }
    }
  }'
```

- Résultat attendu : le `request-id` est retrouvable dans les métriques et, selon la configuration, dans les logs associés.

## Guide de dépannage

| Symptôme | Cause probable | Première action |
|---|---|---|
| La route de santé échoue | Mauvaise cible backend, problème réseau ou plan appliqué | Vérifier l’URL d’endpoint, l’accessibilité sur le réseau Docker et le plan utilisé par la requête. |
| L’appel fonctionnel renvoie `404` | Le chemin gateway ne correspond pas à la route backend | Vérifier le `context-path` et le mapping de route backend. |
| L’appel fonctionnel renvoie `401` | Mécanisme d’accès manquant ou invalide | Vérifier le plan actif et l’en-tête ou le credential utilisé. |
| Le quota ne renvoie jamais `429` | Pas de rate limit appliqué ou seuil trop élevé | Revoir la politique Gravitee ou la configuration du plan. |
| Les analytics sont vides | Mauvais câblage Elasticsearch ou reporting désactivé | Vérifier les noms de services, les endpoints et les réglages de reporting. |
| Le transcript apparaît dans les logs | Journalisation du payload activée | Désactiver la capture de payload dans le reporting API puis retester. |

## Trace de validation à conserver

- Horodatage d’exécution du runbook
- Hôte gateway utilisé et environnement visé
- Captures ou exports montrant la visibilité analytics
- Traces terminal des scénarios `200`, refus d’accès et `429`
- Résultats de recherche prouvant l’absence du transcript de test et la corrélation par `request-id`
