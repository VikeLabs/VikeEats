import pytest
import sys
import os
from flask import Flask
import sqlalchemy as sa

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def mock_db(app):
    """Fixture to provide a clean, temporary database for each test."""
    test_db_path = 'test_vikeeats.db'
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass # Handle cases where it's still locked
    
    # Override DB_PATH in api.db
    import api.db
    original_db_path = api.db.DB_PATH
    original_db_url = api.db.DB_URL
    api.db.DB_PATH = test_db_path
    api.db.DB_URL = f"sqlite:///{test_db_path}"
    
    # Initialize the database (create tables)
    from api.create_db import create_database
    create_database()
    
    engine = sa.create_engine(api.db.DB_URL)
    yield engine
    
    # Restore original paths
    api.db.DB_PATH = original_db_path
    api.db.DB_URL = original_db_url
    
    # Cleanup after restore
    if os.path.exists(test_db_path):
        try:
            # We need to dispose the engine to release the file lock
            engine.dispose()
            os.remove(test_db_path)
        except:
            pass

@pytest.fixture
def mock_uvic_index():
    with open(os.path.join(os.path.dirname(__file__), 'mock_data', 'uvic_index.html'), 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def mock_uvss_sub():
    with open(os.path.join(os.path.dirname(__file__), 'mock_data', 'uvss_sub.html'), 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def mock_cove_menu():
    with open(os.path.join(os.path.dirname(__file__), 'mock_data', 'cove_menu.html'), 'r', encoding='utf-8') as f:
        return f.read()
