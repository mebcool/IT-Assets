
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import SessionLocal
from ...schemas import ComputerCreate, ComputerUpdate, ComputerOut
from ...crud import create_computer, list_computers, get_computer, update_computer, delete_computer

router = APIRouter(prefix='/api/computers', tags=['computers'])

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/', response_model=list[ComputerOut])
async def api_list_computers(db: Session = Depends(get_db)):
    return list_computers(db)

@router.post('/', response_model=ComputerOut)
async def api_create_computer(payload: ComputerCreate, db: Session = Depends(get_db)):
    return create_computer(db, **payload.dict())

@router.get('/{computer_id}', response_model=ComputerOut)
async def api_get_computer(computer_id: int, db: Session = Depends(get_db)):
    obj = get_computer(db, computer_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Computer not found')
    return obj

@router.put('/{computer_id}', response_model=ComputerOut)
async def api_update_computer(computer_id: int, payload: ComputerUpdate, db: Session = Depends(get_db)):
    obj = update_computer(db, computer_id, **payload.dict())
    if not obj:
        raise HTTPException(status_code=404, detail='Computer not found')
    return obj

@router.delete('/{computer_id}')
async def api_delete_computer(computer_id: int, db: Session = Depends(get_db)):
    ok = delete_computer(db, computer_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Computer not found')
    return {'ok': True}
