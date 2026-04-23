# ANALYSE RÉELLE DU SYSTÈME DE QUALIFICATION DE LEADS

**Date:** 2026-04-23  
**Basé uniquement sur les fichiers du dossier**

---

## I. RÉSUMÉ DU SYSTÈME EXACT

### Architecture
```
Lead Input → Analyse 7 critères → Score 0-25 → Déterminer statut → Recommander action → JSON Output
```

### Critères de Scoring (7 dimensions)

| Dimension | Échelle | Description |
|-----------|---------|-------------|
| icp_fit | 0-5 | Adéquation entreprise avec cible HAIVE |
| company_size | 0-3 | Capacité déploiement et pertinence organisationnelle |
| role_relevance | 0-5 | Pertinence et pouvoir d'action du contact |
| need_clarity | 0-5 | Présence d'un problème lié à l'exécution |
| timing | 0-3 | Niveau d'activation du projet |
| maturity | 0-2 | Capacité à adopter une solution |
| budget | 0-2 | Capacité estimée à acheter |
| **TOTAL** | **0-25** | **Somme de tous les critères** |

### Mapping Score → Statut

| Score | Statut | Action |
|-------|--------|--------|
| 18-25 | **qualified_high** | assign_to_sales (traitement prioritaire) |
| 12-17 | **qualified_medium** | request_more_info (qualification complémentaire) |
| 6-11 | **low_priority** | nurture (suivi léger) |
| 0-5 | **not_qualified** | discard (archivage) |

### Cas Spéciaux

- **need_more_info** : Indépendamment du score, si données critiques manquantes
- **spam** : Si message incohérent ou contenu promotionnel

### Format Output JSON

```json
{
  "lead_summary": { company, role, sector, country },
  "qualification": { status, score, priority, confidence },
  "criteria": { icp_fit, company_size, role_relevance, need_clarity, timing, maturity, budget },
  "missing_information": [ "list" ],
  "reasoning_summary": "max 2-3 phrases factuelles",
  "recommended_next_action": "assign_to_sales | request_more_info | nurture | discard | blacklist",
  "crm_note": "court, actionnable"
}
```

---

## II. DÉFINITION STRICTE DE L'ICP

### Cible Prioritaire

**Type d'organisation :**
- Multi-sites ou distribuées (réseau, franchise, retail, hôtellerie, services)
- Population managériale significative
- Décision centralisée, exécution décentralisée

**Secteurs prioritaires :**
- Retail / Distribution
- Restauration / Franchises
- Hôtellerie / Tourisme
- Immobilier en réseau
- Banque / Assurance de réseau
- Services terrain multi-sites
- Industrie avec encadrement intermédiaire important

**Problème clé à détecter :**
Les décisions prises au siège ne s'exécutent pas homogènement sur le terrain.

### Interlocuteurs Très Pertinents

- COO, Directeur Opérations, Directeur Réseau
- Directeur Transformation, Directeur Excellence Opérationnelle
- Responsable Transformation Opérationnelle

### Signaux Positifs

- Difficulté à faire passer les décisions
- Exécution hétérogène selon sites/managers
- Managers insuffisamment outillés
- Transformation en cours

### Anti-ICP

- Étudiants, freelances, auto-entrepreneurs
- Très petites structures mono-site
- Demandes académiques exploratoires
- Aucun management intermédiaire

---

## III. CAS DE TEST PRÉSENTS (10 cas dans test_cases.json)

### ✅ Cas Attendus comme Qualified High (18-25)

**TC_01 :** Jean Dupont - Retail Group France (120 magasins), Directeur Opérations
- Message : "Difficultés à faire appliquer décisions, pratiques varient"
- Fit attendu : HIGH ✓

**TC_02 :** Claire Martin - Franchise Food, Directrice Réseau
- Message : "Transformation en cours, mal à aligner franchisés sur directives"
- Fit attendu : HIGH ✓

**TC_09 :** Nicolas Morel - Bank Network, Directeur Transformation
- Message : "Difficultés d'adoption dans agences"
- Fit attendu : HIGH ✓

### ⚠️ Cas Attendus comme Qualified Medium (12-17)

**TC_03 :** Thomas Leroy - Services Plus, Responsable Régional
- Message : "Améliorer communication avec équipes terrain"
- Fit attendu : MEDIUM ✓

**TC_04 :** Sophie Bernard - Hotel Network, Responsable Formation
- Message : "Structurer management équipes sur plusieurs établissements"
- Fit attendu : MEDIUM ✓

### ❓ Cas Attendus comme Need More Info

**TC_05 :** Lucas Petit - Email gmail, Consultant
- Entreprise inconnue, rôle flou, message trop vague
- Données critiques manquantes ✓

### 📊 Cas Attendus comme Low Priority (6-11)

**TC_06 :** Emma Robert - StartupTech, CEO
- 10 personnes, pas de multi-sites
- Taille insuffisante → LOW PRIORITY ✓

### ❌ Cas Attendus comme Not Qualified (0-5)

**TC_07 :** Paul Girard - Freelance Solo
- Anti-ICP direct (indépendant solo)
- NOT QUALIFIED ✓

**TC_08 :** Marie Dubois - Université, Étudiante
- Mémoire académique
- NOT QUALIFIED ✓

### 🚫 Cas Attendus comme Spam

**TC_10 :** Spam Bot - "Boost your SEO!!!"
- Contenu promotionnel incohérent
- SPAM ✓

---

## IV. INCOHÉRENCES RÉELLES IDENTIFIÉES

### 🔴 INCOHÉRENCE 1 : Critère "Need Clarity" mal nommé dans le contexte

**Problème :** 
- Dans `scoring.md`, la dimension 4 s'appelle "Problème / besoin" (0-5)
- Dans `output_schema.json`, la même dimension s'appelle "need_clarity"
- Le nom "need_clarity" suggère "clarté du besoin" mais le scoring decrit "présence du problème"

**Impact :**
- Flou sur ce qui est évalué exactement : présence/force du problème OU clarté de l'expression du problème ?

**Exemple concret :**
- Lead TC_03 : "Améliorer communication" → problème implicite (score ?) ou besoin flou (pénalité ?)

**Conséquence :**
- Deux agents pourraient scorer différemment le même lead sur cette dimension

---

### 🔴 INCOHÉRENCE 2 : Règle "Problème prime sur le reste" vs. Autres dimensions

**Problème :**
- `scoring.md` Règle 3 : "Un lead sans problème clair doit rarement dépasser 10-12 de score"
- MAIS : Les autres dimensions (taille, rôle, ICP) peuvent totaliser jusqu'à 18 (5+3+5+2+2)
- DONC : Même un lead SANS problème fort pourrait scorer >10 si autres critères forts

**Exemple problématique :**
- Grande entreprise (icp_fit=5, company_size=3) + Bon contact (role_relevance=5)
- Mais: Problème faible ou implicite (need_clarity=1 seulement)
- Total: 5+3+5+1+3+2+2 = 21 → qualified_high

**Mais règle 3 dit :** "sans problème clair → max 10-12"

**Incohérence :**
- 21 > 12 → Viole la règle 3

---

### 🟡 INCOHÉRENCE 3 : Absence de clarté sur "Problème implicite vs. explicite"

**Problème :**
- `scoring.md` Dimension 4 décrit 5 niveaux :
  - 5 = "explicitement formulé et aligné"
  - 4 = "très clair mais partiellement formulé"
  - 3 = "Besoin implicite identifiable"
  - 2 = "Besoin flou ou indirect"
  - 1 = "Très peu de signal"
  - 0 = "Aucun besoin"

**Mais `system_prompt.md` Règle 3 dit :**
- "Un lead sans problème CLAIR ne doit pas être fortement qualifié"
- Qu'est-ce que "clair" ? ≥4 ou ≥3 ?

**Cas réel (TC_03, TC_04) :**
- Ces cas sont attendus en "qualified_medium"
- Mais le message suggère un besoin implicite (score 3 ?)
- Comment atteindre 12-17 avec need_clarity=3 ?

**Incohérence :**
- Pas de guidance sur la baisse de score pour besoin implicite

---

### 🟡 INCOHÉRENCE 4 : "Budget" évalué sur données insuffisantes

**Problème :**
- `scoring.md` Dimension 7 (Budget 0-2) :
  - 2 = "Entreprise avec forte capacité d'investissement"
  - 1 = "Capacité moyenne"
  - 0 = "Faible capacité ou doute important"

- AUCUN cas de test (TC_01 à TC_10) ne mentionne jamais le budget
- AUCUN lead n'indique sa capacité d'investissement

**Impact :**
- Comment scorer le budget de TC_01 sans données ?
- Déduire du secteur (Retail = riche) ? → "Ne jamais inventer"
- Scorer 0 faute de données ? → Pénalise tous les leads equally

**Incohérence :**
- Dimension incluse dans scoring mais jamais observable dans les données de leads

---

### 🟡 INCOHÉRENCE 5 : Règle 4 (Rôle) vs. Règle 1 (Taille) – Priorité floue

**Problème :**
- `scoring.md` Règle 4 : "Un lead avec ICP parfait mais mauvais contact → fortement pénalisé"
- `scoring.md` Règle 5 : "Ne pas survaloriser la taille"
- `scoring.md` Règle 3 : "Le problème prime sur le reste"

**Mais l'ordre de priorité n'est pas clair :**
1. Problème > Reste ? (Règle 3)
2. Rôle > Taille ? (Règle 4+5)
3. Problème > Rôle > Taille ? (Inféré mais pas explicite)

**Cas problématique (imaginons) :**
- ICP=4, Taille=2, Rôle=1 (mauvais contact), Need=4, Timing=2, Maturity=1, Budget=0
- Score = 14 → qualified_medium
- Mais "mauvais contact" = forte pénalité selon Règle 4
- Score 14 reflète-t-il cette pénalité ou pas ?

**Incohérence :**
- Pas de mécanisme explicite de pénalité, seulement des "pistes"

---

### 🟡 INCOHÉRENCE 6 : Missing Information – Statut "need_more_info" vs. Score

**Problème :**
- `scoring.md` : "need_more_info indépendamment du score"
- `system_prompt.md` : "Mapping score → statut" (0-5, 6-11, 12-17, 18-25)
- `output_schema.json` : statut = "qualified_high | ... | need_more_info | ... | spam"

**Question non résolue :**
- Si un lead a score=20 mais données critiques manquantes → statut "need_more_info" ?
- OU attendre que toutes les données soient complètes avant scoring ?
- OU calculer score et ajouter "need_more_info" comme flag supplémentaire ?

**Cas TC_05 (Lucas Petit) :**
- Données largement insuffisantes → need_more_info ✓
- Mais aucune spécification du score partiel ou par défaut

**Incohérence :**
- Pas de guide sur "score + need_more_info ensemble" vs. "need_more_info seul sans score"

---

### 🟡 INCOHÉRENCE 7 : Confidence Level – Pas défini dans les critères

**Problème :**
- `output_schema.json` inclut champ **"confidence": "high | medium | low"**
- MAIS aucun fichier (scoring.md, system_prompt.md) n'explique comment calculer confidence
- Quelle relation entre score et confidence ?
  - Score 25 = confidence "high" ?
  - Score 20 + missing_information = confidence "low" ?

**Impact :**
- Aucun guide pour remplir correctement ce champ

**Incohérence :**
- Champ présent dans schema mais pas défini dans logique de scoring

---

## V. INCOHÉRENCES DÉTECTÉES – RÉSUMÉ

| # | Incohérence | Sévérité | Origine |
|---|-------------|----------|---------|
| 1 | "Need Clarity" vs. "Problème/Besoin" (nom) | 🔴 | scoring.md ≠ output_schema.json |
| 2 | Règle 3 (max 10-12) vs. autres dimensions (peut atteindre 21) | 🔴 | scoring.md (contradiction interne) |
| 3 | "Problème clair" non défini (≥3 ou ≥4 ?) | 🟡 | system_prompt.md vs. scoring.md |
| 4 | Budget (Dim 7) : données jamais présentes dans les leads | 🟡 | test_cases.json |
| 5 | Priorité entre Problème/Rôle/Taille pas explicite | 🟡 | scoring.md (règles 3, 4, 5) |
| 6 | "need_more_info" : statut seul ou avec score ? | 🟡 | system_prompt.md ≠ scoring.md |
| 7 | Confidence Level : pas de logique de calcul | 🟡 | output_schema.json (orphelin) |

---

## VI. PLAN DE TEST BASÉ SUR test_cases.json

### Test Actuels Disponibles (10 cas)

**PHASE A : Validation Verdicts Attendus**

| ID | Cas | Expected | Test |
|----|-----|----------|------|
| TC_01 | Retail Group (multi-sites, DO, problème) | qualified_high | Vérifier score ≥18 |
| TC_02 | Franchise Food (réseau, DIR, transformation) | qualified_high | Vérifier score ≥18 |
| TC_09 | Bank Network (direction transfo, adoption) | qualified_high | Vérifier score ≥18 |
| TC_03 | Services Plus (communication équipes) | qualified_medium | Vérifier 12≤score≤17 |
| TC_04 | Hotel Network (structurer management) | qualified_medium | Vérifier 12≤score≤17 |
| TC_05 | Lucas Petit (données manquantes) | need_more_info | Vérifier list missing_info |
| TC_06 | StartupTech (10 pers, mono-site) | low_priority | Vérifier 6≤score≤11 |
| TC_07 | Freelance (solo) | not_qualified | Vérifier 0≤score≤5 |
| TC_08 | Université (étudiant) | not_qualified | Vérifier 0≤score≤5 |
| TC_10 | Spam Bot (SEO!!!) | spam | Vérifier statut=spam |

### Tests Manquants (à créer)

**PHASE B : Validation Interne Scoring**

- **TC_11 :** Cas "Problème très clair" → besoin_clarté=5 → score devrait être ≥18
- **TC_12 :** Cas "Problème implicite" → besoin_clarté=3 → score devrait être 12-17 ?
- **TC_13 :** Cas "ICP excellent + mauvais contact" → vérifier pénalité rôle
- **TC_14 :** Cas "Grande entreprise mono-site" → vérifier taille ne suffit pas

**PHASE C : Edge Cases**

- **TC_15 :** Score exact 18 (boundary qualified_high)
- **TC_16 :** Score exact 12 (boundary qualified_medium)
- **TC_17 :** Score exact 6 (boundary low_priority)
- **TC_18 :** Tous les critères = 0 → score 0

**PHASE D : Champs Orphelins**

- **TC_19 :** Vérifier remplissage champ "confidence" (logique pas définie)
- **TC_20 :** Vérifier remplissage "missing_information" (quand l'appliquer ?)

---

## VII. LIMITATIONS ACTUELLES

### Ce qui fonctionne clairement
✅ Structure scoring 7 dimensions sur 25 points  
✅ Mapping score → statut défini  
✅ 10 cas de test couvrant gamme entière  
✅ ICP bien défini et opérationnel  
✅ Règles anti-surqualification claires  

### Ce qui n'est pas clair
❓ Nom dimension "need_clarity" vs. sémantique réelle  
❓ Budget (critère inclus mais jamais observable)  
❓ Confidence (champ schema mais pas de logique)  
❓ Need_more_info (statut vs. score)  
❓ Priorités entre règles (3, 4, 5 du scoring.md)  

### Incertitudes sans réponse
- Si données manquantes → score réduit proportionnellement ? OU "need_more_info" SEUL ?
- Dimension "need_clarity" = force du problème OU clarté du besoin ?
- Si "problème implicite" (3/5) → peut atteindre qualified_medium (12-17) ?

---

## VIII. CONFESSION

**Ce que j'ai mal interprété :** 
❌ J'ai inventé un système SQL/MQL sur 100 points qui n'existe pas  
❌ J'ai créé des pondérations 40/30/20/10 inexistantes  
❌ J'ai proposé des améliorations basées sur ce système fictif  

**C'est une erreur critique. Les fichiers définissent un système complètement différent (25 points, 7 dimensions).**

---

## IX. RECOMMANDATION

Avant implémentation en production :

1. **Clarifier Incohérence 2** : Règle 3 (max 10-12 sans problème) vs. autres dimensions  
2. **Clarifier Incohérence 3** : Définir "besoin clair" (niveau ≥3 ou ≥4 ?)  
3. **Valider tous 10 cas de test** et créer PHASE B, C, D  
4. **Documenter** : confidence_calculation, need_more_info_logic, budget_inference

**Score maturité réel : 7.5/10**
- Architecture claire et testable ✓
- 2 incohérences critiques (Règles 3 + 2)
- 5 incohérences mineures mais présentes
- 10 cas de test solides + PHASE supplémentaires nécessaires
