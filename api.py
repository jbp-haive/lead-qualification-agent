#!/usr/bin/env python3
"""
HAIVE Lead Qualification Agent - REST API
"""

import os
import json
import sys
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
        update_payload = {
            PIPEDRIVE_FIELD_KEYS['score']: score,
            PIPEDRIVE_FIELD_KEYS['status']: status,
            PIPEDRIVE_FIELD_KEYS['confidence']: confidence,
            PIPEDRIVE_FIELD_KEYS['action']: action,
            PIPEDRIVE_FIELD_KEYS['reasoning']: reasoning
        }

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

        lead_input = {
            "name": pd_data.get("name", "Unknown"),
            "company": company,
            "role": pd_data.get("job_title", "Unknown"),
            "message": pd_data.get("notes", ""),
            "email": email,
            "source": "pipedrive"
        }

        qualifier = LeadQualifier()
        result = qualifier.qualify(lead_input)

        # Mettre à jour les champs Pipedrive avec les résultats de qualification
        person_id = pd_data.get("id")
        if person_id:
            update_pipedrive_person(person_id, result)

        return jsonify({
            "success": True,
            "pipedrive_id": person_id,
            "qualification": result.get("qualification"),
            "recommended_action": result.get("recommended_next_action"),
            "full_result": result
        }), 200
    except Exception as e:
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
