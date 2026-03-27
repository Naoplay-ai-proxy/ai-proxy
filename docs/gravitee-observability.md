# Gravitee Observability

> Référence technique pour la visibilité de l’usage de l’API via Gravitee et Elasticsearch.

## Objet du document

Ce document décrit l’approche retenue pour rendre observable l’usage du proxy IA exposé via Gravitee.

L’objectif est de disposer de métriques simples et exploitables pour suivre le trafic, la latence et les erreurs, sans dépendre du transcript brut des requêtes.

## Indicateurs attendus

L’observabilité retenue doit permettre de suivre au minimum :

- le volume d’appels ;
- la latence moyenne ;
- la répartition des statuts HTTP ;
- les erreurs `4xx` ;
- les erreurs `5xx`.

## Chaîne d’observabilité

```text
Client -> Gravitee Gateway -> Backend ai-proxy
            |
            v
      Analytics Gravitee
            |
            v
       Elasticsearch
```

La gateway collecte les informations d’usage et les rend visibles via la console Gravitee et, selon les besoins, via Elasticsearch.

## Source principale

La lecture principale repose sur les métriques Gravitee, généralement stockées dans des index de type :

```text
gravitee-v4-metrics-*
```

Ces données suffisent pour le suivi de base de l’usage, de la performance et des erreurs.

## Conditions de bon fonctionnement

Pour que l’observabilité soit exploitable :

- les analytics doivent être activés côté Gravitee ;
- Elasticsearch doit être joignable par les composants Gravitee ;
- la configuration réseau doit viser le bon service, en particulier en environnement Docker ;
- la console doit pouvoir lire les données remontées.

## Point d’attention Docker

Lorsque Gravitee et Elasticsearch tournent dans des conteneurs distincts, `localhost` peut être inadapté.

Il faut alors utiliser le **nom du service ou du conteneur accessible sur le réseau Docker**.

## Limites de l’approche

Cette observabilité n’a pas vocation à remplacer :

- les logs applicatifs du backend ;
- les diagnostics détaillés côté code ;
- les traces métier fines.

Elle fournit avant tout une visibilité gateway sur l’usage et les statuts.

## Articulation avec les autres documents

- la configuration générale de l’exposition API est décrite dans `docs/gravitee-configuration.md` ;
- la politique de journalisation structurée est décrite dans `docs/structured-logging.md` ;
- les vérifications détaillées sont décrites dans `docs/runbooks/gravitee-validation-runbook.md`.

## Référence associée

- `docs/runbooks/gravitee-validation-runbook.md`
