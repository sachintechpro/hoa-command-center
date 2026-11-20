# HOA Command Center

A modern HOA management operations demo for community managers, residents, board members, vendors, and administrators.

## Initial release
- Role-based demo views (demo persona switcher; not production authentication)
- Community overview and operational dashboard
- Resident service requests and maintenance work orders
- Manager triage, vendor assignment, status progression, and completion verification
- Architectural review decisions and board action tracking
- Audit history and seeded fictional Canyon Ridge HOA data

## Local run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. SQLite is used locally when `DATABASE_URL` is not set.

## Render

Use **New → Blueprint** in Render and select this repository. Review the proposed web service and PostgreSQL database, including their plan and pricing, before applying. The app reads `DATABASE_URL` and initializes its demo schema on startup.

## Demo personas

Manager, Resident, Vendor, Board, and Administrator. The persona selector is only a demonstration convenience; production deployment requires real authentication, authorization enforcement, privacy controls, and security review.

All names, addresses, balances, and operational records are fictional. Do not enter real homeowner or payment data.
