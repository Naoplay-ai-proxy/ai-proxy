# Gravitee Observability

> Référence technique pour la visibilité de l’usage de l’API via Gravitee et Elasticsearch.

## Objet du document

Ce document décrit l’approche retenue pour rendre observable l’usage du proxy IA exposé via Gravitee. L’objectif est de disposer de métriques exploitables pour le suivi fonctionnel, le diagnostic technique et la gouvernance minimale de l’API, sans s’appuyer sur le transcript brut des requêtes.

## Objectifs d’observabilité

L’observabilité attendue côté gateway doit permettre de répondre aux questions suivantes :

- combien d’appels ont été effectués ;
- avec quelle latence moyenne ;
- quelle est la répartition des statuts HTTP ;
- combien d’erreurs `4xx` et `5xx` sont observées ;
- si les appels rejetés, limités ou en erreur sont bien visibles dans les outils Gravitee.

## Composants concernés

```text
Client -> Gravitee Gateway -> Backend FastAPI
            |
            v
      Analytics / Reporting
            |
            v
       Elasticsearch
```

Les données visibles dans la console Gravitee reposent sur la collecte réalisée par la gateway puis stockée dans Elasticsearch.

## Indicateurs minimum à suivre

- volume total d’appels ;
- latence moyenne ;
- répartition des codes de statut ;
- volume d’erreurs `4xx` ;
- volume d’erreurs `5xx`.

## Source des données

La source principale d’observabilité côté Gravitee est constituée par les index de métriques, généralement de type :

```text
gravitee-v4-metrics-*
```

Selon le niveau de journalisation activé, des informations complémentaires peuvent aussi apparaître dans des index de logs, mais les métriques doivent rester la base principale de lecture pour l’usage, la performance et les erreurs.

## Configuration attendue

Pour que l’observabilité fonctionne correctement :

- la gateway doit avoir analytics/reporting activé ;
- Elasticsearch doit être joignable depuis les composants Gravitee ;
- les endpoints configurés dans les conteneurs doivent cibler les bons noms de services réseau ;
- la console Gravitee doit être capable de lire les données remontées.

## Point d’attention en environnement Docker

Dans un déploiement conteneurisé, l’usage de `localhost` dans la configuration analytics peut empêcher la remontée correcte des données si Elasticsearch tourne dans un autre conteneur.

Dans ce cas, il faut utiliser le **nom du service ou du conteneur résolu sur le réseau Docker**, et non `localhost`.

## Vérifications de premier niveau

### Vérifier la présence des index Gravitee

```bash
curl "http://localhost:9200/_cat/indices/gravitee-*?v"
```

### Vérifier la présence de métriques récentes

```bash
curl -X GET "http://localhost:9200/gravitee-v4-metrics-*/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 1,
    "sort": [{ "@timestamp": "desc" }]
  }'
```

## Requête d’agrégation recommandée

La requête suivante permet d’obtenir un résumé exploitable sur les dernières 24 heures.

```bash
curl -X GET "http://localhost:9200/gravitee-v4-metrics-*/_search" \
  -H "Content-Type: application/json" \
  -d '{
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

## Interprétation des résultats

- `hits.total.value` : nombre total de documents correspondant à la fenêtre de temps ;
- `status_codes` : répartition des statuts HTTP ;
- `errors_4xx` : volume d’erreurs côté accès ou validation ;
- `errors_5xx` : volume d’erreurs côté backend ou service amont ;
- `avg_latency` : latence moyenne observée par la gateway.

## Usage opérationnel des métriques

Les métriques Gravitee sont utiles pour :

- valider qu’un appel de test est bien passé par la gateway ;
- vérifier qu’un refus d’accès apparaît bien en `401` ou `403` ;
- confirmer l’apparition d’un `429` lorsque la limitation de débit est atteinte ;
- suivre la latence globale de l’API ;
- préparer les futurs tableaux de bord d’usage, de coût et de qualité.

## Segmentation possible

Selon la configuration effective, l’analyse peut être segmentée par :

- plan ;
- API ;
- application consommatrice ;
- route ou chemin ;
- identifiant consommateur si une stratégie de propagation existe.

La segmentation avancée n’est pas obligatoire pour le MVP, mais la structure d’observabilité doit rester compatible avec cette évolution.

## Différence entre analytics et logs

- **Analytics / métriques** : conçus pour mesurer les volumes, les statuts et la latence.
- **Logs** : conçus pour le diagnostic détaillé et la corrélation, avec davantage de vigilance sur la donnée capturée.

L’observabilité de base doit fonctionner même si les logs détaillés sont volontairement limités pour des raisons de gouvernance.

## Limites connues

- un appel très récent peut ne pas apparaître instantanément selon le délai de remontée ;
- des métriques visibles dans Elasticsearch peuvent ne pas être encore visibles dans la console selon le timing ;
- une mauvaise configuration réseau entre conteneurs peut donner l’impression que Gravitee ne collecte rien ;
- une console vide ne signifie pas automatiquement que l’appel n’a pas eu lieu : il faut vérifier la chaîne complète.

## Dépannage de premier niveau

| Symptôme | Cause probable | Première action |
|---|---|---|
| Aucun analytics visible | Endpoint Elasticsearch incorrect ou reporting non actif | Vérifier la configuration analytics côté gateway et les noms de services utilisés. |
| Index Gravitee absents | Elasticsearch non alimenté ou non joignable | Vérifier la connectivité entre gateway et Elasticsearch. |
| Volume visible mais latence incohérente | Champ consulté non adapté ou fenêtre trop courte | Rejouer un test contrôlé puis relancer la requête d’agrégation. |
| Les tests Postman n’apparaissent pas | Mauvais environnement, mauvaise API ou mauvais filtrage | Vérifier l’API cible, la période, puis générer un trafic simple et identifiable. |

## Éléments de preuve à conserver

- capture ou export console montrant les appels ;
- sortie `_cat/indices` montrant les index Gravitee ;
- requête d’agrégation montrant statuts, erreurs et latence ;
- preuve que les scénarios `200`, `401` et `429` apparaissent correctement.
