
# ---- CSV + utilities ----
import csv
from io import StringIO
from datetime import date

# FastAPI / responses / templates / DB session
from fastapi import FastAPI, Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Helpers for CSV parsing
from .utils import parse_date_loose, parse_bool_loose

# ORM / CRUD
from .database import Base, engine, SessionLocal
from .models import Staff, Computer, SpecialSoftware
from .crud import (
    create_staff, list_staff, delete_staff,
    create_computer, list_computers, delete_computer,
    create_software, list_software, delete_software
)

# JSON API routers (kept)
from .api.routers import staff as staff_api, computers as computers_api, software as software_api

app = FastAPI(title='IT Assets Webapp')

# Create tables at startup
Base.metadata.create_all(bind=engine)

# Static & templates
app.mount('/static', StaticFiles(directory='app/static'), name='static')
templates = Jinja2Templates(directory='app/templates')

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include JSON API routers
app.include_router(staff_api.router)
app.include_router(computers_api.router)
app.include_router(software_api.router)

# ------------------ UI PAGES ------------------
@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

# ------------------ Staff ------------------
@app.get('/staff')
async def staff_list(request: Request, sort: str = 'name', dir: str = 'asc', q: str = '', db: Session = Depends(get_db)):
    sort = sort if sort in {'id', 'name', 'email'} else 'name'
    dir = 'desc' if dir == 'desc' else 'asc'
    rows = list_staff(db, sort, dir, q)
    return templates.TemplateResponse('staff_list.html', {'request': request, 'staff': rows, 'sort': sort, 'dir': dir, 'q': q})

@app.get('/staff/new')
async def staff_new(request: Request):
    return templates.TemplateResponse('staff_new.html', {'request': request})

@app.post('/staff/new')
async def staff_create(name: str = Form(...), email: str | None = Form(None), db: Session = Depends(get_db)):
    create_staff(db, name=name, email=email)
    return RedirectResponse('/staff', status_code=303)

@app.post('/staff/{staff_id}/delete')
async def staff_delete(staff_id: int, db: Session = Depends(get_db)):
    delete_staff(db, staff_id)
    return RedirectResponse('/staff', status_code=303)

@app.get('/staff/{staff_id}/edit')
async def staff_edit(request: Request, staff_id: int, db: Session = Depends(get_db)):
    obj = db.query(Staff).get(staff_id)
    return templates.TemplateResponse('staff_edit.html', {'request': request, 'staff': obj})

@app.post('/staff/{staff_id}/edit')
async def staff_update(staff_id: int, name: str = Form(None), email: str | None = Form(None), db: Session = Depends(get_db)):
    from .crud import update_staff
    update_staff(db, staff_id, name=name, email=email)
    return RedirectResponse('/staff', status_code=303)

# ------------------ Computers ------------------
@app.get('/computers')
async def computers_list(request: Request, sort: str = 'comp_name', dir: str = 'asc', q: str = '', db: Session = Depends(get_db)):
    # add 'ticket_number' to sortable columns
    sort = sort if sort in {'id', 'comp_name', 'model', 'service_tag', 'owner', 'warranty_end', 'is_manager', 'ticket_number'} else 'comp_name'
    dir = 'desc' if dir == 'desc' else 'asc'
    rows = list_computers(db, sort, dir, q)
    return templates.TemplateResponse('computer_list.html', {'request': request, 'computers': rows, 'sort': sort, 'dir': dir, 'q': q})

@app.get('/computers/new')
async def computers_new(request: Request, db: Session = Depends(get_db)):
    # keep using list_staff(db) to populate dropdown
    return templates.TemplateResponse('computer_new.html', {'request': request, 'staff': list_staff(db)})

@app.post('/computers/new')
async def computers_create(
    staff_id: int = Form(...),
    comp_name: str = Form(...),
    computer_model: str = Form(...),
    service_tag: str = Form(...),
    warranty_end: str | None = Form(None),
    is_manager: str | None = Form(None),   # checkbox returns "1" or None
    ticket_number: str | None = Form(None),
    db: Session = Depends(get_db)
):
    we_date: date | None = None
    if warranty_end:
        try:
            we_date = date.fromisoformat(warranty_end)
        except ValueError:
            we_date = None

    payload = dict(
        staff_id=staff_id,
        comp_name=comp_name,
        computer_model=computer_model,
        service_tag=service_tag,
        warranty_end=we_date,
        is_manager=1 if is_manager else 0,
        ticket_number=ticket_number,
    )

    create_computer(db, **payload)
    return RedirectResponse('/computers', status_code=303)

@app.post('/computers/{computer_id}/delete')
async def computers_delete(computer_id: int, db: Session = Depends(get_db)):
    delete_computer(db, computer_id)
    return RedirectResponse('/computers', status_code=303)

@app.get('/computers/{computer_id}/edit')
async def computers_edit(request: Request, computer_id: int, db: Session = Depends(get_db)):
    obj = db.query(Computer).get(computer_id)
    staff = db.query(Staff).order_by(Staff.name).all()
    return templates.TemplateResponse('computer_edit.html', {'request': request, 'computer': obj, 'staff': staff})

@app.post('/computers/{computer_id}/edit')
async def computers_update(
    computer_id: int,
    staff_id: int = Form(None),
    comp_name: str = Form(None),
    computer_model: str = Form(None),
    service_tag: str = Form(None),
    warranty_end: str | None = Form(None),
    is_manager: str | None = Form(None),
    ticket_number: str | None = Form(None),
    db: Session = Depends(get_db)
):
    we_date = None
    if warranty_end:
        try:
            we_date = date.fromisoformat(warranty_end)
        except ValueError:
            we_date = None
    fields = dict(
        staff_id=staff_id,
        comp_name=comp_name,
        computer_model=computer_model,
        service_tag=service_tag,
        warranty_end=we_date,
        is_manager=1 if is_manager else 0,
        ticket_number=ticket_number,
    )
    from .crud import update_computer
    update_computer(db, computer_id, **fields)
    return RedirectResponse('/computers', status_code=303)

# ------------------ Software ------------------
@app.get('/software')
async def software_list_page(request: Request, sort: str = 'software_name', dir: str = 'asc', q: str = '', db: Session = Depends(get_db)):
    sort = sort if sort in {'id', 'software_name', 'computer'} else 'software_name'
    dir = 'desc' if dir == 'desc' else 'asc'
    rows = list_software(db, sort, dir, q)
    return templates.TemplateResponse('software_list.html', {'request': request, 'software': rows, 'sort': sort, 'dir': dir, 'q': q})

@app.get('/software/new')
async def software_new(request: Request, db: Session = Depends(get_db)):
    computers = db.query(Computer).order_by(Computer.comp_name).all()
    return templates.TemplateResponse('software_new.html', {'request': request, 'computers': computers})

@app.post('/software/new')
async def software_create(
    computer_id: int = Form(...),
    software_name: str = Form(...),
    db: Session = Depends(get_db)
):
    create_software(db, computer_id=computer_id, software_name=software_name)
    return RedirectResponse('/software', status_code=303)

@app.post('/software/{software_id}/delete')
async def software_delete(software_id: int, db: Session = Depends(get_db)):
    delete_software(db, software_id)
    return RedirectResponse('/software', status_code=303)

@app.get('/software/{software_id}/edit')
async def software_edit(request: Request, software_id: int, db: Session = Depends(get_db)):
    obj = db.query(SpecialSoftware).get(software_id)
    computers = db.query(Computer).order_by(Computer.comp_name).all()
    return templates.TemplateResponse('software_edit.html', {'request': request, 'software': obj, 'computers': computers})

@app.post('/software/{software_id}/edit')
async def software_update(software_id: int, computer_id: int = Form(None), software_name: str = Form(None), db: Session = Depends(get_db)):
    from .crud import update_software
    update_software(db, software_id, computer_id=computer_id, software_name=software_name)
    return RedirectResponse('/software', status_code=303)

# ------------------ Import / Export ------------------

@app.get("/import")
async def import_page(request: Request):
    return templates.TemplateResponse("import_export.html", {"request": request})



@app.post("/import")
async def import_csv(
    file: UploadFile = File(...),
    overwrite: str | None = Form(None),     # checkbox: "1" -> True, None -> False
    db: Session = Depends(get_db)
):
    raw = await file.read()
    text = raw.decode("utf-8", errors="replace")

    # Detect delimiter; fallback to tab vs comma heuristic
    try:
        from csv import Sniffer
        dialect = Sniffer().sniff(text.splitlines()[0])
        delim = dialect.delimiter
    except Exception:
        first_line = text.splitlines()[0] if text.splitlines() else ""
        delim = "\t" if first_line.count("\t") >= first_line.count(",") else ","

    # Use index-based parsing to handle duplicate headers (e.g., multiple "Special software")
    r = csv.reader(StringIO(text), delimiter=delim)
    rows = list(r)
    if not rows:
        return {"ok": True, "message": "Imported CSV. No rows found."}

    headers = rows[0]

    def norm(s: str | None) -> str:
        return (s or "").lstrip("\ufeff").strip().lower()  # strip BOM, trim, lowercase

    norm_headers = [norm(h) for h in headers]

    def find_index(*candidates: str) -> int | None:
        # exact normalized match first
        for c in candidates:
            c_norm = norm(c)
            if c_norm in norm_headers:
                return norm_headers.index(c_norm)
        # fuzzy: first header containing any candidate substring
        for i, h in enumerate(norm_headers):
            if any(norm(c) in h for c in candidates):
                return i
        return None

    # Column indices
    idx_staff    = find_index("fac/staff name", "staff name", "name")
    idx_comp     = find_index("comp name", "computer name", "hostname")
    idx_type     = find_index("type", "model", "computer model")
    idx_st       = find_index("st", "service tag", "serial", "service_tag")
    idx_warranty = find_index("warranty end", "warranty", "warranty_end")
    idx_manager  = find_index("manager's account", "manager", "is_manager")
    idx_ticket   = find_index("ticket number", "ticket", "issue key")  # optional

    # ALL indices for "Special software" columns (duplicate headers supported)
    sw_indices = [i for i, h in enumerate(norm_headers) if ("special" in h) or ("software" in h)]

    from .models import Staff, Computer, SpecialSoftware
    from .crud import create_staff

    overwrite_flag = bool(overwrite)
    created = updated = 0
    sw_added_total = 0

    # Process data rows
    for row in rows[1:]:
        # Pad short rows (Excel sometimes truncates trailing empty cells)
        if len(row) < len(headers):
            row = row + [""] * (len(headers) - len(row))

        staff_name    = (row[idx_staff]    if idx_staff    is not None else "").strip()
        comp_name     = (row[idx_comp]     if idx_comp     is not None else "").strip()
        comp_model    = (row[idx_type]     if idx_type     is not None else "").strip()
        service_tag   = (row[idx_st]       if idx_st       is not None else "").strip()
        warranty_raw  = (row[idx_warranty] if idx_warranty is not None else "").strip()
        is_manager_raw= (row[idx_manager]  if idx_manager  is not None else "").strip()
        ticket_number = (row[idx_ticket]   if idx_ticket   is not None else "").strip() or None

        warranty_end = parse_date_loose(warranty_raw or None)
        is_manager   = parse_bool_loose(is_manager_raw or None)

        # Minimal required fields
        if not staff_name or not comp_name or not service_tag:
            continue

        # Ensure Staff exists
        staff_obj = db.query(Staff).filter(Staff.name == staff_name).first()
        if not staff_obj:
            staff_obj = create_staff(db, name=staff_name, email=None)

        # ✅ Upsert Computer: by service_tag first, else fallback by comp_name
        comp_obj = db.query(Computer).filter(Computer.service_tag == service_tag).first()
        if not comp_obj:
            comp_obj = db.query(Computer).filter(Computer.comp_name == comp_name).first()

        if not comp_obj:
            # INSERT new computer
            comp_obj = Computer(
                staff_id=staff_obj.staff_id,
                comp_name=comp_name,
                computer_model=comp_model or "Unknown",
                service_tag=service_tag,
                warranty_end=warranty_end,
                is_manager=is_manager,
                ticket_number=ticket_number,
            )
            db.add(comp_obj)
            db.commit()
            db.refresh(comp_obj)
            created += 1
        else:
            # UPDATE existing computer
            comp_obj.staff_id       = staff_obj.staff_id
            comp_obj.comp_name      = comp_name or comp_obj.comp_name
            comp_obj.computer_model = comp_model or comp_obj.computer_model
            comp_obj.warranty_end   = warranty_end or comp_obj.warranty_end
            comp_obj.is_manager     = is_manager
            comp_obj.ticket_number  = ticket_number or comp_obj.ticket_number

            # If matched by comp_name and CSV provides a new service_tag, only apply it if unused elsewhere
            if service_tag and comp_obj.service_tag != service_tag:
                tag_conflict = db.query(Computer).filter(
                    Computer.service_tag == service_tag,
                    Computer.computer_id != comp_obj.computer_id
                ).first()
                if not tag_conflict:
                    comp_obj.service_tag = service_tag
            db.commit()
            updated += 1

        # 🧩 Software import: overwrite or append without duplicates
        if sw_indices:
            if overwrite_flag:
                db.query(SpecialSoftware).filter(
                    SpecialSoftware.computer_id == comp_obj.computer_id
                ).delete()
                db.commit()

            for si in sw_indices:
                val = (row[si] or "").strip()
                if not val:
                    continue
                exists = db.query(SpecialSoftware).filter(
                    SpecialSoftware.computer_id == comp_obj.computer_id,
                    SpecialSoftware.software_name == val
                ).first()
                if not exists:
                    db.add(SpecialSoftware(computer_id=comp_obj.computer_id, software_name=val))
                    sw_added_total += 1
            db.commit()

    return {
        "ok": True,
        "message": f"Imported CSV. Created {created} computers, updated {updated}. Software added: {sw_added_total}."
    }


@app.get("/export/computers.csv")
async def export_computers_csv(db: Session = Depends(get_db)):
    from .models import Computer, Staff, SpecialSoftware
    from sqlalchemy import func

    # Collect computers + owner
    comps = db.query(Computer).join(Staff, Computer.staff_id == Staff.staff_id).all()

    # Determine max software count per computer (at least 6 to match your layout)
    sw_counts = {
        c.computer_id: db.query(func.count(SpecialSoftware.software_id))
                          .filter(SpecialSoftware.computer_id == c.computer_id)
                          .scalar()
        for c in comps
    }
    max_sw = max(sw_counts.values()) if sw_counts else 0
    max_sw = max(max_sw, 6)

    # Build CSV in-memory
    output = StringIO()
    writer = csv.writer(output)
    # include Ticket number in header
    header = ["Fac/Staff Name", "Comp Name", "Type", "ST", "Warranty End", "Manager's account", "Ticket number"] \
             + ["Special software"] * max_sw
    writer.writerow(header)

    for c in comps:
        owner  = c.owner.name if c.owner else ""
        is_mgr = "TRUE" if (c.is_manager or 0) else "FALSE"
        we_str = c.warranty_end.isoformat() if c.warranty_end else ""
        sw     = db.query(SpecialSoftware).filter(SpecialSoftware.computer_id == c.computer_id) \
                                          .order_by(SpecialSoftware.software_name).all()
        sw_names = [s.software_name for s in sw][:max_sw]
        sw_names += [""] * (max_sw - len(sw_names))  # pad
        # include ticket_number in each row
        row = [owner, c.comp_name, c.computer_model, c.service_tag, we_str, is_mgr, c.ticket_number or ""] + sw_names
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=\"computers_export.csv\""}
    )
