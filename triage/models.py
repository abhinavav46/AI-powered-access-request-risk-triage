from django.db import models


class AccessRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    RISK_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    requester_name = models.CharField(max_length=120)
    department = models.CharField(max_length=120)
    request_text = models.TextField(
        help_text="Describe the system/data you need access to and why."
    )

    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, blank=True)
    risk_confidence = models.FloatField(null=True, blank=True)
    risk_source = models.CharField(max_length=20, blank=True)  # 'ml_model' or 'rule_override'
    matched_keyword = models.CharField(max_length=100, blank=True, null=True)
    recommended_approver = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.requester_name} - {self.request_text[:40]} ({self.risk_level})"
