cd C:\Users\stu875651\Downloads\it_assets_app
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

http://localhost:8000/

# IT Assets Webapp (FastAPI + SQLAlchemy + SQLite)

A simple web application to track Staff, Computers, and Special Software.
- Backend: FastAPI
- ORM: SQLAlchemy 2.x Declarative
- DB: SQLite (`app.db`)
- UI: Server-rendered forms (Jinja2) + Swagger at `/docs`

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: http://localhost:8000/
API docs: http://localhost:8000/docs

## Database
Tables are created automatically at startup and stored in `app.db`. You can also run:

```bash
python scripts/init_db.py
python scripts/seed.py  # optional sample data
```

## Structure
```
it_assets_app/
  app/
    main.py
    database.py
    models.py
    schemas.py
    crud.py
    api/routers/
      staff.py
      computers.py
      software.py
    templates/
      base.html
      index.html
      staff_list.html
      staff_new.html
      computer_list.html
      computer_new.html
      software_list.html
      software_new.html
    static/
      style.css
  scripts/
    init_db.py
    seed.py
  requirements.txt
  README.md
```

## Notes
- SQLite foreign keys are enforced via `PRAGMA foreign_keys = ON`.
- Unique constraints on `service_tag` and `comp_name` prevent duplicates.
- `manager_staff_id` references the `staff` table and is optional.
