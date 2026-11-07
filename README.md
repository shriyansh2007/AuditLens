# AuditLens – Internal Audit & Control Testing System

AuditLens is a Python-based internal audit analytics application that
evaluates financial transactions against predefined internal controls.

## Features

- Duplicate invoice detection
- Missing approval detection
- Approval authority verification
- Missing documentation detection
- Segregation of duties testing
- Risk scoring and classification
- SQLite database
- Investigation status tracking
- Interactive Streamlit dashboard
- CSV export

## Technology Stack

- Python
- Pandas
- SQLite
- Streamlit
- Plotly

## Dataset

This project uses 1,000 synthetically generated financial transactions
and 25 synthetic employees. Certain records deliberately contain
control exceptions to test the audit rules.

## Run Locally

Install dependencies:

    python -m pip install -r requirements.txt

Generate data and audit results by running the notebook cells
or the Python scripts.

Launch the dashboard:

    python -m streamlit run app.py

Open http://localhost:8501

## Audit Rules

1. Duplicate Payment
2. Missing Approval
3. Approval Limit Violation
4. Missing Documentation
5. Segregation of Duties Violation

## Risk Scoring

Each exception contributes points to a transaction's risk score.
The total is capped at 100.

- Low: 0–19
- Medium: 20–39
- High: 40–69
- Critical: 70–100

These scores are illustrative prioritization indicators, not
statistical probabilities of fraud or financial loss.

## Disclaimer

AuditLens is an educational prototype using synthetic data.
Flagged transactions require human investigation and do not
establish fraud, misconduct or financial loss.

## Author

Shriyansh Goyal
B.Tech ECE, NSUT Delhi
