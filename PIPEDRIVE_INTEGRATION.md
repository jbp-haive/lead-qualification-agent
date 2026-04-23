# Intégration Pipedrive – Agent de Qualification HAIVE

**Guide de configuration pour qualifier automatiquement les leads dans Pipedrive**

---

## 🎯 Vue d'ensemble

L'agent se connecte à Pipedrive de 3 façons:

1. **API REST** – Appels manuels ou depuis des workflows
2. **Webhooks** – Déclenche une qualification automatique quand un lead arrive
3. **Zapier/Make** – Sans code, via automation

---

## Option 1: API REST (Recommandé)

### Démarrer l'API

```bash
cd ":lead-qualification-agent:"
pip install flask
python3 api.py
```

L'API écoute sur `http://localhost:5000`

### Endpoints disponibles

#### 1. Vérifier le statut
```bash
curl http://localhost:5000/health
```

#### 2. Qualifier un lead
```bash
curl -X POST http://localhost:5000/qualify \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jean Dupont",
    "company": "Retail Group",
    "role": "Directeur opérations",
    "message": "Nous avons des difficultés à faire appliquer nos décisions dans nos magasins",
    "source": "pipedrive"
  }'
```

**Réponse:**
```json
{
  "lead_summary": {...},
  "qualification": {
    "status": "qualified_high",
    "score": 21,
    "confidence": "HIGH"
  },
  "criteria": {...},
  "recommended_next_action": "assign_to_sales",
  ...
}
```

#### 3. Qualifier plusieurs leads (batch)
```bash
curl -X POST http://localhost:5000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "leads": [
      {"name": "Lead 1", "company": "...", ...},
      {"name": "Lead 2", "company": "...", ...}
    ]
  }'
```

---

## Option 2: Webhooks Pipedrive (Automatique)

### Configuration

1. **Installer l'API** sur un serveur accessible (localhost ne fonctionne pas)
   - Ex: `https://votre-api.com:5000`

2. **Configurer le webhook dans Pipedrive**
   - Allez à: **Settings → Custom integrations → Webhooks**
   - Cliquez **"Add webhook"**
   - URL: `https://votre-api.com:5000/pipedrive/webhook`
   - Events: Cochez **"Person added"** ou **"Deal added"**
   - Cliquez **Save**

3. **Quand un nouveau lead arrive:**
   - Pipedrive appelle l'API
   - L'agent qualifie automatiquement
   - Le résultat revient à Pipedrive

### Utiliser les résultats dans Pipedrive

Une fois les webhooks actifs, créez un workflow Pipedrive qui:

1. **Écoute** les nouveaux leads (persons ou deals)
2. **Appelle** l'API (via custom action)
3. **Stocke** le résultat dans des custom fields:
   - `haive_score` (nombre)
   - `haive_status` (texte)
   - `haive_confidence` (texte)
   - `haive_action` (texte)

---

## Option 3: Zapier / Make (Sans code)

### Avec Zapier

1. **Créez une Zap:**
   - Trigger: Pipedrive → "New Person"
   - Action: Webhooks by Zapier → "POST"
   - URL: `https://votre-api.com:5000/qualify`
   - Body: Mappez les champs Pipedrive

2. **Exemple de mapping:**
   ```
   name → name (du trigger)
   company → org_id.name
   role → job_title
   message → notes
   source → "zapier"
   ```

3. **Ajouter une action Follow-up:**
   - Pipedrive → "Update Person"
   - Remplir les custom fields avec les résultats Zapier

### Avec Make (Integromat)

Processus similaire:
1. Module HTTP → POST vers l'API
2. Module Pipedrive → Mettre à jour la personne
3. Mapper les résultats aux custom fields

---

## Configuration des Custom Fields Pipedrive

Pour stocker les résultats, créez ces custom fields:

| Nom | Type | Description |
|-----|------|-------------|
| `haive_score` | Numéro (0-25) | Score de qualification |
| `haive_status` | Liste | `qualified_high`, `qualified_medium`, `low_priority`, `need_more_info`, `not_qualified`, `spam` |
| `haive_confidence` | Liste | `HIGH`, `MEDIUM`, `LOW` |
| `haive_action` | Texte | `assign_to_sales`, `request_more_info`, `nurture`, `discard`, `blacklist` |
| `haive_reasoning` | Texte long | Explication du scoring |

**Pour créer ces fields:**
1. Allez à **Settings → Custom fields**
2. Sélectionnez **Persons** (ou Deals)
3. Cliquez **"Add custom field"**
4. Configurez comme ci-dessus

---

## Automatisation dans Pipedrive

### Workflow 1: Qualifier et assigner

```
Trigger: Person ajoutée
  ↓
Action: Appeler l'API de qualification
  ↓
Condition: Si status = "qualified_high"
  ↓
Action: Assigner à l'équipe Sales
  ↓
Action: Mettre à jour custom field "haive_status"
```

### Workflow 2: Qualifier et filtrer

```
Trigger: Deal créé
  ↓
Action: Appeler l'API
  ↓
Condition: Si confidence = "LOW"
  ↓
Action: Ajouter au tag "À enrichir"
  ↓
Action: Envoyer email pour collecte info
```

### Workflow 3: Spam automatique

```
Trigger: Person ajoutée
  ↓
Action: Appeler l'API
  ↓
Condition: Si status = "spam"
  ↓
Action: Ajouter au tag "Spam"
  ↓
Action: Archiver
```

---

## Exemples d'intégration

### Python (pour votre CRM)

```python
import requests

def qualify_pipedrive_lead(pipedrive_person_id):
    """Qualifier un lead Pipedrive"""
    
    # Récupérer les données depuis Pipedrive
    person = pipedrive.persons.get(pipedrive_person_id)
    
    # Préparer pour qualification
    lead_data = {
        "name": person['name'],
        "company": person['org_id']['name'],
        "role": person.get('job_title', ''),
        "message": person.get('notes', ''),
        "source": "pipedrive"
    }
    
    # Appeler l'API
    response = requests.post(
        'http://localhost:5000/qualify',
        json=lead_data
    )
    
    result = response.json()
    
    # Mettre à jour Pipedrive
    pipedrive.persons.update(pipedrive_person_id, {
        'custom_haive_score': result['qualification']['score'],
        'custom_haive_status': result['qualification']['status'],
        'custom_haive_confidence': result['qualification']['confidence'],
        'custom_haive_action': result['recommended_next_action']
    })
    
    return result
```

### cURL (test rapide)

```bash
#!/bin/bash

# Qualifier un lead depuis le CLI
curl -s -X POST http://localhost:5000/qualify \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Lead",
    "company": "Test Company",
    "role": "Manager",
    "message": "Nous avons besoin de qualifier nos leads",
    "source": "cli"
  }' | jq .

# Résultat:
# {
#   "qualification": {
#     "status": "...",
#     "score": ...,
#     "confidence": "..."
#   },
#   ...
# }
```

---

## Déploiement en Production

### Option A: Sur un serveur (recommandé)

```bash
# Sur serveur Linux (ex: Ubuntu 22.04)
cd /opt/haive-agent
python3 -m venv venv
source venv/bin/activate
pip install flask
nohup python3 api.py > api.log 2>&1 &
```

Puis:
- Configurer un reverse proxy (nginx/Apache)
- Ajouter SSL (Let's Encrypt)
- Ouvrir le port 5000

### Option B: Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY agent.py api.py ./
RUN pip install flask
EXPOSE 5000
CMD ["python3", "api.py"]
```

```bash
docker build -t haive-qualifier .
docker run -p 5000:5000 haive-qualifier
```

### Option C: AWS Lambda / Cloud Functions

Adapter `api.py` en fonction serverless:
- AWS Lambda + API Gateway
- Google Cloud Functions
- Azure Functions

---

## Monitoring et Logs

### Vérifier les appels API

```bash
# Voir les logs de l'API
tail -f api.log

# Compter les qualifications par statut
grep "qualified_high" api.log | wc -l
```

### Metrics à tracker

- Nombre de qualifications/jour
- Distribution des statuts (high/medium/low)
- Taux de "need_more_info"
- Taux de spam détecté
- Temps moyen de qualification

---

## Troubleshooting

| Problème | Solution |
|----------|----------|
| "Connection refused" | Vérifier que l'API est lancée (`python3 api.py`) |
| "Invalid JSON" | Vérifier le format du body request |
| "Field not found" | Vérifier que les custom fields existent dans Pipedrive |
| "Webhook not called" | Vérifier que l'URL est accessible de l'extérieur |
| API lente | Ajouter du caching ou optimiser le scoring |

---

## Support & Feedback

Si l'API échoue:
1. Vérifiez les logs: `tail -f api.log`
2. Testez manuellement: `curl http://localhost:5000/health`
3. Vérifiez le JSON input

Si le scoring est incorrect:
1. Consultez `SCORING_CLARIFICATIONS.md`
2. Vérifiez le message du lead (peu de signaux?)
3. Ajustez le scoring dans `agent.py` si nécessaire

---

## Prochaines Étapes

1. ✅ Démarrer l'API localement
2. ✅ Tester les endpoints avec curl
3. ✅ Créer les custom fields dans Pipedrive
4. ✅ Configurer webhooks ou Zapier
5. ✅ Monitorer les résultats
6. ✅ Ajuster si nécessaire après 20-50 leads
