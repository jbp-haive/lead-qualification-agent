# Clarifications sur le Scoring

## Dimension 4 : "Need Clarity" (0-5)

### Définition exacte

Cette dimension évalue la **présence, la force et la clarté d'un problème d'exécution managériale** détecté chez le lead.

Elle répond à la question : **"Existe-t-il un problème lié à l'exécution et à la transformation managériale, et comment est-il exprimé ?"**

---

## Interprétation des niveaux

### 5 — Problème explicitement formulé et directement aligné

Le lead mentionne explicitement un problème d'exécution, d'adoption ou d'alignement.
Le problème est clairement lié à la mission HAIVE.

**Exemple :** "Nous avons du mal à faire appliquer nos décisions dans nos 120 magasins" (TC_01)

---

### 4 — Problème très clair mais partiellement formulé

Le problème est évident mais pas exprimé en ces termes exacts.
Le lead mentionne des symptômes directs : exécution hétérogène, managers débordés, difficulté d'adoption, etc.

**Exemple :** "Difficultés d'adoption dans nos agences" (TC_09)

---

### 3 — Besoin implicite mais identifiable

Le lead n'exprime pas directement un problème d'exécution.
MAIS le contexte (multi-sites, réseau, transformation) rend le besoin probable.
L'agent doit déduire le besoin de la structure organisationnelle et du message.

**Exemple :** "Nous cherchons à améliorer la communication avec nos équipes terrain" (TC_03)
→ Besoin sous-jacent d'alignement et d'exécution décentralisée identifiable mais pas explicite

---

### 2 — Besoin flou ou indirect

Le lead mentionne un besoin lointain, très vague, ou sans lien clair avec l'exécution managériale.
Pas assez de signaux pour déduire un vrai besoin d'exécution.

**Exemple :** "Nous souhaitons des outils pour mieux organiser notre travail" (TC_06)

---

### 1 — Très peu de signal

Quasi aucun signal de besoin d'exécution.
Le lead cherche surtout de l'information ou du contenu générique.

**Exemple :** "Je suis intéressé par votre solution, pouvez-vous m'en dire plus ?" (TC_05, sans contexte entreprise)

---

### 0 — Aucun besoin détectable

Le lead n'a clairement aucun besoin compatible avec HAIVE.

**Exemple :** "Je travaille seul et cherche des outils pour structurer mon activité" (TC_07)

---

## Notes importantes

- Cette dimension est **déterminante** pour la qualification (Règle 3 dans scoring.md)
- Un lead sans besoin explicite (niveau ≤ 2) ne peut pas atteindre qualified_high
- En cas de doute entre niveaux (ex. : 2 ou 3 ?), appliquer Règle 2 : **"Privilégier la prudence"** → choisir le niveau inférieur
- Si le besoin existe mais le lead n'en parle pas du tout → c'est un niveau 0 ou 1, pas 3 (ne jamais inventer)

---

## Cas limites de scoring

| Cas | Niveau | Justification |
|-----|--------|---------------|
| "Nous avons des difficultés à standardiser les pratiques..." | 4-5 | Problème clairement énoncé, bien formulé |
| "Nous transformons notre organisation et devons aligner les équipes..." | 3 | Contexte suggère besoin d'exécution, mais pas totalement explicite |
| "Nous cherchons une solution de gestion d'équipes..." | 2 | Trop vague, enjeu d'exécution pas évident |
| "Nous sommes une startup en croissance..." | 0-1 | Structure trop petite, besoin d'exécution managériale absent |
| Aucune mention du besoin (email promo, demande de devis générique) | 0 | Pas de signal détectable |

---

## Cohérence avec autres dimensions

Le score "need_clarity" (Dimension 4) doit être cohérent avec :

### Avec ICP Fit (Dim 1)
- Si ICP poor (1-2), besoin peut rester bas même s'il est mentionné
- Si ICP excellent (4-5), besoin mentionné → score need_clarity s'élève

### Avec Company Size (Dim 2)
- Si structure très petite (0-1), besoin d'exécution managériale peu probable
- Même un besoin explicite reste limité si l'entreprise est trop petite

### Avec Role Relevance (Dim 3)
- Si contact très junior (0-1), même un besoin explicite exprimé par lui peut être moins pertinent
- Contact décisionnaire (4-5) qui exprime besoin clair → besoin_clarity score haut

---

## Exemples détaillés de scoring

### Exemple 1 : TC_01 (Retail Group)

**Message :** "Nous avons des difficultés à faire appliquer nos décisions dans nos 120 magasins. Les pratiques varient énormément d'un point de vente à l'autre."

- Besoin clair ? OUI, explicitement formulé
- Lié à HAIVE ? OUI (exécution, standardisation, multi-sites)
- Aligné ? OUI (difficulté → solution d'exécution)

**Score need_clarity : 5**

---

### Exemple 2 : TC_03 (Services Plus)

**Message :** "Nous cherchons à améliorer la communication avec nos équipes terrain."

- Besoin explicite ? NON (ne dit pas "difficulté")
- Contexte ? Services Plus, Responsable Régional → multi-sites probable
- Besoin déductible ? OUI (communication terrain + responsable régional = besoin d'alignement)

**Score need_clarity : 3**
(Implicite mais identifiable à partir du contexte)

---

### Exemple 3 : TC_05 (Lucas Petit)

**Message :** "Je suis intéressé par votre solution, pouvez-vous m'en dire plus ?"

- Besoin mentionné ? NON
- Contexte ? Consultant inconnu, email perso
- Besoin déductible ? NON (aucune indication)

**Score need_clarity : 0 ou 1**
(Aucun signal ou très faible)

---

## Interaction avec Règle 3

La Règle 3 du scoring.md spécifie :

> Un lead sans problème clair doit être fortement pénalisé sur la dimension "besoin"...
> Un lead avec un besoin explicite et fortement aligné (score 4-5) peut atteindre qualified_high même si d'autres critères sont faibles.
> Un lead avec un besoin faible, flou ou implicite (score 0-2) ne doit pas atteindre qualified_high, même si l'entreprise est grande ou le contact est senior.

Cela signifie :
- **Score 0-1** → Limite strictement la qualification (max low_priority)
- **Score 2** → Besoin trop flou, pénalité sévère sur qualification finale
- **Score 3** → Besoin implicite, qualification possible mais limitée
- **Score 4-5** → Besoin clair, qualification peut atteindre qualified_high

---

## Checklist pour scorer need_clarity

Avant d'assigner un score, vérifier :

- [ ] Le lead mentionne-t-il explicitement un problème ? (5 ou 4)
- [ ] Le problème mentionné est-il lié à l'exécution ou à la transformation ? (4 ou 3)
- [ ] Le contexte (secteur, taille, rôle) suggère-t-il un besoin même non explicite ? (3 ou 2)
- [ ] Y a-t-il au moins un faible signal de besoin ? (1)
- [ ] Aucun signal du tout ? (0)

En cas d'hésitation → choisir le score inférieur (Règle 2 : "Privilégier la prudence")
