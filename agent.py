#!/usr/bin/env python3
"""
Lead Qualification Agent - HAIVE
Evaluates B2B leads against HAIVE's ICP and scoring framework.

Usage:
    python agent.py < input.json
    echo '{"name": "..."}' | python agent.py
"""

import json
import sys
from typing import Dict, List, Optional

# ICP reference
ICP_SECTORS = {
    "retail": 5, "franchise": 5, "hotel": 4, "bank": 5, "logistics": 4,
    "manufacturing": 4, "distribution": 5, "services": 3, "startup": 0,
    "consulting": 2, "education": 0, "freelance": 0
}

DECISION_ROLES = {
    "coo": 5, "cto": 3, "ceo": 4, "directeur opérations": 5, "directeur transformation": 5,
    "directeur réseau": 5, "directrice réseau": 5, "directeur général": 4, "vp operations": 5, "vp": 4,
    "directeur formation": 3, "directrice formation": 3, "responsable régional": 3, "responsable formation": 2, "responsable": 2,
    "consultant": 0, "étudiant": 0, "indépendant": 0, "marketing": 0
}


class LeadQualifier:
    """HAIVE Lead Qualification Agent"""

    def __init__(self):
        self.lead = {}
        self.criteria = {}
        self.missing = []
        self.score = 0
        self.status = ""
        self.confidence = ""

    def qualify(self, lead_data: Dict) -> Dict:
        """Main qualification function"""
        self.lead = lead_data
        self.missing = []
        self.criteria = {}

        # Validate required fields
        if not self._validate_input():
            return self._output_need_more_info()

        # Score each dimension
        self._score_icp_fit()
        self._score_company_size()
        self._score_role_relevance()
        self._score_need_clarity()
        self._score_timing()
        self._score_maturity()
        self._score_budget()

        # Calculate total and determine status
        self._calculate_score()
        self._determine_status()
        self._calculate_confidence()

        return self._build_output()

    def _validate_input(self) -> bool:
        """Check for critical missing fields"""
        required = ["name", "company", "role", "message"]

        company = str(self.lead.get("company", "")).lower()

        # Check for "Inconnu" or missing company
        if company in ["inconnu", "unknown", ""] or not self.lead.get("company"):
            self.missing.append("company_identification")
            return False

        return True

    def _score_icp_fit(self):
        """Dimension 1: ICP Fit (0-5)"""
        company = str(self.lead.get("company", "")).lower()
        message = str(self.lead.get("message", "")).lower()

        # Check for multi-site signals
        multi_site_keywords = ["magasin", "site", "agence", "franchis", "filial", "établiss", "réseau"]
        has_multi_site = any(kw in message for kw in multi_site_keywords)

        # Check sector
        sector_score = 0
        for sector, score in ICP_SECTORS.items():
            if sector in company or sector in message:
                sector_score = score
                break

        if has_multi_site and sector_score >= 4:
            score = 5
        elif has_multi_site or sector_score == 5:
            score = 4
        elif sector_score >= 3:
            score = 3
        elif sector_score > 0:
            score = 2
        else:
            score = 1 if "entreprise" in message else 0
            if "seul" in message or "indépend" in message or "freelance" in message:
                score = 0

        self.criteria["icp_fit"] = score

    def _score_company_size(self):
        """Dimension 2: Company Size & Structure (0-3)"""
        company = str(self.lead.get("company", "")).lower()
        message = str(self.lead.get("message", "")).lower()

        # Anti-ICP: Solo/freelance = 0
        if any(kw in (company + message) for kw in ["freelance", "indépendant", "seul", "solo"]):
            score = 0
        # Look for size indicators
        elif any(kw in message for kw in ["120 magasins", "plusieurs établiss", "multi-site", "réseau", "agences", "franchisés"]):
            score = 3
        elif any(kw in message for kw in ["équipes terrain", "plusieurs équipes", "structure", "régional", "manager"]):
            score = 3  # Regional/multi-team structure
        elif "équipe de 10" in message:
            score = 1
        else:
            score = 2  # Default: assume intermediate

        self.criteria["company_size"] = score

    def _score_role_relevance(self):
        """Dimension 3: Role Relevance (0-5)"""
        role = str(self.lead.get("role", "")).lower()

        # Check role against decision makers
        score = 0
        for role_key, role_score in DECISION_ROLES.items():
            if role_key in role:
                score = role_score
                break

        # If no match, default scoring
        if score == 0:
            if any(x in role for x in ["directeur", "director", "coo", "cto", "vp"]):
                score = 4
            elif any(x in role for x in ["responsable", "manager", "coordinat"]):
                score = 2
            else:
                score = 0

        self.criteria["role_relevance"] = score

    def _score_need_clarity(self):
        """Dimension 4: Problem/Need Clarity (0-5)"""
        company = str(self.lead.get("company", "")).lower()
        message = str(self.lead.get("message", "")).lower()

        # Anti-ICP: Solo/freelance has NO management execution need
        if any(kw in (company + message) for kw in ["freelance", "indépendant", "seul", "solo"]):
            score = 0
        # Level 5: Explicit problem clearly stated
        elif any(kw in message for kw in ["difficultés à appliquer", "difficultés d'adoption", "mal à aligner", "difficulté"]):
            score = 5
        # Level 4: Very clear but less explicit
        elif any(kw in message for kw in ["aligner", "standardiser", "transformation", "pratiques varient"]):
            score = 4
        # Level 3: Implicit need identifiable from context
        elif any(kw in message for kw in ["améliorer la communication", "structurer management", "équipes terrain", "management"]):
            score = 3
        # Level 2: Vague need
        elif any(kw in message for kw in ["outils", "organiser", "gérer", "mieux"]):
            score = 2
        # Level 1: Minimal signal
        elif any(kw in message for kw in ["intéressé", "plus", "solution"]):
            score = 1
        # Level 0: No signal
        else:
            score = 0

        # If message is promotional spam
        if any(kw in message for kw in ["boost", "click here", "seo", "!!!", "amazing services"]):
            self.criteria["is_spam"] = True
            score = 0

        self.criteria["need_clarity"] = score

    def _score_timing(self):
        """Dimension 5: Timing/Urgency (0-3)"""
        company = str(self.lead.get("company", "")).lower()
        message = str(self.lead.get("message", "")).lower()

        # Anti-ICP: Solo/freelance timing = 0
        if any(kw in (company + message) for kw in ["freelance", "indépendant", "seul", "solo"]):
            score = 0
        elif any(kw in message for kw in ["en cours", "déployons", "pleine transformation", "immédiat", "difficultés", "rencontrons"]):
            score = 3
        elif any(kw in message for kw in ["envisage", "cherche", "besoin", "souhait", "aligner"]):
            score = 2
        elif any(kw in message for kw in ["explore", "intéressé", "plus d'info"]):
            score = 1
        else:
            score = 0

        self.criteria["timing"] = score

    def _score_maturity(self):
        """Dimension 6: Digital/Organizational Maturity (0-2)"""
        company = str(self.lead.get("company", "")).lower()
        message = str(self.lead.get("message", "")).lower()

        # Anti-ICP: Solo/freelance maturity = 0
        if any(kw in (company + message) for kw in ["freelance", "indépendant", "seul", "solo"]):
            score = 0
        elif any(kw in (company + message) for kw in ["groupe", "banque", "réseau", "franchise", "structure"]):
            score = 1
        else:
            score = 0

        self.criteria["maturity"] = score

    def _score_budget(self):
        """Dimension 7: Budget Potential (0-2)"""
        company = str(self.lead.get("company", "")).lower()

        if any(kw in company for kw in ["group", "banque", "retail", "franchise", "network"]):
            score = 1
        else:
            score = 0

        self.criteria["budget"] = score

    def _calculate_score(self):
        """Sum all criteria"""
        self.score = sum([
            self.criteria.get("icp_fit", 0),
            self.criteria.get("company_size", 0),
            self.criteria.get("role_relevance", 0),
            self.criteria.get("need_clarity", 0),
            self.criteria.get("timing", 0),
            self.criteria.get("maturity", 0),
            self.criteria.get("budget", 0),
        ])

    def _determine_status(self):
        """Map score to status"""
        if self.criteria.get("is_spam"):
            self.status = "spam"
        elif len(self.missing) >= 3 or (self.score <= 5 and len(self.missing) > 0):
            self.status = "need_more_info"
        elif self.score >= 18:
            self.status = "qualified_high"
        elif self.score >= 12:
            self.status = "qualified_medium"
        elif self.score >= 6:
            self.status = "low_priority"
        else:
            self.status = "not_qualified"

    def _calculate_confidence(self):
        """Calculate confidence based on score and missing info"""
        missing_count = len(self.missing)

        if self.score >= 18 and missing_count < 2 and self.status != "need_more_info":
            self.confidence = "HIGH"
        elif (12 <= self.score < 18) or (self.score >= 18 and missing_count >= 2):
            self.confidence = "MEDIUM"
        else:
            self.confidence = "LOW"

    def _output_need_more_info(self) -> Dict:
        """Output for need_more_info status"""
        return {
            "lead_summary": {
                "name": self.lead.get("name", "Unknown"),
                "company": self.lead.get("company", "Unknown"),
                "role": self.lead.get("role", "Unknown"),
            },
            "qualification": {
                "status": "need_more_info",
                "score": None,
                "confidence": "LOW",
            },
            "criteria": {},
            "missing_information": ["company_identification", "role_clarity", "problem_clarity", "company_size"],
            "reasoning_summary": "Informations critiques manquantes. Impossible de qualifier sans clarifications.",
            "recommended_next_action": "request_more_info",
            "crm_note": "Lead nécessite enrichissement avant qualification complète.",
        }

    def _build_output(self) -> Dict:
        """Build JSON output according to schema"""
        # Determine recommended action
        if self.status == "spam":
            action = "discard"
        elif self.status == "qualified_high":
            action = "assign_to_sales"
        elif self.status == "qualified_medium":
            action = "request_more_info"
        elif self.status == "low_priority":
            action = "nurture"
        elif self.status == "need_more_info":
            action = "request_more_info"
        else:
            action = "discard"

        # Build reasoning
        reasoning = self._build_reasoning()

        return {
            "lead_summary": {
                "name": self.lead.get("name", ""),
                "company": self.lead.get("company", ""),
                "role": self.lead.get("role", ""),
                "source": self.lead.get("source", ""),
            },
            "qualification": {
                "status": self.status,
                "score": self.score,
                "confidence": self.confidence,
            },
            "criteria": {
                "icp_fit": self.criteria.get("icp_fit", 0),
                "company_size": self.criteria.get("company_size", 0),
                "role_relevance": self.criteria.get("role_relevance", 0),
                "need_clarity": self.criteria.get("need_clarity", 0),
                "timing": self.criteria.get("timing", 0),
                "maturity": self.criteria.get("maturity", 0),
                "budget": self.criteria.get("budget", 0),
            },
            "missing_information": self.missing,
            "reasoning_summary": reasoning,
            "recommended_next_action": action,
            "crm_note": self._build_crm_note(),
        }

    def _build_reasoning(self) -> str:
        """Build 2-3 sentence reasoning"""
        if self.status == "spam":
            return "Contenu non professionnel, promotionnel ou incohérent."

        parts = []

        # ICP assessment
        if self.criteria.get("icp_fit", 0) >= 4:
            parts.append("ICP excellent")
        elif self.criteria.get("icp_fit", 0) >= 3:
            parts.append("ICP pertinent")
        else:
            parts.append("ICP faible")

        # Role assessment
        role_score = self.criteria.get("role_relevance", 0)
        if role_score >= 4:
            parts.append("contact décisionnaire")
        elif role_score >= 2:
            parts.append("contact pertinent")
        else:
            parts.append("contact peu pertinent")

        # Need assessment
        need_score = self.criteria.get("need_clarity", 0)
        if need_score >= 4:
            parts.append("besoin explicite")
        elif need_score == 3:
            parts.append("besoin implicite")
        else:
            parts.append("besoin faible")

        return ". ".join(parts) + "."

    def _build_crm_note(self) -> str:
        """Build actionable CRM note"""
        if self.status == "qualified_high":
            return f"Lead qualifié. Contact: {self.lead.get('role')} chez {self.lead.get('company')}. À traiter en priorité."
        elif self.status == "qualified_medium":
            return f"Lead à qualifier. Besoin: {self.criteria.get('need_clarity', 0)}/5. Questions complémentaires recommandées."
        elif self.status == "need_more_info":
            return f"Informations insuffisantes. Enrichir: {', '.join(self.missing[:2])}."
        else:
            return f"Lead faible ou hors cible. Score: {self.score}/25."


def main():
    """Read JSON from stdin, qualify, output JSON"""
    try:
        # Read input
        input_data = json.load(sys.stdin)

        # Qualify
        qualifier = LeadQualifier()
        result = qualifier.qualify(input_data)

        # Output
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except json.JSONDecodeError as e:
        print(json.dumps({
            "error": "Invalid JSON input",
            "details": str(e)
        }), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": "Unexpected error",
            "details": str(e)
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
