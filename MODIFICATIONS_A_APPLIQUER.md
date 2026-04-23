# MODIFICATIONS À APPLIQUER – VERSIONS FINALES EXACTES

---

## 📄 FICHIER 1 : scoring.md – Règle 3

**Section :** "## Règles importantes" → "### 3. Le problème prime sur le reste"

### ❌ TEXTE ACTUEL À SUPPRIMER
```
### 3. Le problème prime sur le reste
Un lead sans problème clair doit rarement dépasser :
- 10 à 12 de score
Même si :
- l'entreprise est grande
- le contact est senior
```

### ✅ TEXTE À COLLER À LA PLACE
```
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
```

---

## 📄 FICHIER 2 : system_prompt.md – Logique Confidence

**Section :** Ajouter APRÈS "## CRM note", AVANT "## Cas particuliers"

### ✅ TEXTE À COLLER (NOUVELLE SECTION COMPLÈTE)

```markdown
## Calcul du champ Confidence

Le champ "confidence" (high | medium | low) doit être rempli selon cette logique matricielle :

### HIGH Confidence
Les conditions suivantes doivent TOUTES être vraies :
- score ≥ 18 (statut qualified_high)
- missing_information est vide OU contient moins de 2 éléments
- Signification : "Verdict très fiable, données suffisantes pour décision immédiate"

Exemples :
- TC_01 (Retail Group) : score 20-22, entreprise identifiable, rôle clair, problème explicite → HIGH
- TC_02 (Franchise Food) : score 20+, contexte de transformation clair → HIGH

### MEDIUM Confidence
Au moins une de ces conditions est vraie :
- score 12-17 (qualified_medium ou low_priority) ET missing_information est courte
- score ≥ 18 MAIS 2+ éléments dans missing_information (doutes malgré bon score)
- Signification : "Verdict probable mais des doutes ou incertitudes existent"

Exemples :
- TC_03 (Services Plus) : score 12-14, besoin implicite ("améliorer communication"), contact pas décisionnaire → MEDIUM
- TC_04 (Hotel Network) : score 12-15, rôle "Formation" pertinent mais pas opérations → MEDIUM
- TC_01 avec rôle incertain : score 20 mais besoin non complètement clair → MEDIUM

### LOW Confidence
Au moins une de ces conditions est vraie :
- score ≤ 11 (low_priority ou not_qualified)
- statut = need_more_info
- missing_information contient 3+ éléments critiques
- Signification : "Verdict incertain, enrichissement ou clarification nécessaire"

Exemples :
- TC_05 (Lucas Petit) : entreprise "Inconnu", rôle "Consultant", message vague, email perso → LOW (need_more_info)
- TC_06 (StartupTech) : score 6-8 car structure trop petite → LOW
- Un lead avec score 20 mais "rôle inconnú" + "taille inconnue" + "secteur incertain" → LOW

### Règle synthétique
```
confidence = fonction(score, missing_info_count, status)
- score ≥18 ET missing_info < 2 ET status≠need_more_info → HIGH
- (12≤score<18) OU (score≥18 ET missing_info≥2) → MEDIUM
- score<12 OU status=need_more_info OU missing_info≥3 → LOW
```

### Utilisation pratique
- HIGH : Lead prêt pour assign_to_sales sans clarification supplémentaire
- MEDIUM : Lead prêt pour request_more_info ou nurture, avec doutes documentés
- LOW : Lead nécessite enrichissement avant action commerciale (ou discard/blacklist)
```

---

## 📄 FICHIER 3 : CLARIFICATION NEED_CLARITY (document séparé)

### Option 1 : Créer fichier `SCORING_CLARIFICATIONS.md`

**Chemin :** `/Users/enatse/Angent IA - Lead Qualification/:lead-qualification-agent:/SCORING_CLARIFICATIONS.md`

### ✅ CONTENU À CRÉER

```markdown
# Clarifications sur le Scoring

## Dimension 4 : "Need Clarity" (0-5)

### Définition exacte
Cette dimension évalue la **présence, la force et la clarté d'un problème d'exécution managériale** détecté chez le lead.

Elle répond à la question : **"Existe-t-il un problème lié à l'exécution et à la transformation managériale, et comment est-il exprimé ?"**

### Interprétation des niveaux

#### 5 — Problème explicitement formulé et directement aligné
- Le lead mentionne explicitement un problème d'exécution, d'adoption ou d'alignement
- Le problème est clairement lié à la mission HAIVE
- Exemple : "Nous avons du mal à faire appliquer nos décisions dans nos 120 magasins" (TC_01)

#### 4 — Problème très clair mais partiellement formulé
- Le problème est évident mais pas exprimé en ces termes exacts
- Le lead mentionne des symptômes directs : exécution hétérogène, managers débordés, etc.
- Exemple : "Difficultés d'adoption dans nos agences" (TC_09)

#### 3 — Besoin implicite mais identifiable
- Le lead n'exprime pas directement un problème d'exécution
- MAIS le contexte (multi-sites, réseau, transformation) rend le besoin probable
- L'agent doit déduire le besoin de la structure organisationnelle
- Exemple : "Nous cherchons à améliorer la communication avec nos équipes terrain" (TC_03) → besoin sous-jacent d'alignement/exécution

#### 2 — Besoin flou ou indirect
- Le lead mentionne un besoin lointain, très vague, ou sans lien clair avec l'exécution
- Pas assez de signaux pour déduire un vrai besoin d'exécution managériale
- Exemple : "Nous souhaitons des outils pour mieux organiser notre travail" (TC_06)

#### 1 — Très peu de signal
- Quasi aucun signal de besoin d'exécution
- Le lead cherche surtout de l'information ou du contenu générique
- Exemple : "Je suis intéressé par votre solution, pouvez-vous m'en dire plus ?" (TC_05, sans contexte entreprise)

#### 0 — Aucun besoin détectable
- Le lead n'a clairement aucun besoin compatible avec HAIVE
- Exemple : "Je travaille seul et cherche des outils pour structurer mon activité" (TC_07)

### Notes importantes
- Cette dimension est **déterminante** pour la qualification (Règle 3)
- Un lead sans besoin explicite (niveau ≤ 2) ne peut pas atteindre qualified_high
- En cas de doute entre niveaux (ex. : 2 ou 3 ?), appliquer Règle 2 : **"Privilégier la prudence"** → choisir le niveau inférieur

### Cas limites

| Cas | Niveau | Justification |
|-----|--------|---------------|
| "Nous avons des difficultés à standardiser..." | 4-5 | Problème clair, bien formulé |
| "Nous transformons notre organisation..." | 3 | Contexte suggère besoin, mais pas explicite |
| "Nous cherchons une solution de gestion..." | 2 | Trop vague, pas d'enjeu d'exécution évident |
| "Nous sommes une startup en croissance" | 0-1 | Structure trop petite, besoin absent |

### Cohérence avec autres dimensions
Le score "need_clarity" (Dimension 4) doit être cohérent avec :
- **ICP Fit** (Dim 1) : Si ICP poor (1-2), besoin peut rester bas même si mentionné
- **Company Size** (Dim 2) : Si très petite structure (0-1), besoin d'exécution peu probable
- **Role Relevance** (Dim 3) : Si contact très junior (0-1), même un besoin explicite peut être moins pertinent
```

---

## 🎯 RÉSUMÉ APPLICATION

### Fichiers à modifier : 2

| Fichier | Action | Risque |
|---------|--------|--------|
| `scoring.md` | Remplacer Règle 3 | ✅ None (clarification interne) |
| `system_prompt.md` | Ajouter section Confidence | ✅ None (nouvelle section) |

### Fichiers à créer : 1

| Fichier | Action | Usage |
|---------|--------|-------|
| `SCORING_CLARIFICATIONS.md` | Créer nouveau | Documentation opérationnelle |

### Fichiers à NE PAS modifier

| Fichier | Raison |
|---------|--------|
| `output_schema.json` | Keep minimal, no metadata |
| `test_cases.json` | No changes needed |
| `ICP.md` | No changes needed |
| Autres | Out of scope |

---

## ✅ CHECKLIST PRE-APPLICATION

- [ ] `scoring.md` : Règle 3 trouvée et prête à remplacer
- [ ] `system_prompt.md` : Section "## CRM note" localisée (point d'insertion après)
- [ ] Textes copiables sans corruption d'accents ou caractères spéciaux
- [ ] `SCORING_CLARIFICATIONS.md` à créer avec contenu complet

---

## 🧪 VALIDATION POST-APPLICATION

Après modification, valider avec ces 3 cas :

**Test 1 :** TC_01 (Retail Group)
- Expected : qualified_high, score 20+, confidence HIGH
- Check : Règle 3 cohérence appliquée ✓

**Test 2 :** TC_03 (Services Plus)
- Expected : qualified_medium, score 12-15, confidence MEDIUM
- Check : Logique confidence MEDIUM correcte (besoin implicite) ✓

**Test 3 :** TC_05 (Lucas Petit)
- Expected : need_more_info, confidence LOW
- Check : Logique confidence LOW correcte (missing_info) ✓

---

## 📋 PROCHAINES ÉTAPES

1. ✅ Appliquer les 2 modifications (scoring.md + system_prompt.md)
2. ✅ Créer `SCORING_CLARIFICATIONS.md`
3. ⏭️ Tester les 10 cas (TC_01 à TC_10) avec agent
4. ⏭️ Valider cohérence scores + confidence
5. ⏭️ Documenter écarts ou clarifications additionnelles si needed
