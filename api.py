#!/usr/bin/env python3
"""
HAIVE Lead Qualification Agent - REST API
"""

import os
import json
import sys
from flask import Flask, request, jsonify
from agent import LeadQualifier

app = Flask(__name__)

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
        return jsonify({"success": True, "pipedrive_id": pd_data.get("id"), "qualification": result.get("qualification"), "recommended_action": result.get("recommended_next_action"), "full_result": result}), 200
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
