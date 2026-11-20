# HOA Command Center

A responsive HOA management operations demo for community managers, residents, board members, and vendors.

## Included demo capabilities

- Community operations dashboard for a fictional 286-home community.
- Resident service requests and maintenance work orders.
- Manager triage, insured-vendor assignment, work-order status progression, and audit history.
- Architectural review decisions and board action tracking.
- Vendor directory with insurance-readiness indicator.
- Financial management: fictional homeowner assessments, outstanding balances, demo payment entries, vendor invoices, and invoice status decisions.
- Demo persona selector for Manager, Resident, Vendor, Board, and Administrator.

## Financial demo data

The Financial Management page contains illustrative November 2026 assessments, balances, vendor invoices, and payment records. The **Record demo payment** action only writes a fictional ledger entry to the application's local database. It does not connect to a bank, card processor, payment gateway, or real homeowner account. No money is collected.

All names, unit numbers, balances, invoices, and operational records are fictional.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. SQLite is used when `DATABASE_URL` is not configured.

## Deploy on Render (free demo)

1. In Render, choose **New → Blueprint** and select this repository.
2. Review the Blueprint plan. It defines one **Free web service** and no paid database.
3. Apply the plan after confirming it contains no paid resources.
4. Render builds the Flask application and starts it with Gunicorn.

The free deployment uses SQLite in the service filesystem. Treat it as a demonstration environment: data can be lost on restart, redeploy, or service replacement, and the free service may spin down when idle. Do not use it for production HOA records or real payments.

## Important security and production limitations

The persona selector is a UI demonstration only; it is not authentication or enforced role-based access control. Before any real HOA use, implement verified user identity, server-enforced permissions, tenant/community data isolation, secure document storage, audit protections, backups, privacy controls, and a production database. Payment collection requires a compliant payment provider and appropriate security and financial controls.

This project is a functional portfolio demonstration, not a production-ready HOA accounting or payment platform.
