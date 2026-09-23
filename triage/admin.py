from django.contrib import admin
from .models import AccessRequest


@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = (
        "requester_name", "department", "risk_level",
        "risk_confidence", "status", "submitted_at",
    )
    list_filter = ("risk_level", "status", "department")
    search_fields = ("requester_name", "request_text")
    readonly_fields = (
        "risk_level", "risk_confidence", "risk_source",
        "matched_keyword", "recommended_approver", "submitted_at",
    )
