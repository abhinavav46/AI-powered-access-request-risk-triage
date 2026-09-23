from django import forms
from .models import AccessRequest


class AccessRequestForm(forms.ModelForm):
    class Meta:
        model = AccessRequest
        fields = ["requester_name", "department", "request_text"]
        widgets = {
            "requester_name": forms.TextInput(attrs={
                "placeholder": "e.g. Abhinav A V", "class": "form-input",
            }),
            "department": forms.TextInput(attrs={
                "placeholder": "e.g. IAM / Engineering / Finance", "class": "form-input",
            }),
            "request_text": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Describe exactly what system/data you need access to, and why.",
                "class": "form-input",
            }),
        }
