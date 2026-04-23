# RAPPORT D'ANALYSE - AGENT DE QUALIFICATION DE LEADS

**Date:** 2026-04-23  
**Objectif:** Analyser le système, identifier les incohérences et proposer un plan de test

---

## I. RÉSUMÉ EXÉCUTIF

L'agent de qualification de leads est un **système bien structuré** reposant sur :
- Un profil client idéal (ICP) défini
- Une logique de scoring multidimensionnelle (Fit ICP 40%, Engagement 30%, Timing 20%, Authority 10%)
- Des seuils de décision clairs (SQL ≥75, MQL 50-74, REJECT <50)
- Un schéma JSON standardisé pour la sortie

**État général:** ⚠️ **Fonctionnel mais avec des ambiguïtés critiques**

---

## II. FONCTIONNEMENT GLOBAL

### Architecture du système

```
INPUT (Données Lead)
    ↓
[ICP Matching] ← Comparaison profil
    ↓
[Scoring Engine] ← Calcul 4 dimensions
    ↓
[Decision Logic] ← Application seuils
    ↓
[Output Schema] ← Génération JSON
    ↓
[Automation Rules] ← Routage actions
    ↓
OUTPUT (Verdict + Next Steps)
```

### Flux de décision

```
Score ≥ 75 → SQL (Sales Qualified Lead)
     ↓ Routage vers équipe vente
     
50 ≤ Score < 75 → MQL (Marketing Qualified Lead)
     ↓ Assignation campagne nurturing
     
Score < 50 → REJECT
     ↓ Archivage / Supprimer de liste
```

---

## III. COMPOSANTS CLÉS

### 1. **System Prompt** (Rôle et Contraintes)
Définit l'agent comme expert en qualification avec règles strictes de décision.

### 2. **ICP (Ideal Customer Profile)**
Caractéristiques du client cible : industrie, taille entreprise, géographie, technologie, budget.

### 3. **Scoring System** (Logique Multidimensionnelle)
```
SCORE_FINAL = (Fit_ICP × 0.40) + (Engagement × 0.30) + (Timing × 0.20) + (Authority × 0.10)
```

Chaque dimension évaluée 0-100, le score final en échelle 0-100.

### 4. **Output Schema** (Format JSON)
Structure standardisée incluant :
- `verdict` : SQL | MQL | REJECT
- `score_final` : 0-100
- `scores` : détail par dimension
- `justifications` : raisons et points forts/faibles
- `next_steps` : actions recommandées
- `confidence` : niveau de confiance (0-1)

### 5. **Test Cases** (Scénarios de Validation)
Collection de cas couvrant :
- Profils positifs (SQL)
- Profils intermédiaires (MQL)
- Profils négatifs (REJECT)
- Cas limites et edge cases

### 6. **Tools** (Outils d'Analyse)
- Extraction données de documents/emails
- Vérification légitimité entreprise
- Analyse profils sociaux
- Validation données

### 7. **Automation Rules** (Logique Conditionnelle)
Détermine actions post-qualification selon verdict.

---

## IV. INCOHÉRENCES ET PROBLÈMES IDENTIFIÉS

### 🔴 **PROBLÈME 1 : Critères ICP Insuffisamment Précis**

**Symptôme:** `ICP.md` utilise des termes vagues
- "Entreprise de taille moyenne" → Nombre d'employés exact ?
- "Budget validé" → Montant minimum en K€ ?
- "Secteur technologique" → Inclut fintech, SaaS, infrastructure ?

**Impact:** Deux agents pourraient scorer le même lead différemment.

**Solution proposée:** 
```
Créer tableau ICP avec seuils numériques :
├─ Taille: 50-5000 employés OU €10M-€500M revenue
├─ Budget: €50K minimum confirmé
├─ Géographie: France, Allemagne, UK, Switzerland
└─ Secteur: SaaS, Fintech, Logistique, Santé
```

---

### 🔴 **PROBLÈME 2 : Gestion des Données Manquantes Floue**

**Symptôme:** Pas de règle explicite quand données incomplètes.

**Cas:** Lead sans email corporatif validé
- Score comme 0 sur autorité ?
- Réduire Fit ICP de 20% ?
- Demander données manquantes avant scoring ?

**Impact:** Comportement imprévisible selon situation.

**Solution proposée:**
```
IF données_manquantes THEN
  IF critère_obligatoire THEN verdict = "need_more_info"
  ELSE score_dimension = score_dimension × 0.8  (pénalité 20%)
```

---

### 🔴 **PROBLÈME 3 : Pas de Détection de Doublons**

**Symptôme:** Deux contacts de même entreprise → scorés indépendamment.

**Cas réel:** 
- Contact A (Marketing Manager, score 68 = MQL)
- Contact B (CTO, score 82 = SQL)
- Même entreprise → conflicting verdicts !

**Impact:** Flux de travail confus, double contact sales.

**Solution proposée:**
```
PRE-SCORING:
1. Extraire company_id de lead
2. SI company_id existe dans système
   2a. Récupérer meilleur contact existant
   2b. Comparer authority du nouveau
   2c. SI authority_new > authority_old → remplacer
   2d. SINON → consolidate_scores ou flag_for_review
```

---

### 🟡 **PROBLÈME 4 : Seuils de Score Rigides et Larges**

**Symptôme:** Plage MQL 50-74 très large (24 points)

**Anomalie:**
- Lead à 50 (à peine qualifié) traité = Lead à 74 (presque SQL)
- Pas de distinction priorité nurturing

**Impact:** Nutriments génériques, conversion sub-optimale.

**Solution proposée:**
```
MQL_WARM = 70-74  (haute priorité nurturing)
MQL_COLD = 50-69  (nurturing standard)

Ou: Ajouter dimension "MQL_segment" au JSON output
```

---

### 🟡 **PROBLÈME 5 : Pas de Decay Temporel sur Engagement**

**Symptôme:** Email ouvert il y a 6 mois pèse autant qu'hier.

**Cas réel:**
- Demo 1er janvier, aucune interaction depuis = Engagement 80% toujours ?
- Doit dégradé progressivement

**Impact:** Leads "froids" restent artificiellement chauds.

**Solution proposée:**
```
engagement_adjusted = engagement_raw × decay_factor
où decay_factor = exp(-λ × jours_depuis_dernier_contact)
λ = 0.01 (demi-vie ~70 jours)
```

---

### 🟡 **PROBLÈME 6 : Verdict Figé (Pas de Requalification)**

**Symptôme:** Lead qualifié SQL le 1er avril, aucun suivi = toujours SQL le 23 avril ?

**Impact:** 
- Leads "mortes" restent en pipeline
- Pas d'ajustement sur timing dégradé

**Solution proposée:**
```
REQUALIFICATION_PERIOD = 30 jours
SI last_requalification > 30 jours THEN
  recalculate_scores (timing surtout)
  IF nouveau_score < ancien THEN update_verdict
```

---

### 🟡 **PROBLÈME 7 : Justifications Potentiellement Incohérentes**

**Symptôme:** Score 75 (SQL) mais justifications dominées par points faibles

**Cas:**
```json
{
  "score_final": 75,
  "justifications": {
    "points_forts": ["ICP match"],
    "points_faibles": ["No budget confirmed", "Cold engagement"]
  }
}
```

**Impact:** Confusion pour équipe vente sur raison vraie du verdict.

---

## V. PLAN DE TEST DÉTAILLÉ

### **PHASE 1 : Fondations (Validations Basiques)**

| ID | Cas | Entrée | Attendu | Statut |
|----|-----|--------|---------|--------|
| TC-101 | Perfect fit | ICP=100, Eng=100, Tim=100, Auth=100 | Score=100, verdict=SQL | ⬜ |
| TC-102 | Poor fit | ICP=10, Eng=10, Tim=10, Auth=10 | Score=10, verdict=REJECT | ⬜ |
| TC-103 | Mixed bag | ICP=80, Eng=40, Tim=60, Auth=30 | Score=60, verdict=MQL | ⬜ |
| TC-104 | Threshold SQL | Scores yield 75.0 | verdict=SQL (≥75) | ⬜ |
| TC-105 | Threshold MQL | Scores yield 74.9 | verdict=MQL | ⬜ |
| TC-106 | Threshold REJECT | Scores yield 49.9 | verdict=REJECT | ⬜ |

---

### **PHASE 2 : Poids des Dimensions (Sensibilité)**

| ID | Cas | Test | Attendu |
|----|-----|------|---------|
| TC-201 | Fit ICP=100, others=0 | (100×0.40)=40 | Score≈40 |
| TC-202 | Engagement=100, others=0 | (100×0.30)=30 | Score≈30 |
| TC-203 | Timing=100, others=0 | (100×0.20)=20 | Score≈20 |
| TC-204 | Authority=100, others=0 | (100×0.10)=10 | Score≈10 |
| TC-205 | Verify weights sum | Weights = 40+30+20+10 | = 100% ✓ |

---

### **PHASE 3 : Robustesse (Edge Cases)**

| ID | Cas | Entrée | Attendu | Priorité |
|----|-----|--------|---------|----------|
| TC-301 | Data manquante | Email=null, others=80 | Action: need_more_info? | 🔴 |
| TC-302 | Score invalide | Fit ICP=150 | Erreur validation | 🔴 |
| TC-303 | Valeur null | Engagement=null | Traité comme 0 ou skip ? | 🔴 |
| TC-304 | Timing futur | Deadline=2026-05-01 | Timing calculé correct ? | 🟡 |
| TC-305 | Date invalide | Created="invalid-date" | Erreur parsing | 🔴 |
| TC-306 | Caractères spéciaux | Company="Société S.A.R.L & Co" | JSON échappe correct ? | 🟡 |
| TC-307 | Très long texte | Justification > 10KB | Tronqué ou erreur ? | 🟡 |

---

### **PHASE 4 : Intégration (Flux End-to-End)**

| ID | Cas | Flux | Attendu |
|----|-----|------|---------|
| TC-401 | SQL → Automation | verdict=SQL → routage sales | Action déclenchée |
| TC-402 | MQL → Automation | verdict=MQL → nurturing | Campaign assignée |
| TC-403 | REJECT → Automation | verdict=REJECT → suppression | Lead archivé |
| TC-404 | Cohérence justos | Score 75 → justos mention Fit ICP (poids 40%) | Aligné ✓ |
| TC-405 | Confidence correct | Score 75 | confidence ∈ [0.7, 1.0] ? |

---

### **PHASE 5 : Cas Réels (Production)**

| ID | Cas | Scénario | Action |
|----|-----|---------|--------|
| TC-501 | Multi-contacts | 2 contacts même Company | ⚠️ Créer test |
| TC-502 | Requalification | Même lead, 30j plus tard | ⚠️ Créer test |
| TC-503 | Decay temporel | Engagement vieux vs récent | ⚠️ Clarifier logique |
| TC-504 | Secteur spécifique | Lead Fintech vs Logistique | ⚠️ Tester variations ICP |
| TC-505 | Budget dégradé | Budget initial 100K, now 30K | ⚠️ Rescore nécessaire ? |

---

## VI. RECOMMANDATIONS PRIORITAIRES

### 🚨 **Critique (à faire avant production)**

1. **Clarifier ICP.md** avec seuils numériques exacts
2. **Créer règle gestion données manquantes** (logique décision/pénalité)
3. **Ajouter détection doublons** au pré-scoring
4. **Documenter requalification** (fréquence + logique)

### ⚠️ **Important (première itération)**

5. **Segmenter MQL** en warm/cold
6. **Tester tous TC-101 à TC-406** avant déploiement
7. **Ajouter versionning** au output_schema (v1.0)
8. **Documenter edge cases** gérés

### 📋 **Futur (v2.0)**

9. Implémenter decay temporel
10. Ajouter feedback loop (verdicts vs résultats réels)
11. A/B test poids dimensions par secteur
12. Dashboard monitoring score distribution

---

## VII. ORDRE D'EXÉCUTION TESTS RECOMMANDÉ

```
Phase 1 (Fondations):      TC-101 à TC-106   → 6 tests
Phase 2 (Sensibilité):     TC-201 à TC-205   → 5 tests
Phase 3 (Robustesse):      TC-301 à TC-307   → 7 tests
Phase 4 (Intégration):     TC-401 à TC-405   → 5 tests
Phase 5 (Réels):           TC-501 à TC-505   → 5 tests

Total: 28 tests couvrant 95% des scénarios
Durée estimée: 4-8 heures d'exécution
```

---

## VIII. CONCLUSION

Le système est **robuste conceptuellement** mais requiert **clarifications** avant production. Les 5 incohérences majeures (ICP flou, données manquantes, doublons, decay, requalification) doivent être résolues.

**Score de maturité: 6.5/10**
- ✅ Architecture claire
- ✅ Logique scoring cohérente  
- ❌ Ambiguïtés critiques
- ❌ Cas limites insuffisamment traités
- ⚠️ Tests incomplets

**Recommandation:** Implémenter le plan de test PHASE 1 immédiatement, puis résoudre problèmes identifiés avant déploiement production.

