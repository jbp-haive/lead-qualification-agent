#!/usr/bin/env python3
"""
HAIVE Lead Qualification Agent - REST API
Expose the agent via HTTP API for Pipedrive integration

Usage:
    python3 api.py
    Then POST to http://localhost:5000/qualify
"""

from flask import Flask, request, jsonify
from agent import LeadQualifier
import json
import sys

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "HAIVE Lead Qualifier"})

@app.route('/qualify', methods=['POST'])
def qualify():
    """
    Qualify a lead

    Expected input:
    {
        "name": "string",
        "email": "string",
        "company": "string",
        "role": "string",
        "message": "string",
        "source": "string"
    }

    Returns:
    {
        "lead_summary": {...},
        "qualification": {...},
        "criteria": {...},
        ...
    }
    """
    try:
        # Get JSON from request
        data = request.get_json()

        if not data:
            return jsonify({"error": "Empty request body"}), 400

        # Required fields for Pipedrive
        required = ["name", "company", "role", "message"]
        missing = [f for f in required if not data.get(f)]

        if missing:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing)}",
                "required_fields": required
            }), 400

        # Qualify
        qualifier = LeadQualifier()
        result = qualifier.qualify(data)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "Qualification failed",
            "details": str(e)
        }), 500

@app.route('/batch', methods=['POST'])
def batch_qualify():
    """
    Qualify multiple leads

    Expected input:
    {
        "leads": [
            {"name": "...", "company": "...", ...},
            {...}
        ]
    }
    """
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

        return jsonify({
            "count": len(results),
            "results": results
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Batch qualification failed",
            "details": str(e)
        }), 500

@app.route('/pipedrive/webhook', methods=['POST'])
def pipedrive_webhook():
    """
    Webhook receiver for Pipedrive person.created events

    This endpoint is called by Pipedrive when a new person/deal is added.
    It qualifies the lead and can optionally update the deal.
    """
    try:
        data = request.get_json()

        # Pipedrive webhook format
        # data = {
        #     "action": "added",
        #     "object": "person",
        #     "data": {
        #         "id": 123,
        #         "name": "John Doe",
        #         "email": [{"value": "john@example.com"}],
        #         "org_id": {"value": 456, "name": "Company Inc"},
        #         ...
        #     }
        # }

        if not data:
            return jsonify({"error": "Empty webhook payload"}), 400

        # Extract lead info from Pipedrive format
        pd_data = data.get("data", {})

        lead_input = {
            "name": pd_data.get("name", "Unknown"),
            "company": pd_data.get("org_id", {}).get("name", "Unknown"),
            "role": pd_data.get("job_title", "Unknown"),
            "message": pd_data.get("notes", ""),
            "email": pd_data.get("email", [{}])[0].get("value", ""),
            "source": "pipedrive"
        }

        # Qualify
        qualifier = LeadQualifier()
        result = qualifier.qualify(lead_input)

        # Return qualification for Pipedrive to process
        return jsonify({
            "success": True,
            "pipedrive_id": pd_data.get("id"),
            "qualification": result.get("qualification"),
            "recommended_action": result.get("recommended_next_action"),
            "full_result": result
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Webhook processing failed",
            "details": str(e)
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET /health",
            "POST /qualify",
            "POST /batch",
            "POST /pipedrive/webhook"
        ]
    }), 404

def main():
    """Start API server"""
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

    app.run(host="0.0.0.0", port=5001, debug=False)

if __name__ == "__main__":
    main()
