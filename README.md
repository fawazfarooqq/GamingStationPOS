# GamingStation — Full-Stack Gaming Center POS

A college-project-friendly, full-stack POS system for a gaming station / gaming cafe.

## Features

- 10 managed stations: PS5, PS4, Pool and Tennis tables
- Start/stop timed gaming sessions
- Automatic duration and billing
- Customer name + mobile capture
- Product / snack inventory
- Cart and product sales
- Session + product combined checkout
- Multiple payment methods: Cash, UPI, Card
- Customers / CRM
- Expenses
- Daily dashboard metrics
- Revenue and station utilization reports
- CSV export
- Product stock tracking and low-stock alerts
- Session history
- Search/filterable transactions
- Settings for station rates and business name
- SQLite persistence through Flask backend
- REST API
- Responsive dark neon UI
- Automated backend tests

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:

http://127.0.0.1:5000

## Test

```powershell
pytest -q
```

## Project structure

```text
GamingStation-POS/
├── app.py
├── requirements.txt
├── README.md
├── app/
│   ├── db.py
│   ├── services.py
│   ├── templates/index.html
│   └── static/app.js
├── data/
└── tests/
    └── test_api.py
```

## Notes

This is a local POS prototype. It is designed to demonstrate a complete software project with persistent data and a REST API. For production deployment, add authentication/authorization, database backups, audit logs, HTTPS, printer/payment-terminal integration, and stronger validation.
