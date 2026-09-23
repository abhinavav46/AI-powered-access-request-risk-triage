"""
predictor.py
------------
Loads the trained TF-IDF + Logistic Regression pipeline once (singleton) and
exposes classify_request(text) for the Django views to call.

Design note: on top of the ML model, we add a small rule-based "safety net".
This is a common real-world IAM pattern: never let a probabilistic model be
the ONLY thing standing between a user and a dangerous access grant. If the
request text contains a small set of critical keywords (root, admin, delete
production data, bypass MFA, etc.), we force the risk to "high" regardless
of what the model predicts, and say so in the explanation. This also makes
the system easier to demo and reason about for someone reviewing your code.
"""

import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "risk_model.joblib")

HIGH_RISK_KEYWORDS = [
    "root access", "root credentials", "admin access", "administrator access",
    "superuser", "domain controller", "bypass mfa", "bypass multi-factor",
    "disable audit", "disable logging", "delete records", "delete production",
    "export the full customer database", "encryption key", "payroll",
    "credit card", "ssn", "salary", "compensation details", "aws root",
    "approve my own access", "security group policies", "commit rights",
]

_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "risk_model.joblib not found. Run: python manage.py train_model"
            )
        _pipeline = joblib.load(MODEL_PATH)
    return _pipeline


def classify_request(text: str):
    """
    Returns a dict:
        risk_level: 'low' | 'medium' | 'high'
        confidence: float (0-1), the model's probability for the chosen class
        source: 'ml_model' or 'rule_override'
        matched_keyword: the keyword that triggered a rule override, if any
        recommended_approver: suggested approval path based on risk_level
    """
    pipeline = _get_pipeline()
    text_lower = text.lower()

    probabilities = pipeline.predict_proba([text])[0]
    classes = pipeline.classes_
    best_index = probabilities.argmax()
    ml_risk = classes[best_index]
    ml_confidence = float(probabilities[best_index])

    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in text_lower:
            return {
                "risk_level": "high",
                "confidence": max(ml_confidence, 0.95),
                "source": "rule_override",
                "matched_keyword": keyword,
                "recommended_approver": _approver_for("high"),
            }

    return {
        "risk_level": ml_risk,
        "confidence": ml_confidence,
        "source": "ml_model",
        "matched_keyword": None,
        "recommended_approver": _approver_for(ml_risk),
    }


def _approver_for(risk_level: str) -> str:
    return {
        "low": "Auto-approved (manager notified)",
        "medium": "Requires manager approval",
        "high": "Requires IAM security team + manager approval",
    }.get(risk_level, "Requires manager approval")
