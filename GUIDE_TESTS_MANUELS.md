# GUIDE DES TESTS MANUELS – TC_01 à TC_10

**Objectif :** Valider que l'agent applique correctement les modifications (Règle 3 + Confidence)

**Format de rapport :** Pour chaque cas, rapporter le JSON output ou remplir le template fourni

---

## 📋 TEMPLATE DE RAPPORT PAR CAS

```
### TC_XX – [NOM CAS]

**Input :**
- Name: 
- Company:
- Role:
- Message:

**Output reçu :**
- Score: 
- Verdict (status):
- Confidence:
- Reasoning:

**Attendu :**
- Score: [range]
- Verdict:
- Confidence:

**Validations :**
- ☐ Score dans la bonne plage
- ☐ Verdict correct
- ☐ Confidence cohérent avec score + missing_info
- ☐ Reasoning factuel

**Notes / Anomalies :**
```

---

## 🧪 CAS DE TEST 1-10

### TC_01 – Retail Group France

**Input :**
```json
{
  "name": "Jean Dupont",
  "email": "jean.dupont@retailgroup.fr",
  "company": "Retail Group France",
  "role": "Directeur des opérations",
  "message": "Nous avons des difficultés à faire appliquer nos décisions dans nos 120 magasins. Les pratiques varient énormément d'un point de vente à l'autre.",
  "source": "inbound"
}
```

**Attendu :**
- **Score :** 20-25 (qualified_high)
- **Verdict :** qualified_high
- **Confidence :** HIGH (score ≥18, pas de missing_info)
- **Raison :** ICP excellent (multi-sites) + Rôle clé (DO) + Besoin explicite + Timing présent

---

### TC_02 – Franchise Food

**Input :**
```json
{
  "name": "Claire Martin",
  "email": "claire.martin@franchisefood.com",
  "company": "Franchise Food",
  "role": "Directrice réseau",
  "message": "Nous sommes en pleine transformation et avons du mal à aligner nos franchisés sur les nouvelles directives.",
  "source": "inbound"
}
```

**Attendu :**
- **Score :** 20-25 (qualified_high)
- **Verdict :** qualified_high
- **Confidence :** HIGH

---

### TC_03 – Services Plus

**Input :**
```json
{
  "name": "Thomas Leroy",
  "email": "thomas.leroy@servicesplus.fr",
  "company": "Services Plus",
  "role": "Responsable régional",
  "message": "Nous cherchons à améliorer la communication avec nos équipes terrain.",
  "source": "inbound"
}
```

**Attendu :**
- **Score :** 12-17 (qualified_medium)
- **Verdict :** qualified_medium
- **Confidence :** MEDIUM (besoin implicite, pas décisionnaire)
- **Raison :** Besoin implicite (niveau 3) → plafonne qualification

---

### TC_04 – Hotel Network

**Input :**
```json
{
  "name": "Sophie Bernard",
  "email": "sophie.bernard@hotelnetwork.com",
  "company": "Hotel Network",
  "role": "Responsable formation",
  "message": "Nous souhaitons structurer le management de nos équipes sur plusieurs établissements.",
  "source": "inbound"
}
```

**Attendu :**
- **Score :** 12-17 (qualified_medium)
- **Verdict :** qualified_medium
- **Confidence :** MEDIUM

---

### TC_05 – Lucas Petit

**Input :**
```json
{
  "name": "Lucas Petit",
  "email": "lucas.petit@gmail.com",
  "company": "Inconnu",
  "role": "Consultant",
  "message": "Je suis intéressé par votre solution, pouvez-vous m'en dire plus ?",
  "source": "website"
}
```

**Attendu :**
- **Score :** N/A (statut spécial, données manquantes)
- **Verdict :** need_more_info
- **Confidence :** LOW
- **Missing_information :** [entreprise, taille, secteur, besoin]

---

### TC_06 – StartupTech

**Input :**
```json
{
  "name": "Emma Robert",
  "email": "emma.robert@startuptech.io",
  "company": "StartupTech",
  "role": "CEO",
  "message": "Nous sommes une équipe de 10 personnes et cherchons un outil pour mieux organiser notre travail.",
  "source": "inbound"
}
```

**Attendu :**
- **Score :** 6-11 (low_priority)
- **Verdict :** low_priority
- **Confidence :** LOW
- **Raison :** Structure trop petite (10 pers) → besoin d'exécution managériale absent

---

### TC_07 – Freelance

**Input :**
```json
{
  "name": "Paul Girard",
  "email": "paul.girard@freelance.fr",
  "company": "Freelance",
  "role": "Consultant indépendant",
  "message": "Je travaille seul et cherche des outils pour structurer mon activité.",
  "source": "website"
}
```

**Attendu :**
- **Score :** 0-5 (not_qualified)
- **Verdict :** not_qualified
- **Confidence :** LOW
- **Raison :** Anti-ICP (solo indépendant)

---

### TC_08 – Université

**Input :**
```json
{
  "name": "Marie Dubois",
  "email": "marie.dubois@student.edu",
  "company": "Université",
  "role": "Étudiante",
  "message": "Je fais un mémoire sur les outils de management, pouvez-vous répondre à quelques questions ?",
  "source": "email"
}
```

**Attendu :**
- **Score :** 0-5 (not_qualified)
- **Verdict :** not_qualified
- **Confidence :** LOW
- **Raison :** Contexte académique, pas de projet commercial

---

### TC_09 – Bank Network

**Input :**
```json
{
  "name": "Nicolas Morel",
  "email": "nicolas.morel@banknetwork.fr",
  "company": "Bank Network",
  "role": "Directeur transformation",
  "message": "Nous déployons une nouvelle stratégie et rencontrons des difficultés d'adoption dans nos agences.",
  "source": "inbound"
}
```

**Attendu :**
- **Score :** 20-25 (qualified_high)
- **Verdict :** qualified_high
- **Confidence :** HIGH
- **Raison :** Problème clair + Rôle transformation + Multi-sites implicite

---

### TC_10 – Spam Bot

**Input :**
```json
{
  "name": "Spam Bot",
  "email": "contact@seo-agency.com",
  "company": "SEO Agency",
  "role": "Marketing",
  "message": "Boost your SEO with our amazing services!!! Click here now!!!",
  "source": "form"
}
```

**Attendu :**
- **Score :** N/A (statut spécial)
- **Verdict :** spam
- **Confidence :** LOW
- **Raison :** Contenu promotionnel incohérent

---

## 📊 TABLEAU DE SYNTHÈSE ATTENDUE

| TC | Company | Expected Status | Expected Confidence | Priority |
|----|---------|-----------------|-------------------|----------|
| TC_01 | Retail Group | qualified_high | HIGH | Test d'abord |
| TC_02 | Franchise Food | qualified_high | HIGH | Test d'abord |
| TC_03 | Services Plus | qualified_medium | MEDIUM | Test clé (besoin implicite) |
| TC_04 | Hotel Network | qualified_medium | MEDIUM | Normal |
| TC_05 | Lucas Petit | need_more_info | LOW | Normal |
| TC_06 | StartupTech | low_priority | LOW | Normal |
| TC_07 | Freelance | not_qualified | LOW | Normal |
| TC_08 | Université | not_qualified | LOW | Normal |
| TC_09 | Bank Network | qualified_high | HIGH | Test clé (Règle 3) |
| TC_10 | Spam Bot | spam | LOW | Normal |

---

## ✅ VALIDATIONS CLÉS À VÉRIFIER

### Validation 1 : Règle 3 appliquée ?

**Cas clés :** TC_01, TC_09 (qualified_high avec besoin explicite)
```
Vérifier que :
- Score ≥18
- Reasoning mentionne "problème explicite" ou "besoin clair"
- Verdict = qualified_high
```

### Validation 2 : Confidence calculé correctement ?

**Cas clés :** 
- TC_01, TC_02, TC_09 → Should be HIGH (score ≥18, no missing_info)
- TC_03, TC_04 → Should be MEDIUM (score 12-17)
- TC_05, TC_06, TC_10 → Should be LOW (missing_info or score <12)

```
Vérifier que :
- HIGH = score ≥18 ET missing_info vide/courte
- MEDIUM = score 12-17 OU (score ≥18 mais missing_info présent)
- LOW = score <12 OU need_more_info OU many missing_info
```

### Validation 3 : Need Clarity cohérent ?

**Cas clés :** TC_03 (besoin implicite, score 3)
```
Vérifier que :
- TC_03 score entre 12-17 (pas qualified_high malgré ICP bon)
- Reasoning explique "besoin implicite"
- Confidence = MEDIUM (doute sur besoin)
```

---

## 📝 FORMAT DE RAPPORT À ENVOYER

Après avoir testé les 10 cas, rapportez :

```markdown
# RÉSULTATS TESTS TC_01 à TC_10

## Résumé
- Cas exécutés : 10/10
- Cas validés : X/10
- Cas anomalies : Y/10

## Validations clés
- ☐ Règle 3 appliquée (TC_01, TC_09 qualified_high)
- ☐ Confidence HIGH pour score ≥18
- ☐ Need Clarity cohérent (TC_03 MEDIUM)

## Anomalies détectées
[Lister tout ce qui ne match pas avec "Attendu"]

## Exemple anomalie
```
TC_01 : Attendu qualified_high mais reçu qualified_medium
  Raison probable : Besoin scoré trop bas (2 au lieu de 4-5)
```

## Conclusion
[Système fonctionne correctement / Ajustements nécessaires]
```

---

## 🎯 AVANT DE COMMENCER

- [ ] Fichiers modifiés appliqués ? (scoring.md, system_prompt.md)
- [ ] Agent accessible et fonctionnel ?
- [ ] Vous avez les inputs TC_01-TC_10 ci-dessus ?
- [ ] Format de rapport clair ?

**Prêt à tester ? 👉** Lancez les 10 cas et rapportez-moi les résultats dans le format proposé !
