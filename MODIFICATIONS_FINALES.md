# MODIFICATIONS FINALES EXACTES – COPIER-COLLER

---

## 📄 FICHIER 1 : scoring.md

### SECTION À MODIFIER
**Localisation :** "## Règles importantes" → Sous-section "### 3. Le problème prime sur le reste"

### TEXTE ACTUEL À REMPLACER
```
### 3. Le problème prime sur le reste
Un lead sans problème clair doit rarement dépasser :
- 10 à 12 de score
Même si :
- l'entreprise est grande
- le contact est senior
```

### TEXTE À REMPLACER PAR
```
### 3. Le problème prime sur le reste
Un lead sans problème clair doit être fortement pénalisé sur la dimension "besoin" (Problème/Besoin, 0-5).
La présence et clarté du problème déterminent le plafond de qualification possible.

Concrètement :
- Un lead avec un besoin explicite et fortement aligné (score 4-5 sur la dimension) peut atteindre qualified_high même si d'autres critères sont faibles
- Un lead avec un besoin faible, flou ou implicite (score 0-2 sur la dimension) ne doit pas atteindre qualified_high, même si l'entreprise est grande ou le contact est senior
- En cas de doute sur le besoin, réduire le score (règle : "ne jamais inventer")

Exemples de cohérence attendue :
- ICP fit=5, Taille=3, Rôle=5, Besoin=4, Timing=2, Maturité=1, Budget=0 → Score=20 (qualified_high) ✓
- ICP fit=5, Taille=3, Rôle=5, Besoin=1, Timing=2, Maturité=1, Budget=0 → Score=17 (qualified_medium) ✓
- ICP fit=5, Taille=3, Rôle=5, Besoin=0, Timing=2, Maturité=1, Budget=0 → Score=16 (qualified_medium) ✓
```

---

## 📄 FICHIER 2 : output_schema.json

### SECTION À MODIFIER
**Localisation :** Section `"qualification"` et section `"criteria"`

### MODIFICATION 1 : Ajouter documentation avant la section "criteria"

### TEXTE À INSÉRER AVANT `"criteria": {`
```json
  "_field_definitions": {
    "need_clarity_definition": "Évalue la présence, la force et la clarté d'un problème d'exécution managériale. Échelle : 5 = explicitement formulé et directement aligné avec HAIVE; 4 = très clair mais partiellement formulé; 3 = besoin implicite mais identifiable; 2 = besoin flou ou indirect; 1 = très peu de signal; 0 = aucun besoin détectable."
  },
```

### MODIFICATION 2 : Clarifier le champ "confidence" dans "qualification"

**Texte actuel :**
```json
  "confidence": "high | medium | low"
```

**Remplacer par :**
```json
  "confidence": "high | medium | low",
  "_confidence_note": "Reflète la certitude du verdict. HIGH = score clair ET données complètes. MEDIUM = score ambigu OU données partielles. LOW = statut need_more_info OU nombreuses données manquantes."
```

---

## 📄 FICHIER 3 : system_prompt.md

### SECTION À AJOUTER
**Localisation :** Après la section "## CRM note", avant la section "## Cas particuliers"

### TEXTE À INSÉRER COMPLÈTEMENT (NOUVELLE SECTION)

```
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

## 🔍 VÉRIFICATION – Avant d'appliquer

### Checklist de cohérence

- [ ] Règle 3 dans scoring.md parle de "dimension besoin" et donne exemples scores
- [ ] output_schema.json inclut `_field_definitions.need_clarity_definition` ET `_confidence_note`
- [ ] system_prompt.md inclut section "## Calcul du champ Confidence" complète avec exemples et formule
- [ ] Aucun autre texte modifié
- [ ] Aucune clé JSON renommée

### Tests de validation post-modification

**Test 1 :** Appliquer TC_01
- Expected status : qualified_high
- Expected confidence : HIGH (score 20+, données complètes)
- Must match Règle 3 cohérence exemple

**Test 2 :** Appliquer TC_03
- Expected status : qualified_medium
- Expected confidence : MEDIUM (score 12-15, besoin implicite)
- Must match nouvelle logique confidence

**Test 3 :** Appliquer TC_05
- Expected status : need_more_info
- Expected confidence : LOW (données manquantes)
- Must match nouvelle logique confidence

---

## 📋 Résumé des modifications

| Fichier | Section | Action | Type |
|---------|---------|--------|------|
| scoring.md | Règles importantes → Règle 3 | Remplacer (3 para) | Critical |
| output_schema.json | Avant "criteria" | Insérer `_field_definitions` | Documentation |
| output_schema.json | Dans "qualification" | Ajouter `_confidence_note` | Documentation |
| system_prompt.md | Après "## CRM note" | Insérer nouvelle section | Critical |

**Impact :** 0 changements rupture, 4 modifications d'ajout/clarification
**Durée application :** < 5 min (copier-coller)
**Validation :** Exécuter TC_01, TC_03, TC_05 après modifications
