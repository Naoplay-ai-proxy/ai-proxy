# Playbook — Proxy IA gouverné 

Ce playbook décrit **comment l’équipe travaille** (Kanban + qualité + gouvernance) sur l’ensemble du projet :
- Phase 1 : API métier (FastAPI / OpenAPI / tests)
- Phase 2 : intégration Gravitee (plans, policies, routage, quotas)
- Phase 3 : sécurité & gouvernance (OAuth, contrôle domaine, logs gouvernés, filtrage)
- Phase 4 : Google Chat (commande, UX, erreurs)
- Phase 5 : observabilité & pilotage (KPI, dashboards, alerting)

Objectif : **un flux stable**, des règles claires, et une qualité vérifiable.

---

## 1) Working Agreements (règles de collaboration)

- **Petites unités de livraison** : on découpe les tâches en morceaux livrables (évite les “big bang”).
- **Timeboxing** : bloqué > 30–45 min → escalade (message + contexte + erreur + tentative).
- **Changements sensibles = explicitement signalés** : contrat API, auth, quotas, logs, filtrage → description claire + reviewer/owner.
- **Qualité avant vitesse** : pas de “Done” sans DoD, sinon dette technique.
- **Traçabilité minimale** : décision importante = trace (PR, issue, ou note dans docs).

---

## 2) Definition of Ready (DoR)

Une carte peut passer en **Ready** si :
- objectif clair (quoi / pourquoi)
- critères d’acceptation écrits (comment on sait que c’est validé)
- dépendances identifiées (ex: besoin d’un endpoint, d’un plan Gravitee, d’un secret)
- risque identifié si sensible (sécurité, données, coût)
- estimation **relative** (S/M/L) si utile  
  > S/M/L = effort/complexité, **pas** priorité.  

---

## 3) Definition of Done (DoD)

Une carte est **Done** si elle respecte **le type de livrable** (code / config / doc) + les règles de gouvernance.

### 3.1 DoD — Code (FastAPI, libs, scripts, Google Chat, etc.)
- changement livré via PR (review effectuée)
- checks locaux OK (tests/lint) et **CI verte si activée**
- tests ajoutés/mis à jour si applicable  
  *Sinon : justification courte dans la PR (ex: doc-only / changement non testable par pytest)*
- docs mises à jour si le comportement/contrat change

### 3.2 DoD — Configuration (Gravitee, policies, plans, quotas, flows)
- configuration appliquée et testée sur un cas nominal + un cas d’erreur
- preuve/trace : export config, capture, ou note technique (selon vos pratiques)
- si impact prod/sécurité : validation par owner/lead

### 3.3 DoD — Documentation
- doc complète, relue, cohérente avec l’implémentation
- exemple(s) si utile (payload, captures, commandes)

### 3.4 Gouvernance (global, toutes phases)
- pas de secrets commités (tokens, clés, `.env`)
- pas de données sensibles en logs 
- décisions “risquées” explicites (contrat, sécurité, quotas, coûts)

---

## 4) Board policies (Kanban)

### 4.1 Colonnes (exemple)
Backlog → Ready → In Progress → Review → Done

> “Review” = **validation/contrôle qualité** (pas uniquement PR GitHub)

### 4.2 WIP limits (recommandé)
Objectif : éviter l’engorgement.
- In Progress : max 2 cartes par dev
- Review : max 4 (à ajuster par lead si nécessaire)

### 4.3 Entry/Exit conditions
- Backlog → Ready : DoR respecté
- Ready → In Progress : carte priorisée + assignée
- In Progress → Review (selon livrable) :
  - **Code** : tests locaux OK + PR ouverte
  - **Config (Gravitee)** : checklist de config OK + preuve (export/screenshot/note)
  - **Doc** : doc prête + relecture demandée
- Review → Done :
  - DoD respecté
  - validation obtenue (approve PR / validation owner / relecture)

---

## 5) Gestion des incidents (léger)

Un **incident** = impact important, par exemple :
- indisponibilité (API/Gravitee/Google Chat)
- grosse régression fonctionnelle
- fuite potentielle de données (logs, headers, transcripts)
- coûts anormaux (tokens, appels LLM)
- erreurs en chaîne (401/403/429/5xx, timeouts)

### 5.1 Réaction
- créer une carte “INCIDENT” (priorité haute) + assigner un owner
- isoler / corriger / valider (cas nominal + cas erreur)
- noter brièvement la cause et la correction (même 3 lignes)

### 5.2 Post-mortem léger (3–10 lignes)
Après résolution :
- cause racine
- impact
- correction appliquée
- actions de prévention 

---

## 6) Release policy (placeholder)

À activer lorsque le projet a :
- un environnement stable (REC/Préprod) ou un cycle de livraison régulier
- une CI en place (GitHub Actions) et des critères de release définis

Pour l’instant : une “release” = un état stable sur `main` + validation minimale du livrable.
