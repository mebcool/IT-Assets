
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from . import models

# ---------- Staff ----------

def create_staff(db: Session, name: str, email: str | None):
    obj = models.Staff(name=name, email=email)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_staff(db: Session, sort: str = "name", dir: str = "asc", q: str = ""):
    colmap = {"id": models.Staff.staff_id, "name": models.Staff.name, "email": models.Staff.email}
    col = colmap.get(sort, models.Staff.name)
    ordering = asc(col) if dir == "asc" else desc(col)

    stmt = select(models.Staff)
    if q:
        stmt = stmt.where(models.Staff.name.ilike(f"%{q}%") | models.Staff.email.ilike(f"%{q}%"))
    stmt = stmt.order_by(ordering)
    return db.scalars(stmt).all()


def get_staff(db: Session, staff_id: int):
    return db.get(models.Staff, staff_id)


def update_staff(db: Session, staff_id: int, **fields):
    obj = get_staff(db, staff_id)
    if not obj:
        return None
    for k, v in fields.items():
        if v is not None:
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_staff(db: Session, staff_id: int):
    obj = get_staff(db, staff_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

# ---------- Computers ----------

def create_computer(db: Session, **fields):
    obj = models.Computer(**fields)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj




def list_computers(db: Session, sort: str = "comp_name", dir: str = "asc", q: str = ""):
    colmap = {
        "id": models.Computer.computer_id,
        "comp_name": models.Computer.comp_name,
        "model": models.Computer.computer_model,
        "service_tag": models.Computer.service_tag,
        "warranty_end": models.Computer.warranty_end,
        "is_manager": models.Computer.is_manager,
        "owner": models.Staff.name,  # sort by owner's name
    }

    col = colmap.get(sort, models.Computer.comp_name)
    ordering = asc(col) if dir == "asc" else desc(col)

    # ✅ Explicit owner join (disambiguates FK choice)
    stmt = (
        select(models.Computer)
        .join(
            models.Staff,
            models.Computer.staff_id == models.Staff.staff_id
        )
    )

    if q:
        stmt = stmt.where(
            models.Computer.comp_name.ilike(f"%{q}%")
            | models.Computer.computer_model.ilike(f"%{q}%")
            | models.Computer.service_tag.ilike(f"%{q}%")
            | models.Staff.name.ilike(f"%{q}%")
        )

    stmt = stmt.order_by(ordering)

    # unique() prevents duplicates due to the join
    return db.scalars(stmt).unique().all()



def get_computer(db: Session, computer_id: int):
    return db.get(models.Computer, computer_id)


def update_computer(db: Session, computer_id: int, **fields):
    obj = get_computer(db, computer_id)
    if not obj:
        return None
    for k, v in fields.items():
        if v is not None:
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_computer(db: Session, computer_id: int):
    obj = get_computer(db, computer_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

# ---------- Special Software ----------

def create_software(db: Session, **fields):
    obj = models.SpecialSoftware(**fields)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj



def list_software(db: Session, sort: str = "software_name", dir: str = "asc", q: str = ""):
    colmap = {
        "id": models.SpecialSoftware.software_id,
        "software_name": models.SpecialSoftware.software_name,
        "computer": models.Computer.comp_name,
    }
    col = colmap.get(sort, models.SpecialSoftware.software_name)
    ordering = asc(col) if dir == "asc" else desc(col)

    stmt = select(models.SpecialSoftware).join(models.Computer)
    if q:
        stmt = stmt.where(
            models.SpecialSoftware.software_name.ilike(f"%{q}%")
            | models.Computer.comp_name.ilike(f"%{q}%")
        )
    stmt = stmt.order_by(ordering)
    return db.scalars(stmt).unique().all()



def get_software(db: Session, software_id: int):
    return db.get(models.SpecialSoftware, software_id)


def update_software(db: Session, software_id: int, **fields):
    obj = get_software(db, software_id)
    if not obj:
        return None
    for k, v in fields.items():
        if v is not None:
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_software(db: Session, software_id: int):
    obj = get_software(db, software_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
