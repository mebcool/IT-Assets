
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import SessionLocal
from ...schemas import SoftwareCreate, SoftwareUpdate, SoftwareOut
from ...crud import create_software, list_software, get_software, update_software, delete_software

router = APIRouter(prefix='/api/software', tags=['software'])

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/', response_model=list[SoftwareOut])
async def api_list_software(db: Session = Depends(get_db)):
    return list_software(db)

@router.post('/', response_model=SoftwareOut)
async def api_create_software(payload: SoftwareCreate, db: Session = Depends(get_db)):
    return create_software(db, **payload.dict())

@router.get('/{software_id}', response_model=SoftwareOut)
async def api_get_software(software_id: int, db: Session = Depends(get_db)):
    obj = get_software(db, software_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Software not found')
    return obj

@router.put('/{software_id}', response_model=SoftwareOut)
async def api_update_software(software_id: int, payload: SoftwareUpdate, db: Session = Depends(get_db)):
    obj = update_software(db, software_id, **payload.dict())
    if not obj:
        raise HTTPException(status_code=404, detail='Software not found')
    return obj

@router.delete('/{software_id}')
async def api_delete_software(software_id: int, db: Session = Depends(get_db)):
    ok = delete_software(db, software_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Software not found')
    return {'ok': True}
