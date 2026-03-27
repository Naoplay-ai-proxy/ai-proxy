# Structured Logging

> Référence technique pour une journalisation exploitable côté Gravitee sans stockage du transcript brut.

## Objet du document

Ce document décrit les principes de journalisation structurée attendus pour le proxy IA exposé via Gravitee.

L’objectif est de conserver des traces utiles au diagnostic et à la corrélation, tout en évitant de stocker des données sensibles.

## Principes retenus

- chaque appel doit être corrélable par un identifiant stable ;
- les champs utiles au diagnostic doivent être lisibles et structurés ;
- les données sensibles ne doivent pas être capturées par défaut ;
- la journalisation doit rester exploitable avec Elasticsearch.

## Champs minimum utiles

La base minimale à conserver comprend :

- un identifiant de corrélation, par exemple `request-id` ;
- un horodatage ;
- le statut HTTP ;
- une mesure de latence ;
- le contexte de route ou d’appel.

Selon le besoin, des champs complémentaires peuvent être ajoutés, mais ils doivent rester compatibles avec les exigences de gouvernance.

## Source principale côté Gravitee

Les métriques Gravitee constituent déjà une base utile pour retrouver :

- le statut HTTP ;
- le timestamp ;
- le temps de réponse ;
- un identifiant de transaction ou de requête selon la configuration disponible.

Les logs détaillés ne doivent être activés qu’avec prudence.

## Données à exclure

Les éléments suivants ne doivent pas apparaître dans les logs si cela peut être évité :

- transcript brut de réunion ;
- clé API ou secret ;
- payload complet contenant des données sensibles ;
- éléments de réponse qui ne sont pas nécessaires au diagnostic.

## Point de vigilance principal

Le risque principal provient de la capture du **payload de requête** dans les logs détaillés de l’API.

Si cette capture est activée de manière trop large, des champs sensibles peuvent se retrouver dans les documents stockés.

## Corrélation

La journalisation reste vraiment exploitable si elle permet de relier :

- un appel observé côté client ;
- une entrée visible dans Gravitee ;
- une métrique ou un log consultable dans Elasticsearch ;
- un événement éventuellement retrouvé côté backend.

Le `request-id` est le point central de cette corrélation.

## Articulation avec les autres documents

- l’exposition de l’API est décrite dans `docs/gravitee-configuration.md` ;
- les métriques et analytics sont décrits dans `docs/gravitee-observability.md` ;
- les contrôles détaillés sont décrits dans `docs/runbooks/structured-logging-validation-runbook.md`.

## Référence associée

- `docs/runbooks/structured-logging-validation-runbook.md`
