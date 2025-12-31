
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import create_staff, create_computer, create_software

print('Seeding sample data...')
db: Session = SessionLocal()

try:
    # Staff
    taylor = create_staff(db, 'Taylor Smith', 'taylor.smith@example.edu')
    james = create_staff(db, 'James Young', 'james.young@example.edu')
    rick = create_staff(db, 'Rick Crowder', 'rick.crowder@example.edu')

    # Computers
    c1 = create_computer(db,
        staff_id=taylor.staff_id,
        comp_name='tsmith-mbp',
        computer_model='MacBook Pro 14 (M3)',
        service_tag='DT1234A',
        warranty_end=None,
        is_manager=1,
    )
    c2 = create_computer(db,
        staff_id=james.staff_id,
        comp_name='jyoung-mba',
        computer_model='MacBook Air 13 (M2)',
        service_tag='DT5678B',
        warranty_end=None,
        is_manager=0,
    )

    # Software
    create_software(db, computer_id=c1.computer_id, software_name='Jamf Pro')
    create_software(db, computer_id=c1.computer_id, software_name='Adobe Creative Cloud')
    create_software(db, computer_id=c2.computer_id, software_name='BarTender')
finally:
    db.close()

print('Seed complete.')
