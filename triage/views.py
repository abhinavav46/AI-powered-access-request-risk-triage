from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import AccessRequest
from .forms import AccessRequestForm
from .ml.predictor import classify_request


def submit_request(request):
    """Home page: shows the submission form and runs the AI risk classifier
    on POST, before saving the record."""
    if request.method == "POST":
        form = AccessRequestForm(request.POST)
        if form.is_valid():
            access_request = form.save(commit=False)

            try:
                result = classify_request(access_request.request_text)
                access_request.risk_level = result["risk_level"]
                access_request.risk_confidence = result["confidence"]
                access_request.risk_source = result["source"]
                access_request.matched_keyword = result["matched_keyword"]
                access_request.recommended_approver = result["recommended_approver"]
            except FileNotFoundError:
                messages.error(
                    request,
                    "The AI model isn't trained yet. Run: python manage.py train_model",
                )
                return render(request, "triage/index.html", {"form": form})

            access_request.save()
            return redirect("triage:request_detail", pk=access_request.pk)
    else:
        form = AccessRequestForm()

    return render(request, "triage/index.html", {"form": form})


def request_detail(request, pk):
    access_request = get_object_or_404(AccessRequest, pk=pk)
    return render(request, "triage/request_detail.html", {"req": access_request})


def dashboard(request):
    """Lists all submitted requests, with optional filtering by risk level
    and status via query params, e.g. /dashboard/?risk=high&status=pending"""
    requests_qs = AccessRequest.objects.all()

    risk_filter = request.GET.get("risk")
    status_filter = request.GET.get("status")

    if risk_filter in ("low", "medium", "high"):
        requests_qs = requests_qs.filter(risk_level=risk_filter)
    if status_filter in ("pending", "approved", "rejected"):
        requests_qs = requests_qs.filter(status=status_filter)

    counts = {
        "total": AccessRequest.objects.count(),
        "high": AccessRequest.objects.filter(risk_level="high").count(),
        "medium": AccessRequest.objects.filter(risk_level="medium").count(),
        "low": AccessRequest.objects.filter(risk_level="low").count(),
        "pending": AccessRequest.objects.filter(status="pending").count(),
    }

    return render(request, "triage/dashboard.html", {
        "requests": requests_qs,
        "counts": counts,
        "risk_filter": risk_filter or "",
        "status_filter": status_filter or "",
    })


@require_POST
def update_status(request, pk):
    """Lets a reviewer approve/reject a request from the dashboard."""
    access_request = get_object_or_404(AccessRequest, pk=pk)
    new_status = request.POST.get("status")
    if new_status in ("approved", "rejected", "pending"):
        access_request.status = new_status
        access_request.save(update_fields=["status"])
        messages.success(request, f"Request #{pk} marked as {new_status}.")
    return redirect("triage:dashboard")


def classify_preview_api(request):
    """Small JSON API used by the front-end JS to show a live AI risk
    preview as the user types, before they submit the form."""
    text = request.GET.get("text", "").strip()
    if not text:
        return JsonResponse({"error": "empty text"}, status=400)
    try:
        result = classify_request(text)
    except FileNotFoundError:
        return JsonResponse({"error": "model not trained"}, status=503)
    return JsonResponse(result)
