#!/usr/bin/env python3
"""
HAIVE Lead Qualification Agent - REST API
"""

import os
import json
import sys
import time
import requests
from flask import Flask, request, jsonify
from agent import LeadQualifier

app = Flask(__name__)

# Configuration Pipedrive (depuis variables d'environnement)
PIPEDRIVE_API_TOKEN = os.environ.get('PIPEDRIVE_API_TOKEN', '')
PIPEDRIVE_API_URL = "https://api.pipedrive.com/v1"

# Clés des champs personnalisés dans Pipedrive
# À remplir avec les clés réelles de vos champs (ex: custom_field_123a45b)
PIPEDRIVE_FIELD_KEYS = {
    'score': os.environ.get('PIPEDRIVE_FIELD_SCORE', ''),
    'status': os.environ.get('PIPEDRIVE_FIELD_STATUS', ''),
    'confidence': os.environ.get('PIPEDRIVE_FIELD_CONFIDENCE', ''),
    'action': os.environ.get('PIPEDRIVE_FIELD_ACTION', ''),
    'reasoning': os.environ.get('PIPEDRIVE_FIELD_REASONING', '')
}

def update_pipedrive_person(person_id: int, qualification_result: dict) -> bool:
    """
    Met à jour les champs personnalisés Pipedrive avec les résultats de qualification.

    Args:
        person_id: ID de la personne dans Pipedrive
        qualification_result: Résultat de qualification de l'agent

    Returns:
        True si mise à jour réussie, False sinon
    """
    if not PIPEDRIVE_API_TOKEN:
        print("⚠️  PIPEDRIVE_API_TOKEN non configuré - champs non mis à jour")
        return False

    if not all(PIPEDRIVE_FIELD_KEYS.values()):
        print("⚠️  Clés de champs Pipedrive incomplètes - champs non mis à jour")
        return False

    try:
        # Extraire les données de qualification
        qualification = qualification_result.get("qualification", {})
        score = qualification.get("score", 0)
        status = qualification.get("status", "")
        confidence = qualification.get("confidence", "")
        action = qualification_result.get("recommended_next_action", "")
        reasoning = qualification_result.get("reasoning_summary", "")

        # Préparer la charge utile pour la mise à jour
        # Exclure les valeurs None/vides pour éviter les erreurs Pipedrive
        update_payload = {}
        if score is not None:  # Important: 0 est une valeur valide!
            update_payload[PIPEDRIVE_FIELD_KEYS['score']] = score
        if status:
            update_payload[PIPEDRIVE_FIELD_KEYS['status']] = status
        if confidence:
            update_payload[PIPEDRIVE_FIELD_KEYS['confidence']] = confidence
        if action:
            update_payload[PIPEDRIVE_FIELD_KEYS['action']] = action
        if reasoning:
            update_payload[PIPEDRIVE_FIELD_KEYS['reasoning']] = reasoning

        # Debug: afficher les valeurs envoyées
        print(f"DEBUG - Payload envoyé à Pipedrive pour personne {person_id}:")
        print(f"  score={score}, status={status}, confidence={confidence}, action={action}")
        print(f"  Champs réellement envoyés: {list(update_payload.keys())}")

        # Appel API Pipedrive
        url = f"{PIPEDRIVE_API_URL}/persons/{person_id}"
        headers = {"Content-Type": "application/json"}
        params = {"api_token": PIPEDRIVE_API_TOKEN}

        response = requests.put(url, json=update_payload, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            print(f"✅ Champs Pipedrive mis à jour pour la personne {person_id}")
            return True
        else:
            print(f"❌ Erreur Pipedrive (code {response.status_code}): {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la mise à jour Pipedrive: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        return False

def enrich_person_data(person_id: int, partial_data: dict) -> dict:
    """
    Enrichit les données partielles du webhook en récupérant l'intégralité des données de la personne.
    Inclut un mécanisme de retry si les champs critiques sont null.

    Args:
        person_id: ID de la personne dans Pipedrive
        partial_data: Données partielles reçues du webhook

    Returns:
        Dictionnaire fusionné avec les données complètes
    """
    if not PIPEDRIVE_API_TOKEN:
        print("⚠️  PIPEDRIVE_API_TOKEN non configuré - impossible d'enrichir les données")
        return partial_data

    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            if attempt == 0:
                print(f"\n🔄 Enrichissement des données pour person_id={person_id}")
            else:
                print(f"🔄 Tentative d'enrichissement #{attempt + 1}/{max_retries}")

            url = f"{PIPEDRIVE_API_URL}/persons/{person_id}"
            params = {"api_token": PIPEDRIVE_API_TOKEN}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                full_data = response.json().get("data", {})
                print(f"✅ Données récupérées de Pipedrive (tentative {attempt + 1})")

                # Fusionner: utiliser les données complètes, garder les données du webhook comme fallback
                enriched = {**partial_data, **full_data}

                # Vérifier les champs critiques
                job_title = enriched.get('job_title')
                notes = enriched.get('notes')

                print(f"  job_title: {job_title if job_title else 'N/A'}")
                print(f"  notes: {notes[:50] if notes else 'N/A'}...")

                # Si champs critiques présents, retourner
                if job_title and notes:
                    print(f"✅ Données complètes obtenues")
                    return enriched

                # Si champs manquants et ce n'est pas la dernière tentative, attendre et retry
                if attempt < max_retries - 1:
                    print(f"⚠️  Champs critiques manquants, attente {retry_delay}s avant retry...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"⚠️  Champs critiques toujours manquants après {max_retries} tentatives")
                    return enriched
            else:
                print(f"⚠️  Erreur API Pipedrive ({response.status_code})")
                if attempt < max_retries - 1:
                    print(f"   Attente {retry_delay}s avant retry...")
                    time.sleep(retry_delay)
                else:
                    return partial_data

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Erreur réseau: {str(e)}")
            if attempt < max_retries - 1:
                print(f"   Attente {retry_delay}s avant retry...")
                time.sleep(retry_delay)
            else:
                return partial_data
        except Exception as e:
            print(f"⚠️  Erreur lors de l'enrichissement: {str(e)}")
            return partial_data

    return partial_data

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "HAIVE Lead Qualifier"})

@app.route('/qualify', methods=['POST'])
def qualify():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty request body"}), 400
        required = ["name", "company", "role", "message"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}", "required_fields": required}), 400
        qualifier = LeadQualifier()
        result = qualifier.qualify(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Qualification failed", "details": str(e)}), 500

@app.route('/batch', methods=['POST'])
def batch_qualify():
    try:
        data = request.get_json()
        leads = data.get("leads", [])
        if not leads:
            return jsonify({"error": "No leads provided"}), 400
        results = []
        for lead in leads:
            qualifier = LeadQualifier()
            result = qualifier.qualify(lead)
            results.append(result)
        return jsonify({"count": len(results), "results": results}), 200
    except Exception as e:
        return jsonify({"error": "Batch qualification failed", "details": str(e)}), 500

@app.route('/pipedrive/webhook', methods=['POST'])
def pipedrive_webhook():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty webhook payload"}), 400
        pd_data = data.get("data", {})

        # 🔴 LOGGING: Webhook reçu
        print("\n" + "="*80)
        print("🔴 WEBHOOK REÇU")
        print("="*80)
        print(f"Payload complet: {json.dumps(pd_data, indent=2, ensure_ascii=False)}")
        print("="*80)

        # 🔄 ENRICHISSEMENT: Récupérer les données complètes de Pipedrive
        person_id = pd_data.get("id")
        if person_id:
            # 🕐 DÉLAI: Attendre que Pipedrive synchronise les données AVANT enrichissement
            print(f"\n⏳ Attente 3 secondes pour synchronisation Pipedrive...")
            time.sleep(3)

            pd_data = enrich_person_data(person_id, pd_data)
            print(f"\n✅ Données enrichies et fusionnées")
        else:
            print(f"\n⚠️  Pas d'ID de personne dans le webhook")

        # Safely extract org_id (handle null/dict case)
        org_id_obj = pd_data.get("org_id")
        company = "Unknown"
        if org_id_obj:
            if isinstance(org_id_obj, dict):
                company = org_id_obj.get("name", "Unknown")
            elif isinstance(org_id_obj, str):
                company = org_id_obj

        # Safely extract email (handle null/empty list case)
        email = ""
        email_list = pd_data.get("email")
        if email_list and isinstance(email_list, list) and len(email_list) > 0:
            email_obj = email_list[0]
            if isinstance(email_obj, dict):
                email = email_obj.get("value", "")
            elif isinstance(email_obj, str):
                email = email_obj

        # Extract job_title and notes: first try standard fields, then custom_fields
        job_title = pd_data.get("job_title") or ""
        notes = pd_data.get("notes") or ""

        # If standard fields are empty, search in custom_fields
        if not job_title or not notes:
            custom_fields = pd_data.get("custom_fields", {})
            if custom_fields:
                print(f"\n🔍 Recherche dans custom_fields pour job_title et notes")
                for field_id, field_data in custom_fields.items():
                    if isinstance(field_data, dict):
                        field_value = field_data.get("value", "")
                        field_type = field_data.get("type", "")

                        # Identify job_title: typically short varchar with professional titles
                        if not job_title and field_type == "varchar" and 5 < len(field_value) < 100:
                            if any(keyword in field_value.lower() for keyword in ["director", "manager", "chief", "vp", "vice", "president", "head", "lead", "officer"]):
                                print(f"  ✅ job_title trouvé dans custom field {field_id}: {field_value}")
                                job_title = field_value

                        # Identify notes: typically longer text
                        if not notes and field_type == "varchar" and len(field_value) > 100:
                            print(f"  ✅ notes trouvés dans custom field {field_id}: {field_value[:50]}...")
                            notes = field_value

        lead_input = {
            "name": pd_data.get("name", "Unknown"),
            "company": company,
            "role": job_title if job_title else "Unknown",
            "message": notes,
            "email": email,
            "source": "pipedrive"
        }

        # 🔴 LOGGING: Données envoyées à l'agent
        print(f"\n📤 Données envoyées à l'agent:")
        print(json.dumps(lead_input, indent=2, ensure_ascii=False))

        qualifier = LeadQualifier()
        result = qualifier.qualify(lead_input)

        # 🔴 LOGGING: Résultat de qualification
        print(f"\n🎯 Résultat qualification:")
        print(f"  score={result['qualification']['score']}")
        print(f"  status={result['qualification']['status']}")
        print(f"  action={result['recommended_next_action']}")

        # Mettre à jour les champs Pipedrive avec les résultats de qualification
        if person_id:
            # 🔴 LOGGING: Avant appel Pipedrive
            print(f"\n📞 Appel Pipedrive API pour person_id={person_id}")
            update_pipedrive_person(person_id, result)

        print("\n" + "="*80 + "\n")

        return jsonify({
            "success": True,
            "pipedrive_id": person_id,
            "qualification": result.get("qualification"),
            "recommended_action": result.get("recommended_next_action"),
            "full_result": result
        }), 200
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        return jsonify({"error": "Webhook processing failed", "details": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "available_endpoints": ["GET /health", "POST /qualify", "POST /batch", "POST /pipedrive/webhook"]}), 404

def main():
    print("\n" + "="*60)
    print("🚀 HAIVE Lead Qualifier API")
    print("="*60)
    print("\nEndpoints:")
    print("  GET  http://localhost:5001/health")
    print("  POST http://localhost:5001/qualify")
    print("  POST http://localhost:5001/batch")
    print("  POST http://localhost:5001/pipedrive/webhook")
    print("\n✅ Server running on http://localhost:5001")
    print("="*60 + "\n")
    port = int(os.environ.get('PORT', 5001))
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
