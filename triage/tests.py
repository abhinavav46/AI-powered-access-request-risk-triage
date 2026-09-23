"""
Automated tests for the Access Risk Triage app.

Run with:
    python manage.py test

These cover three layers, which is good practice to point out in an
interview/demo:
1. Unit tests on the ML classifier logic (pure Python, no Django needed).
2. Model tests (Django ORM).
3. View / integration tests (Django test client, simulating real HTTP
   requests the way Selenium would simulate a real browser).
"""

from django.test import TestCase, Client
from django.urls import reverse
from .models import AccessRequest
from .ml.predictor import classify_request, _approver_for


class RiskClassifierTests(TestCase):
    def test_high_risk_keyword_triggers_rule_override(self):
        result = classify_request("I need root access to the production database")
        self.assertEqual(result["risk_level"], "high")
        self.assertEqual(result["source"], "rule_override")

    def test_low_risk_request_is_not_flagged_high(self):
        result = classify_request("Please give me read access to the company newsletter")
        self.assertIn(result["risk_level"], ["low", "medium"])

    def test_approver_mapping(self):
        self.assertEqual(_approver_for("low"), "Auto-approved (manager notified)")
        self.assertEqual(_approver_for("high"), "Requires IAM security team + manager approval")


class AccessRequestModelTests(TestCase):
    def test_string_representation(self):
        req = AccessRequest.objects.create(
            requester_name="Abhinav",
            department="IAM",
            request_text="Need admin access to SailPoint console",
            risk_level="high",
        )
        self.assertIn("Abhinav", str(req))


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_submit_request_page_loads(self):
        response = self.client.get(reverse("triage:submit_request"))
        self.assertEqual(response.status_code, 200)

    def test_submitting_valid_form_creates_record_and_redirects(self):
        response = self.client.post(reverse("triage:submit_request"), {
            "requester_name": "Abhinav",
            "department": "Engineering",
            "request_text": "Need root access to the AWS production account",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AccessRequest.objects.count(), 1)
        self.assertEqual(AccessRequest.objects.first().risk_level, "high")

    def test_dashboard_page_loads(self):
        response = self.client.get(reverse("triage:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_classify_preview_api(self):
        response = self.client.get(reverse("triage:classify_preview_api"), {
            "text": "Need admin access to the production database server",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["risk_level"], "high")

    def test_update_status_flow(self):
        req = AccessRequest.objects.create(
            requester_name="Test User",
            department="QA",
            request_text="Need read access to the QA test plan doc",
            risk_level="low",
        )
        response = self.client.post(
            reverse("triage:update_status", args=[req.pk]), {"status": "approved"}
        )
        req.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(req.status, "approved")
