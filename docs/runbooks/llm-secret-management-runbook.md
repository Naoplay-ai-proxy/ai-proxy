# LLM Secret Management Runbook

> Procédure opérationnelle pour vérifier la présence, l’accès et l’utilisation correcte du secret LLM avec Google Secret Manager.

## Objet du runbook

Ce runbook permet de valider que le secret LLM est bien centralisé, accessible depuis l’environnement d’exécution et effectivement utilisé par l’application sans être exposé dans le code, dans les logs ou dans les clients.

## Périmètre réel

À ce stade, le périmètre validé couvre :

- la présence du secret dans Google Secret Manager ;
- la lecture du secret depuis l’environnement d’exécution ;
- l’utilisation du secret par l’application au démarrage.

Ce runbook **ne considère pas la rotation comme une capacité déjà validée**. Une section de fin mentionne seulement comment une rotation manuelle pourrait être testée plus tard.

## Pré-requis

- le secret a été créé dans Google Secret Manager ;
- l’opérateur connaît le projet GCP cible ;
- l’environnement d’exécution dispose du bon compte ou des bons identifiants ;
- l’application est déployée ou au moins exécutable dans l’environnement visé.

## Variables de travail

```bash
export GCP_PROJECT_ID="<project-id>"
export SECRET_NAME="LLM_API_KEY"
export APP_HEALTH_URL="http://localhost:8000/health"
```

## Synthèse des contrôles

| # | Contrôle | Résultat attendu | Preuve |
|---:|---|---|---|
| 1 | Présence du secret | Le secret existe | Sortie de listing ou vue console |
| 2 | Version active | Une version lisible existe | Vue version ou accès latest |
| 3 | Permissions | L’environnement peut lire le secret | Accès réussi sans erreur IAM |
| 4 | Démarrage applicatif | L’application démarre avec le secret | Logs de démarrage / health check |
| 5 | Non-exposition | La clé n’apparaît pas dans logs ou repo | Vérification négative |

## Contrôle 1 — Vérifier que le secret existe

### Par console GCP

- ouvrir Google Secret Manager ;
- vérifier la présence du secret attendu ;
- confirmer le bon projet GCP.

### Par ligne de commande

```bash
gcloud secrets list --project "$GCP_PROJECT_ID"
```

## Contrôle 2 — Vérifier qu’une version active est disponible

```bash
gcloud secrets versions list "$SECRET_NAME" --project "$GCP_PROJECT_ID"
```

- Résultat attendu : au moins une version active est présente.

## Contrôle 3 — Vérifier l’accès au secret depuis l’environnement

### Cas standard via gcloud

```bash
gcloud secrets versions access latest \
  --secret="$SECRET_NAME" \
  --project="$GCP_PROJECT_ID"
```

- Résultat attendu : la commande retourne la valeur du secret.
- Ne pas copier la valeur dans un document partagé.

### Si la lecture échoue

Contrôler d’abord :

- le compte GCP actif ;
- le projet courant ;
- les permissions IAM ;
- l’existence du secret et de sa version.

## Contrôle 4 — Vérifier le contexte d’authentification

### Vérifier le projet actif

```bash
gcloud config get-value project
```

### Vérifier le compte actif

```bash
gcloud auth list
```

### Vérifier les identifiants applicatifs locaux si nécessaire

```bash
gcloud auth application-default print-access-token
```

## Contrôle 5 — Vérifier le démarrage de l’application

Démarrer l’application dans les conditions normales de l’environnement, puis valider la santé du service.

```bash
curl -i "$APP_HEALTH_URL"
```

- Résultat attendu : HTTP `200`.
- Si l’application dépend du secret au démarrage, l’absence d’accès au secret doit provoquer un échec explicite de startup.

## Contrôle 6 — Vérifier l’usage applicatif réel

Une fois l’application démarrée :

- envoyer un appel métier via l’API ;
- confirmer que le traitement LLM fonctionne ;
- vérifier que l’appel au provider n’échoue pas pour cause de clé absente ou invalide.

## Contrôle 7 — Vérifier la non-exposition

### Dans le dépôt Git

Rechercher la présence accidentelle du nom ou de la valeur du secret dans le repo.

```bash
git grep -n "LLM_API_KEY"
```

- Résultat attendu : seules des références de configuration ou de nommage apparaissent, jamais la valeur du secret.

### Dans les logs

- vérifier les logs applicatifs ;
- vérifier les logs de conteneur ;
- vérifier qu’aucune valeur brute n’a été affichée.

## Rotation manuelle — point d’amélioration futur

La rotation n’est pas couverte comme un contrôle déjà validé dans ce projet.

Si une vérification manuelle devait être ajoutée plus tard, elle pourrait suivre cette logique :

1. créer une nouvelle version du secret ;
2. redémarrer le service si le chargement se fait au démarrage ;
3. rejouer un test fonctionnel ;
4. vérifier que l’application utilise toujours correctement le provider.

Cette section doit être considérée comme une **procédure potentielle**, pas comme une preuve d’implémentation déjà validée.

## Guide de dépannage

| Symptôme | Cause probable | Première action |
|---|---|---|
| `PERMISSION_DENIED` | Permissions IAM insuffisantes | Vérifier le compte utilisé et les droits sur le secret. |
| `You do not currently have an active account selected` | Aucun compte gcloud actif | Authentifier le bon compte puis réessayer. |
| Secret introuvable | Mauvais projet ou mauvais nom | Vérifier `project`, `secret name` et version. |
| L’app ne démarre pas | Secret obligatoire inaccessible | Lire les logs de startup puis tester l’accès au secret hors application. |
| Le test local marche mais pas sur VM | Différence d’identité d’exécution | Comparer le compte local et le compte de service de la VM. |

## Trace de validation à conserver

- projet GCP utilisé ;
- nom du secret validé ;
- preuve d’accès réussi ;
- health check applicatif après chargement ;
- preuve négative d’absence d’exposition dans Git et les logs.
