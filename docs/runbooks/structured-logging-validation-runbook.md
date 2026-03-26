# Structured Logging Validation Runbook

> Procédure opérationnelle pour vérifier que Gravitee produit des traces exploitables sans stocker le transcript brut.

## Objet du runbook

Ce runbook permet de valider trois points essentiels :

- la présence de champs structurés exploitables ;
- l’absence de transcript brut dans les données stockées ;
- la corrélation possible des appels via `request-id`.

## Pré-requis

- l’API est exposée via Gravitee ;
- Elasticsearch est joignable ;
- l’opérateur peut générer un appel de test ;
- la configuration de logs ou reporting de l’API est accessible.

## Variables de travail

```bash
export GATEWAY_URL="https://<gateway-host>/meeting-summary"
export API_KEY="<api-key-if-required>"
export TEST_MARKER="PHRASE_TEST_CONFIDENTIELLE"
export REQUEST_ID_TO_CHECK="replace-with-request-id"
```

## Synthèse des contrôles

| # | Contrôle | Résultat attendu | Preuve |
|---:|---|---|---|
| 1 | Appel de test | Appel traité par Gravitee | Réponse HTTP et en-têtes |
| 2 | Document structuré récent | Champs stables visibles | Résultat Elasticsearch |
| 3 | Absence de transcript | Zéro hit sur la phrase test | Recherche négative |
| 4 | Corrélation | `request-id` retrouvable | Recherche positive |
| 5 | Réglage UI | Payload non capturé | Capture de configuration |

## Contrôle 1 — Générer un appel identifiable

Envoyer un appel contenant une chaîne de test facilement recherchable.

```bash
curl -i "$GATEWAY_URL" \
  -H "Content-Type: application/json" \
  -H "X-Gravitee-Api-Key: $API_KEY" \
  -d "{
    \"meeting_id\": \"m-log-001\",
    \"transcript\": \"$TEST_MARKER\",
    \"language\": \"fr\"
  }"
```

- Conserver le statut HTTP.
- Relever le `request-id` s’il est renvoyé dans les en-têtes ou dans les traces accessibles.

## Contrôle 2 — Vérifier la présence d’un document structuré récent

```bash
curl -X GET "http://localhost:9200/gravitee-v4-metrics-*/_search?pretty" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 1,
    "sort": [{ "@timestamp": "desc" }]
  }'
```

### Vérifications attendues

Rechercher au minimum :

- `request-id` ;
- `@timestamp` ;
- `status` ;
- `gateway-response-time-ms` ;
- `endpoint-response-time-ms` si disponible.

## Contrôle 3 — Prouver l’absence du transcript brut

```bash
curl -X GET "http://localhost:9200/gravitee-v4-*/_search?pretty" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "query_string": {
        "query": "PHRASE_TEST_CONFIDENTIELLE"
      }
    }
  }'
```

### Résultat attendu

```text
hits.total.value = 0
```

Si la phrase est retrouvée, cela signifie qu’un payload sensible a probablement été capturé dans les logs ou dans les structures de reporting.

## Contrôle 4 — Vérifier la corrélation par `request-id`

```bash
curl -X GET "http://localhost:9200/gravitee-v4-*/_search?pretty" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "term": {
        "request-id": "replace-with-request-id"
      }
    }
  }'
```

### Résultat attendu

Le `request-id` doit permettre de retrouver au moins le document de métrique correspondant, et éventuellement un document de log complémentaire selon le niveau de détail activé.

## Contrôle 5 — Vérifier la configuration dans l’UI Gravitee

Dans l’API concernée :

1. ouvrir la section de logs ou reporting ;
2. cliquer sur la configuration de collecte ;
3. vérifier que la capture du **payload** est désactivée dans **Content Data** ou équivalent.

## Guide de dépannage

| Symptôme | Cause probable | Première action |
|---|---|---|
| Aucun document récent | Appel non passé par Gravitee ou analytics non alimenté | Vérifier l’URL de test, puis la collecte analytics. |
| Le transcript apparaît | Capture du payload activée | Désactiver la capture du payload puis rejouer le test. |
| `request-id` introuvable | Mauvais identifiant ou délai d’indexation | Relever un identifiant plus récent puis relancer la recherche. |
| Les latences sont absentes | Mauvais index ou champ inattendu | Vérifier le mapping réel du document retourné. |

## Trace de validation à conserver

- sortie du test HTTP ;
- extrait d’un document récent de métrique ;
- recherche négative sur la phrase test ;
- recherche positive sur le `request-id` ;
- capture de configuration montrant que le payload n’est pas collecté.
