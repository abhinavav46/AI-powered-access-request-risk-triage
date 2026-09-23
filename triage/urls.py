from django.urls import path
from . import views

app_name = "triage"

urlpatterns = [
    path("", views.submit_request, name="submit_request"),
    path("request/<int:pk>/", views.request_detail, name="request_detail"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("request/<int:pk>/status/", views.update_status, name="update_status"),
    path("api/classify-preview/", views.classify_preview_api, name="classify_preview_api"),
]
