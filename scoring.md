# Scoring — Agent de qualification de leads HAIVE

## Objectif du document

Ce document définit la grille de scoring utilisée par l'agent de qualification.
L'objectif est de transformer une analyse qualitative d'un lead en un score quantifié, explicable et reproductible.
Le scoring ne remplace pas le jugement, mais il structure la décision.

---

## Principe général

Chaque lead est évalué sur plusieurs dimensions clés.
Chaque dimension reçoit un score.
Le score total permet de déterminer :
- le niveau de qualification
- la priorité commerciale
- l'action recommandée

---

## Dimensions de scoring

### 1. ICP Fit (0 à 5)

Mesure l'adéquation globale de l'entreprise avec la cible HAIVE.

5 — Entreprise clairement multi-sites ou distribuée, avec forte dépendance à l'exécution managériale.
4 — Entreprise très proche de l'ICP, avec une structure organisationnelle pertinente.
3 — Entreprise partiellement pertinente (structure ou contexte intéressant mais incomplet).
2 — Pertinence faible mais possible dans certains cas.
1 — Très éloigné de l'ICP.
0 — Hors cible.

---

### 2. Taille et structure (0 à 3)

Mesure la capacité de déploiement et la pertinence organisationnelle.

3 — Entreprise avec une structure significative (ETI ou grand groupe, plusieurs équipes ou sites).
2 — Entreprise structurée mais de taille intermédiaire.
1 — Petite structure avec peu de relais managériaux.
0 — Structure insuffisante pour justifier HAIVE.

---

### 3. Rôle du contact (0 à 5)

Mesure la pertinence et le pouvoir d'action du contact.

5 — Décisionnaire direct ou sponsor potentiel (COO, directeur opérations, directeur réseau, transformation…).
4 — Responsable très influent dans le périmètre.
3 — Manager ou interlocuteur pertinent mais non décisionnaire.
2 — Rôle indirect ou influence limitée.
1 — Rôle très éloigné du sujet.
0 — Aucune pertinence.

---

### 4. Problème / besoin (0 à 5)

Mesure la présence d'un problème lié à l'exécution.

5 — Problème explicitement formulé et directement aligné avec HAIVE.
4 — Problème très clair mais partiellement formulé.
3 — Besoin implicite identifiable.
2 — Besoin flou ou indirect.
1 — Très peu de signal.
0 — Aucun besoin détectable.

---

### 5. Urgence / timing (0 à 3)

Mesure le niveau d'activation du projet.

3 — Projet en cours ou besoin immédiat.
2 — Intérêt actif mais pas urgent.
1 — Curiosité ou exploration.
0 — Aucune urgence.

---

### 6. Maturité digitale / organisationnelle (0 à 2)

Mesure la capacité à adopter une solution comme HAIVE.

2 — Organisation déjà outillée, structurée, avec logique data ou outils.
1 — Maturité intermédiaire.
0 — Très faible maturité.

---

### 7. Budget potentiel (0 à 2)

Estimation indirecte de la capacité à acheter.

2 — Entreprise avec forte capacité d'investissement.
1 — Capacité moyenne.
0 — Faible capacité ou doute important.

---

## Score total

Score maximum : 25

---

## Interprétation du score

### 18 à 25 — Qualified High

Lead très pertinent.

- ICP aligné
- contact pertinent
- problème réel
- potentiel commercial fort

Action recommandée :
- traitement prioritaire
- prise de contact rapide
- assignation directe

---

### 12 à 17 — Qualified Medium

Lead intéressant mais à qualifier davantage.

- bon potentiel
- incertitudes sur certains critères

Action recommandée :
- qualification complémentaire
- questions ciblées
- suivi actif

---

### 6 à 11 — Low Priority

Lead faible mais pas totalement inutile.

- plusieurs signaux faibles
- manque de clarté ou de fit

Action recommandée :
- nurture
- suivi léger
- pas prioritaire

---

### 0 à 5 — Not Qualified

Lead hors cible.

- faible fit
- aucun problème pertinent
- contact non pertinent

Action recommandée :
- disqualification
- archivage

---

## Cas particulier : Need More Info

Indépendamment du score, ce statut doit être utilisé si :
- des informations critiques sont manquantes
- le doute est trop élevé
- l'agent ne peut pas conclure sans enrichissement

Exemples :
- rôle du contact inconnu
- entreprise difficile à identifier
- message trop vague
- secteur ou structure incertaine

Dans ce cas :
- ne pas surinterpréter
- ne pas surqualifier
- lister explicitement les informations manquantes

---

## Règles importantes

### 1. Ne jamais inventer

Si une information n'est pas disponible :
- ne pas la supposer
- ne pas la déduire de manière hasardeuse
- réduire le score en conséquence

---

### 2. Privilégier la prudence

En cas de doute :
- baisser le score
- utiliser "need_more_info"

---

### 3. Le problème prime sur le reste

Un lead sans problème clair doit être fortement pénalisé sur la dimension "besoin" (Problème/Besoin, 0-5).
La présence et clarté du problème déterminent le plafond de qualification possible.

Concrètement :
- Un lead avec un besoin explicite et fortement aligné (score 4-5) peut atteindre qualified_high même si d'autres critères sont faibles
- Un lead avec un besoin faible, flou ou implicite (score 0-2) ne doit pas atteindre qualified_high, même si l'entreprise est grande ou le contact est senior
- En cas de doute sur le besoin, réduire le score (règle : "ne jamais inventer")

Exemples de cohérence attendue :
- ICP fit=5, Taille=3, Rôle=5, Besoin=4, Timing=2, Maturité=1, Budget=0 → Score=20 (qualified_high) ✓
- ICP fit=5, Taille=3, Rôle=5, Besoin=1, Timing=2, Maturité=1, Budget=0 → Score=17 (qualified_medium) ✓
- ICP fit=5, Taille=3, Rôle=5, Besoin=0, Timing=2, Maturité=1, Budget=0 → Score=16 (qualified_medium) ✓

---

### 4. Le rôle est déterminant

Un lead avec :
- ICP parfait
- mais mauvais contact
→ doit être fortement pénalisé

---

### 5. Ne pas survaloriser la taille

Une grande entreprise sans problème identifié :
→ ne doit pas être considérée comme un bon lead

---

### 6. Cohérence globale

Le score final doit être cohérent avec :
- le statut
- la priorité
- la recommandation

Exemple :
Un score de 20 ne peut pas être associé à "low_priority".

---

## Ajustements recommandés (itérations)

Ce scoring est une base.
Il devra être ajusté après tests :
- sur 20 à 50 leads réels
- en analysant les erreurs
- en identifiant les biais (trop optimiste, trop strict, etc.)

---

## Résumé opérationnel

Le scoring permet de transformer une analyse qualitative en décision exploitable.
Il doit rester :
- simple
- explicable
- cohérent
- conservateur

L'objectif n'est pas de maximiser le nombre de leads qualifiés, mais de maximiser la qualité des leads transmis aux équipes commerciales.
