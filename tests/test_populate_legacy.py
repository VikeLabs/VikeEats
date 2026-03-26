import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.db import db_ufo, db_uoh, db_uts, db_um
import sqlalchemy as sa
import api.db
from api.create_db import create_database

# Use a temporary DB for testing
TEST_DB = "test_vikeeats_legacy.db"
if os.path.exists(TEST_DB):
    try:
        os.remove(TEST_DB)
    except:
        pass

# Monkeypatch api.db
api.db.DB_PATH = TEST_DB
api.db.DB_URL = f"sqlite:///{TEST_DB}"

# Initialize the database
create_database()

try:
    print("Updating food outlets...")
    ufo = db_ufo()
    print(f"Outlets: {len(ufo)}")
    
    print("Updating operating hours...")
    uoh = db_uoh()
    print(f"Hours: {len(uoh)}")
    
    print("Updating time slots...")
    uts = db_uts()
    print(f"Slots: {len(uts)}")
    
    # Cleanup
    if os.path.exists(TEST_DB):
        # Dispose engine to unlock file if needed
        # (db_ufo etc create their own engines usually, so we might need to wait or just ignore cleanup errors)
        pass
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
