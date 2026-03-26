# Structured Logging

> Référence technique pour une journalisation exploitable côté Gravitee sans stockage du transcript brut.

## Objet du document

Ce document décrit les règles de journalisation structurée attendues pour le proxy IA exposé via Gravitee. L’objectif est de conserver des traces utiles pour le diagnostic, l’audit et la corrélation, tout en évitant de stocker des données sensibles comme le transcript d’une réunion.

## Principes retenus

- chaque appel doit pouvoir être suivi par un identifiant stable ;
- les champs utiles au diagnostic doivent être présents dans un format structuré ;
- les données sensibles ne doivent pas être capturées par défaut ;
- la journalisation doit rester compatible avec l’exploitation dans Elasticsearch.

## Champs structurés attendus

La base minimale à conserver comprend :

- `request-id` ;
- `timestamp` ;
- `status` ;
- `latence` ;
- route ou contexte de l’appel ;
- éventuellement le modèle utilisé, si ce besoin est formalisé.

## Source principale côté Gravitee

Les index de métriques Gravitee contiennent déjà une partie importante des informations utiles à l’exploitation. Ils permettent notamment de retrouver :

- le `request-id` ou un identifiant de transaction ;
- le timestamp de l’appel ;
- le statut HTTP ;
- le temps de réponse de la gateway ;
- le temps de réponse de l’endpoint amont.

### Requête minimale de consultation

```bash
curl -X GET "http://localhost:9200/gravitee-v4-metrics-*/_search?pretty" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 1,
    "sort": [{ "@timestamp": "desc" }]
  }'
```

## Latences utiles

Deux lectures sont particulièrement utiles :

- `endpoint-response-time-ms` : temps de réponse du service amont ;
- `gateway-response-time-ms` : temps total observé par la gateway.

Cette distinction permet d’estimer la part propre au backend amont et la part ajoutée par la traversée de la gateway.

## Suivi du modèle utilisé

Le modèle utilisé n’est pas nécessairement présent nativement dans les documents de métriques.

Si ce suivi devient nécessaire, deux approches restent cohérentes :

- faire renvoyer par le backend un en-tête dédié du type `X-Model-Used` ;
- injecter une métrique personnalisée si l’outillage Gravitee retenu le permet.

Ce besoin reste optionnel pour le MVP, tant que le modèle est contrôlé côté serveur.

## Règle majeure : pas de transcript brut dans les logs

Le transcript d’une réunion constitue une donnée sensible. Il ne doit pas être stocké dans les logs Gravitee si cela peut être évité.

Le principal risque provient de la **capture du payload de requête** dans les logs détaillés de l’API.

## Point de vigilance dans l’interface Gravitee

Si la configuration de reporting ou de logs de l’API est trop permissive, le payload peut apparaître dans les structures de type :

- `entrypoint-request.body`
- `body`
- ou d’autres champs équivalents selon la vue de logs activée

## Réglage recommandé

Dans l’interface Gravitee, pour l’API concernée :

1. ouvrir la section de logs ou de reporting ;
2. accéder à la configuration de collecte ;
3. désactiver la capture du **payload** dans la partie **Content Data** ou équivalent ;
4. conserver uniquement les champs nécessaires à l’exploitation.

## Prouver l’absence du transcript

Une vérification simple consiste à envoyer une requête de test avec une chaîne hautement identifiable, puis à rechercher cette chaîne dans les index Gravitee.

### Requête de recherche globale

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

Le résultat attendu est :

```text
hits.total.value = 0
```

Cette vérification constitue une preuve technique qu’aucune donnée sensible de test n’a été stockée dans les index consultés.

## Corrélation par `request-id`

La corrélation repose sur un identifiant unique transporté le long du chemin de la requête. Cet identifiant permet de relier :

- la réponse observée côté client ;
- la métrique Gravitee correspondante ;
- les éventuels logs détaillés disponibles ;
- les diagnostics backend si la propagation a été conservée.

### Requête de corrélation

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

## Exemple de contenu attendu

Le format exact dépend des index et de la configuration, mais la logique attendue est de pouvoir retrouver un enregistrement structuré proche de :

```json
{
  "timestamp": "2026-02-26T10:15:30Z",
  "request_id": "req-12345",
  "status": 200,
  "latency_ms": 842,
  "route": "/meeting-summary"
}
```

## Ce qu’il faut conserver

- identifiant de requête ;
- horodatage ;
- statut ;
- latence ;
- route ;
- informations minimales d’exploitation.

## Ce qu’il faut exclure

- transcript brut ;
- clé API ;
- secret LLM ;
- contenu sensible envoyé par l’utilisateur ;
- payload complet non nécessaire au diagnostic.

## Usage opérationnel

Une journalisation structurée correcte permet :

- d’expliquer un échec `401`, `429` ou `5xx` ;
- de retrouver un appel particulier ;
- de corréler un incident avec un test ou un ticket ;
- de préparer des audits techniques sans exposer de contenu métier sensible.

## Limites connues

- des logs trop détaillés augmentent le risque de fuite de données ;
- des logs trop minimalistes rendent le diagnostic difficile ;
- le bon compromis doit être documenté et vérifié régulièrement ;
- les preuves d’absence de transcript doivent être rejouées après toute modification de configuration de reporting.

## Éléments de preuve à conserver

- un exemple de document de métrique récent ;
- une recherche négative prouvant l’absence du transcript de test ;
- une recherche positive par `request-id` montrant la corrélation ;
- une capture de configuration montrant que la capture du payload est désactivée.
