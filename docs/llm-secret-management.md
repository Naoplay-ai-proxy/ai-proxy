# LLM Secret Management

> Référence technique pour la centralisation et l’utilisation sécurisée des secrets LLM avec Google Secret Manager.

## Objet du document

Ce document décrit l’approche retenue pour centraliser les secrets nécessaires à l’appel du fournisseur LLM sans exposer de clés dans le code, dans le dépôt Git, dans les clients ou dans l’interface de la gateway.

L’objectif est de garantir une gestion organisationnelle des secrets, compatible avec un backend FastAPI exposé via Gravitee, tout en séparant clairement la configuration applicative des données sensibles.

## Principes retenus

- Les clés LLM sont gérées au niveau de l’organisation, pas au niveau d’un utilisateur individuel.
- Les secrets ne doivent jamais être stockés dans le dépôt Git.
- Les secrets ne doivent jamais être exposés côté Google Chat, frontend, Postman partagé ou payload de requête.
- Le backend récupère les secrets à l’exécution et reste le seul composant autorisé à les utiliser pour appeler le fournisseur LLM.
- La gateway Gravitee protège l’accès à l’API, mais n’a pas vocation à exposer ou porter la valeur brute des secrets applicatifs.

## Choix d’implémentation

Le choix retenu est **Google Secret Manager** comme source de vérité pour les secrets LLM.

Cette approche est cohérente dans un contexte d’hébergement GCP car elle permet :

- un stockage centralisé et géré par l’organisation ;
- un contrôle d’accès via IAM ;
- une récupération à l’exécution depuis la VM ou le service applicatif ;
- une limitation de l’exposition des clés dans les fichiers de configuration et les environnements d’exécution.

## État actuel de l’implémentation

À ce stade, le projet utilise **un seul secret principal** pour l’authentification au provider LLM.

En pratique :

- la clé provider est centralisée dans Google Secret Manager ;
- l’application lit ce secret au démarrage ;
- le backend construit ensuite son client LLM à partir de cette valeur ;
- aucune rotation automatisée du secret n’est considérée comme validée à ce stade.

Autrement dit, la **centralisation du secret est opérationnelle**, mais la **rotation du secret** reste une amélioration possible et non une capacité déjà démontrée.

## Secret concerné

Le secret actuellement utilisé côté LLM est :

- `LLM_API_KEY`

D’autres paramètres applicatifs peuvent exister dans la configuration, mais ils ne correspondent pas nécessairement à des secrets stockés dans Google Secret Manager.

Les paramètres non sensibles, comme certaines limites métier ou la liste des langues autorisées, peuvent rester en configuration classique s’ils ne constituent pas des secrets.

## Architecture logique

```text
Google Secret Manager -> Backend FastAPI -> Client LLM -> Provider LLM
                         ^
                         |
                    settings / startup
```

## Flux de récupération du secret

1. Le backend démarre.
2. Le module de configuration charge les paramètres applicatifs.
3. Le module de secrets interroge Google Secret Manager.
4. La valeur du secret est injectée dans la configuration runtime.
5. L’application construit ensuite le client LLM à partir de cette configuration.
6. Si le secret obligatoire est absent ou inaccessible, le démarrage doit échouer explicitement.

## Intégration applicative recommandée

L’intégration retenue côté backend repose sur une séparation claire entre :

- **configuration applicative** ;
- **chargement du secret** ;
- **construction du client LLM**.

Une organisation de ce type est recommandée :

```text
app/
  core/
    settings.py
    secrets.py
  llm_client.py
  main.py
```

### Logique d’initialisation

- `settings.py` porte la structure de configuration.
- `secrets.py` encapsule la récupération depuis Google Secret Manager.
- `main.py` déclenche le chargement au démarrage.
- l’objet de configuration final est stocké dans `app.state.settings` ;
- le client LLM construit à partir de cette configuration est stocké dans `app.state.llm_client`.

Cette approche évite de relire le secret à chaque requête et limite l’exposition des composants sensibles.

## Authentification GCP

L’accès à Google Secret Manager dépend du contexte d’exécution.

### Depuis une VM GCP

L’application peut s’appuyer sur les identifiants applicatifs associés à la VM, à condition que :

- la VM dispose d’un compte de service adapté ;
- les permissions IAM nécessaires soient accordées ;
- le scope ou l’accès API permette l’appel aux services GCP concernés.

### Depuis un poste local

Pour le développement ou les tests, il est possible d’utiliser des identifiants locaux, par exemple via Application Default Credentials, à condition de travailler dans le bon projet GCP et avec les droits adaptés.

## Permissions minimales attendues

Le service exécutant l’application doit pouvoir **accéder à la version active du secret**.

En pratique, il faut valider au minimum :

- le bon projet GCP ;
- le bon compte d’exécution ;
- les permissions de lecture sur le secret ;
- l’existence d’une version active du secret.

## Comportement attendu en cas d’erreur

Le backend ne doit pas démarrer en mode dégradé silencieux si un secret obligatoire manque.

### Cas à traiter explicitement

- secret introuvable ;
- version absente ou désactivée ;
- mauvais projet GCP ;
- compte non authentifié ;
- permission refusée ;
- erreur réseau temporaire.

### Règles de gestion

- journaliser l’échec de façon exploitable ;
- ne jamais afficher la valeur du secret dans les logs ;
- échouer explicitement au démarrage si le secret est indispensable ;
- conserver un message d’erreur utile pour le diagnostic.

## Séparation des environnements

Même si le projet ne dispose pas encore de plusieurs environnements complets, la documentation doit prévoir la séparation logique suivante :

- **local** : développement ou tests locaux ;
- **VM / intégration** : exécution dans l’infrastructure de test ;
- **production** : exécution en environnement cible.

Chaque environnement doit pouvoir référencer son propre secret ou sa propre configuration d’accès, sans changement de code métier.

## Rotation du secret

La rotation du secret n’est **pas considérée comme validée** à ce stade du projet.

Cela signifie concrètement :

- aucune rotation automatique n’a été confirmée comme mise en place ;
- aucune procédure de rotation industrialisée n’a été démontrée ;
- aucun comportement de rechargement dynamique du secret n’est documenté comme opérationnel.

La rotation peut donc être considérée comme une **évolution recommandée**, mais pas comme une capacité actuellement couverte.

### Évolution possible à prévoir plus tard

Une approche simple consisterait à :

- créer une nouvelle version du secret ;
- redémarrer le service si le chargement se fait au startup ;
- vérifier que l’appel provider fonctionne encore ;
- révoquer l’ancienne version selon la politique interne.

Cette logique reste cependant une **piste d’amélioration** et non un élément déjà validé.

## Règles de non-exposition

Les secrets ne doivent apparaître :

- ni dans le code source ;
- ni dans les fichiers commités ;
- ni dans les payloads entrants ;
- ni dans les réponses HTTP ;
- ni dans les logs applicatifs ou gateway ;
- ni dans les captures d’écran partagées à l’extérieur de l’équipe.

## Points de contrôle recommandés

- le dépôt Git ne contient aucune valeur de secret ;
- le backend démarre uniquement si le secret requis est disponible ;
- la récupération du secret fonctionne depuis l’environnement cible ;
- l’application utilise bien la configuration chargée au runtime ;
- aucune clé n’est visible côté client ou dans les interfaces non prévues pour cela.

## Limites connues

- si le chargement a lieu uniquement au démarrage, toute modification du secret impose un redémarrage du service pour être prise en compte ;
- un mauvais paramétrage IAM peut bloquer complètement l’initialisation ;
- la distinction entre secret et simple variable de configuration doit rester claire pour éviter de complexifier inutilement le projet ;
- la rotation n’est pas encore couverte comme capacité validée.

## Éléments de preuve à conserver

- preuve de présence du secret dans Google Secret Manager ;
- preuve d’accès réussi depuis l’environnement d’exécution ;
- preuve de démarrage réussi de l’application après chargement du secret ;
- preuve négative d’absence de la clé dans le dépôt et dans les logs.
