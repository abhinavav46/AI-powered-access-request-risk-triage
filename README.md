# AI-Powered Access Request Risk Triage

A small, professional Django web application that simulates a real IAM
(Identity and Access Management) workflow: an employee submits a request for
system/data access, and an **AI model reads the free-text justification and
automatically scores its risk** (Low / Medium / High), then recommends who
should approve it. A reviewer can approve or reject each request from a
dashboard.

This is designed as a learning project that's still realistic enough to show
to an interviewer or put on a resume/portfolio — it combines full-stack web
development, applied machine learning, and IAM domain concepts in one place.

---

## Why this project

- **Full-stack Django**: models, forms, views, templates, admin, URL routing,
  a management command, and a test suite — the standard pieces of a real
  Django app.
- **Real AI, not a gimmick**: a machine learning model is actually trained
  from labeled data (not just an if/else chain), using scikit-learn. It runs
  fully offline — no paid API keys, no external AI service, no internet
  dependency once deployed.
- **Domain-relevant**: the "access request risk triage" idea mirrors real
  IAM/security governance tools (like SailPoint), so it's a natural addition
  to a resume that already includes IAM and SailPoint experience.
- **Testable**: includes a Django test suite covering the ML logic, the
  model, and the views — the same mindset as automation/QA testing.

---

## How the AI works

1. **Training data** (`triage/data/training_data.csv`): ~70 example access
   requests, each hand-labeled `low`, `medium`, or `high` risk. Examples:
   - *"Please give me read access to the company newsletter"* → `low`
   - *"Requesting access to the staging environment for testing"* → `medium`
   - *"I need root access to the production database"* → `high`

2. **TF-IDF vectorization**: turns each request's text into a vector of
   word/phrase importance scores (including two-word phrases like "root
   access", not just single words).

3. **Logistic Regression classifier**: learns which words/phrases push a
   request toward each risk level. Trained with `class_weight="balanced"`
   since the dataset is small and not perfectly even across classes.

4. **Rule-based safety net** (`triage/ml/predictor.py`): on top of the ML
   model, a short list of critical keywords ("root access", "bypass MFA",
   "delete production", "encryption key", etc.) will always force a request
   to `high` risk, regardless of what the model predicts. This is a real
   defense-in-depth pattern used in actual security tooling — you never let
   a probabilistic model be the *only* thing standing between a user and a
   dangerous access grant, and it also makes the system's behavior easy to
   explain in a demo or interview.

5. The model is saved to `triage/ml/risk_model.joblib` with `joblib`, and
   loaded once (singleton) by the Django app — so classification at request
   time is instant, with no retraining needed per request.

You can retrain the model any time with:
```bash
python manage.py train_model
```

---

## Project structure

```
access-risk-triage-django/
├── manage.py
├── requirements.txt
├── access_risk_triage/        # Django project (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── triage/                    # Django app
    ├── models.py               # AccessRequest model
    ├── forms.py                 # Submission form
    ├── views.py                 # Submit / dashboard / detail / status / API
    ├── urls.py
    ├── admin.py                 # Django admin registration
    ├── tests.py                 # Automated test suite
    ├── management/commands/
    │   └── train_model.py       # `python manage.py train_model`
    ├── ml/
    │   ├── predictor.py          # Loads model + rule-based safety net
    │   └── risk_model.joblib     # Pre-trained model (included, ready to use)
    ├── data/
    │   └── training_data.csv     # Labeled training examples
    ├── templates/triage/         # HTML templates
    └── static/triage/            # CSS + JS (incl. live AI preview)
```

---

## Setup (run locally)

> **Note:** this was built in an offline sandbox without internet access, so
> Django itself couldn't be pip-installed or run there — the code was written
> by hand following standard Django conventions and every `.py` file was
> syntax-checked. The ML model (training data, scikit-learn pipeline,
> predictor logic) *was* fully trained and tested and works correctly. Please
> run the steps below locally as your first step, mainly to run
> `makemigrations`/`migrate` and confirm the server boots — if anything needs
> a tweak it should be minor.

1. **Clone and enter the project**
   ```bash
   git clone https://github.com/<your-username>/access-risk-triage-django.git
   cd access-risk-triage-django
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate        # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

4. **(Optional) retrain the AI model** — a pre-trained model is already
   included, but you can retrain it any time:
   ```bash
   python manage.py train_model
   ```

5. **Create an admin user** (to view submissions in Django admin)
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/` to submit a request, and
   `http://127.0.0.1:8000/dashboard/` to review submitted requests.

7. **Run the test suite**
   ```bash
   python manage.py test
   ```

---



---
