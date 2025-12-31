

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import Base, engine
from app import models

print('Creating database tables...')
Base.metadata.create_all(bind=engine)
print('Done. SQLite file: app.db')
