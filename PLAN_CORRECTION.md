# PLAN DE CORRECTION MINIMAL ET PRIORISÉ

**Objectif :** Corriger UNIQUEMENT les éléments qui bloquent les tests, sans réinventer.

---

## PARTIE 1 : CLASSIFICATION DES INCOHÉRENCES

### 🔴 À CORRIGER IMMÉDIATEMENT (bloquent tests)

| # | Incohérence | Raison |
|----|-------------|--------|
| 2 | **"Need Clarity" mal nommé** | Ambiguïté sémantique bloque scoring dimension 4 |
| 1 | **Incohérence Règle 3** | Contradiction interne : max 10-12 vs. d'autres dimensions = 18+ |
| 7 | **Confidence Level orphelin** | Champ output_schema.json mais AUCUNE logique → impossible à remplir |

### 🟡 À CLARIFIER PLUS TARD (documentation/guidage)

| # | Incohérence | Raison | Impact | Timing |
|----|-------------|--------|--------|--------|
| 3 | "Problème clair" non défini | Guidance imprécise (niveau 3 ou 4 ?) | Soft (agent peut estimer) | Post-tests |
| 4 | Budget jamais observable | Critère inclus mais absent données | Soft (pénalise tous equally) | Post-tests |
| 5 | Priorité règles 3/4/5 floue | Documentation incohérente | Soft (agent arbitre) | Post-tests |
| 6 | Need_more_info vs. score | Pas de guide interaction | Soft (défaut acceptable) | Post-tests |

---

## PARTIE 2 : 3 CORRECTIONS MINIMALES ESSENTIELLES

### **Correction 1 : Résoudre Incohérence Règle 3**

**Problème :** 
- Règle 3 (`scoring.md`) dit : "Un lead sans problème clair doit rarement dépasser 10-12 de score"
- MAIS : icp_fit(5) + company_size(3) + role_relevance(5) = 13 AVANT need_clarity
- DONC : Impossible respecter règle avec ces poids

**Options de correction (choisir une) :**

**Option A (Recommandée) :** Reclassifier Règle 3 comme "guidage soft"
- Reformuler pour refléter réalité mathématique

**Option B :** Ajouter mécanisme "penalty" explicite
- Si need_clarity ≤ 2 → réduire score global de X points

**Option C :** Baisser poids dimensions autres que besoin
- Rendre need_clarity plus prépondérant

---

### **Correction 2 : Clarifier "Need Clarity" – Renommer ou Définir**

**Problème :**
- `scoring.md` Dim 4 : "**Problème / besoin**" (0-5)
  - Rubrique décrit "PRÉSENCE d'un problème"
  - Niveaux : "explicitement formulé", "très clair", "implicite", "flou", "aucun"
  
- `output_schema.json` : "**need_clarity**" 
  - Suggère "clarté du besoin" (semantic différent)

**Cause de l'ambiguïté :**
- Évalues-tu "force du problème détecté" OU "clarté avec laquelle le lead l'exprime" ?

**Impact sur scoring :**
- Cas TC_03 "Améliorer communication" : Besoin existe mais flou
  - Si évalue PRÉSENCE : score 2-3 (faible/flou)
  - Si évalue CLARTÉ : score 2-3 (peu clair)
  - → MÊME résultat, MAIS logique différente

---

### **Correction 3 : Ajouter Logique "Confidence Level"**

**Problème :**
- `output_schema.json` inclut : `"confidence": "high | medium | low"`
- AUCUN fichier ne définit comment calculer confidence
- Agent ne peut pas remplir ce champ sans logique

**Options de correction :**

**Option A (Recommandée) :** Lier confidence au score + missing_information
```
confidence = fonction(score, missing_info_count)
Exemple :
- score ≥18 ET no missing_info → "high"
- score ≥18 ET some missing_info → "medium"
- score <18 OR many missing_info → "low"
```

**Option B :** Lier confidence uniquement au score
```
confidence = fonction(score)
- score ≥18 → "high"
- score 12-17 → "medium"
- score <12 → "low"
```

---

## PARTIE 3 : MODIFICATIONS PRÉCISES, DOCUMENT PAR DOCUMENT

### **MODIFICATION 1 : Résoudre Incohérence Règle 3**

**Fichier :** `scoring.md`

**Section actuelle :** "## Règles importantes" → Règle 3

**Texte actuel :**
```
### 3. Le problème prime sur le reste
Un lead sans problème clair doit rarement dépasser :
- 10 à 12 de score
Même si :
- l'entreprise est grande
- le contact est senior
```

**Correction proposée (Option A – Recommandée):**
```
### 3. Le problème prime sur le reste
Un lead sans problème clair doit être fortement pénalisé sur la dimension "besoin".
Concrètement :
- Un lead avec besoin explicite et fort (4-5) peut atteindre qualified_high même si d'autres critères faibles
- Un lead avec besoin faible ou implicite (0-2) ne doit pas atteindre qualified_high, même si entreprise grande ou contact senior
- En cas de doute sur besoin, réduire score need_clarity (règle : "ne jamais inventer")

Exemple de cohérence attendue :
- ICP=5, Taille=3, Rôle=5, Besoin=4, Timing=2, Maturité=1, Budget=0 → Score=20 (qualified_high) ✓
- ICP=5, Taille=3, Rôle=5, Besoin=1, Timing=2, Maturité=1, Budget=0 → Score=17 (qualified_medium) ✓
```

**Justification :** 
- Respecte réalité mathématique (somme des poids)
- Clarifie que besoin est "déterminant" mais pas seul criterion
- Fournit exemples concrets

---

### **MODIFICATION 2 : Clarifier "Need Clarity" dans output_schema.json**

**Fichier :** `output_schema.json`

**Section actuelle :** `"criteria": { ... }`

**Texte actuel :**
```json
"criteria": {
  "icp_fit": "number (0-5)",
  "company_size": "number (0-3)",
  "role_relevance": "number (0-5)",
  "need_clarity": "number (0-5)",
  ...
}
```

**Correction proposée :**
```json
"criteria": {
  "icp_fit": "number (0-5) — Adéquation profil client",
  "company_size": "number (0-3) — Capacité organisationnelle",
  "role_relevance": "number (0-5) — Pertinence contact",
  "problem_strength": "number (0-5) — Force/clarté du problème d'exécution",
  ...
}
```

**OU (si garder "need_clarity") ajouter sous-section :**

Dans `output_schema.json`, ajouter avant la section "criteria" :

```json
"_schema_notes": {
  "problem_strength_formerly_need_clarity": "Évalue la présence, clarté ET pertinence d'un problème d'exécution managériale. Scoring : 5=explicite aligné, 4=très clair, 3=implicite détectable, 2=flou, 1=très faible signal, 0=aucun"
}
```

**Justification :**
- Renomme en "problem_strength" = sémantique claire
- OU documente que "need_clarity" = "problème/besoin" du scoring.md
- Élimine ambiguïté pour programmeur/QA

---

### **MODIFICATION 3 : Ajouter Logique Confidence dans system_prompt.md**

**Fichier :** `system_prompt.md`

**Section actuelle :** "## Champs obligatoires"

**Texte actuel :**
```
Tu dois toujours remplir :
- lead_summary
- qualification
- criteria
- missing_information
- reasoning_summary
- recommended_next_action
- crm_note
```

**Correction proposée – Ajouter APRÈS cette section :**

```
## Champ Confidence

Le champ "confidence" (high | medium | low) doit être rempli selon cette logique :

**HIGH confidence :**
- score ≥ 18 (qualified_high)
- AND aucune information critique manquante (missing_information vide OU liste courte)
- Signifie : "Je suis certain du verdict"

**MEDIUM confidence :**
- score 12-17 (qualified_medium OR low_priority)
- OR score ≥18 MAIS informations importantes manquantes
- Signifie : "Verdict probable mais des doutes existent"

**LOW confidence :**
- score ≤ 11 (low_priority OR not_qualified)
- OR statut = need_more_info
- OR nombreuses informations critiques manquantes
- Signifie : "Verdict incertain, besoin de clarification"

Exemple :
- TC_01 (Retail Group) : score 22, no missing info → confidence = "high"
- TC_03 (Services Plus) : score 14, besoin implicite → confidence = "medium"
- TC_05 (Lucas Petit) : statut need_more_info → confidence = "low"
```

**Justification :**
- Fournit logique explicite et testable
- Cohérent avec output_schema.json
- Permet validation dans tests

---

## PARTIE 4 : ORDRE ET PRIORITÉ D'APPLICATION

### **Phase 0 (IMMÉDIATE) – Corrections bloquantes**

**Étape 1 :** Modifier `scoring.md` – Règle 3
- Impact : Clarifier cohérence mathématique
- Durée : 10 min
- Critique : OUI (validation tests dépend de ceci)

**Étape 2 :** Modifier `output_schema.json` – Renommer/documenter problem_strength
- Impact : Éliminer ambiguïté sémantique dimension 4
- Durée : 5 min
- Critique : OUI (agent et QA doivent savoir ce qu'ils scorent)

**Étape 3 :** Modifier `system_prompt.md` – Ajouter logique confidence
- Impact : Permettre remplissage champ orphelin
- Durée : 15 min
- Critique : OUI (output JSON invalide sans ceci)

### **Phase 1 (APRÈS TESTS) – Clarifications soft**

- Documenter définition "problème clair" (3 vs. 4 ?)
- Ajouter note sur Budget (critère non observable)
- Clarifier priorité entre Règles 3/4/5
- Documenter interaction need_more_info + score

---

## PARTIE 5 : IMPLÉMENTATION MINIMALE

### **Fichiers à modifier : 2**

1. ✏️ `scoring.md` – 1 section (Règle 3)
2. ✏️ `system_prompt.md` – 1 nouvelle section (Confidence logic)

### **Fichiers à documenter : 1**

3. 📝 `output_schema.json` – 1 annotation (clarifier need_clarity)

### **Fichiers PAS à modifier : 6**

- ❌ `system_prompt.md` – ICP definition (OK)
- ❌ `ICP.md` (OK, cohérent)
- ❌ `test_cases.json` (OK, couvre tous statuts)
- ❌ `tools.md` (OK, pas concerné)
- ❌ `automation_rules.md` (OK, pas concerné)
- ❌ `evaluation_framework.md` (OK, pas concerné)

---

## RÉSUMÉ

| # | Correction | Fichier | Section | Temps | Critique |
|---|-----------|---------|---------|-------|----------|
| 1 | Règle 3 → Cohérence math | scoring.md | Règles importantes | 10 min | 🔴 OUI |
| 2 | Need Clarity → Problem strength | output_schema.json | criteria | 5 min | 🔴 OUI |
| 3 | Confidence → Logique explicite | system_prompt.md | NEW section | 15 min | 🔴 OUI |

**Durée totale :** 30 min  
**Impact :** Fiabilise agent avant tests  
**Risque :** Minimal (corrections dans scope existant)

---

## VALIDATION POST-CORRECTION

Les 3 corrections permettront de :

✅ Exécuter tous 10 cas de test (TC_01-TC_10) sans ambiguïté  
✅ Remplir JSON output complet (confiance incluse)  
✅ Valider cohérence mathématique scoring  
✅ Documenter les 4 incohérences soft pour Phase 1

Les 4 incohérences soft seront résolues après premiers tests = quand on aura observé comportement réel.
