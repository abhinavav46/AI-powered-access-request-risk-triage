"""
Django management command: python manage.py train_model

Trains the TF-IDF + Logistic Regression risk classifier from
triage/data/training_data.csv and saves it to triage/ml/risk_model.joblib.

Why a management command instead of a plain script?
Django management commands are the standard, professional way to package
one-off / maintenance operations (data imports, retraining, cleanup jobs)
inside a Django project, so they show up alongside `migrate`, `runserver`,
etc. when you run `python manage.py help`.
"""

import os
import joblib
import pandas as pd
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(APP_DIR, "data", "training_data.csv")
MODEL_PATH = os.path.join(APP_DIR, "ml", "risk_model.joblib")


class Command(BaseCommand):
    help = "Trains the access-request risk classifier and saves it to triage/ml/risk_model.joblib"

    def handle(self, *args, **options):
        df = pd.read_csv(DATA_PATH)
        X = df["request_text"]
        y = df["risk_label"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ])

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        report = classification_report(y_test, y_pred, zero_division=0)
        self.stdout.write(self.style.SUCCESS("=== Model evaluation on held-out test data ==="))
        self.stdout.write(report)

        joblib.dump(pipeline, MODEL_PATH)
        self.stdout.write(self.style.SUCCESS(f"Model saved to: {MODEL_PATH}"))
