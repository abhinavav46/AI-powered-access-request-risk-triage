from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AccessRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("requester_name", models.CharField(max_length=120)),
                ("department", models.CharField(max_length=120)),
                ("request_text", models.TextField(help_text="Describe the system/data you need access to and why.")),
                ("risk_level", models.CharField(blank=True, choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], max_length=10)),
                ("risk_confidence", models.FloatField(blank=True, null=True)),
                ("risk_source", models.CharField(blank=True, max_length=20)),
                ("matched_keyword", models.CharField(blank=True, max_length=100, null=True)),
                ("recommended_approver", models.CharField(blank=True, max_length=100)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending", max_length=10)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-submitted_at"],
            },
        ),
    ]
