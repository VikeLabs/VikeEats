import pytest
import sys
import os
from flask import Flask
import sqlalchemy as sa

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import app as flask_app

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def mock_db(app, tmp_path):
    """A clean, temporary database for each test.

    Lives under pytest's tmp_path rather than the working directory, so a run
    can no longer leave a test_vikeeats.db behind in the repo.
    """
    import api.config

    db_file = tmp_path / "vikeeats_test.db"
    original_url = api.config.DB_URL
    api.config.set_db_url(f"sqlite:///{db_file.as_posix()}")

    # Initialize the database (create tables)
    from api.create_db import create_database
    create_database()

    yield api.config.get_engine()

    # Restoring disposes the test engine, releasing the file handle so pytest
    # can clear tmp_path on Windows.
    api.config.set_db_url(original_url)

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
