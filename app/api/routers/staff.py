
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import SessionLocal, engine
from ...models import Staff
from ...schemas import StaffCreate, StaffUpdate, StaffOut
from ...crud import create_staff, list_staff, get_staff, update_staff, delete_staff

router = APIRouter(prefix='/api/staff', tags=['staff'])

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/', response_model=list[StaffOut])
async def api_list_staff(db: Session = Depends(get_db)):
    return list_staff(db)

@router.post('/', response_model=StaffOut)
async def api_create_staff(payload: StaffCreate, db: Session = Depends(get_db)):
    return create_staff(db, name=payload.name, email=payload.email)

@router.get('/{staff_id}', response_model=StaffOut)
async def api_get_staff(staff_id: int, db: Session = Depends(get_db)):
    obj = get_staff(db, staff_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Staff not found')
    return obj

@router.put('/{staff_id}', response_model=StaffOut)
async def api_update_staff(staff_id: int, payload: StaffUpdate, db: Session = Depends(get_db)):
    obj = update_staff(db, staff_id, **payload.dict())
    if not obj:
        raise HTTPException(status_code=404, detail='Staff not found')
    return obj

@router.delete('/{staff_id}')
async def api_delete_staff(staff_id: int, db: Session = Depends(get_db)):
    ok = delete_staff(db, staff_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Staff not found')
    return {'ok': True}
