import pytest
from api.db import db_ufo
import sqlalchemy as sa

def test_db_populate_outlets(mock_db, requests_mock, mock_uvic_index, mock_uvss_sub):
    # Mock both UVic and UVSS websites
    requests_mock.get("https://www.uvic.ca/services/food/where/index.php", text=mock_uvic_index)
    requests_mock.get("https://uvss.ca/thesub/", text=mock_uvss_sub)
    
    # Run population
    db_ufo()
    
    # Verify results in DB
    with mock_db.connect() as conn:
        result = conn.execute(sa.text("SELECT name FROM food_outlets")).fetchall()
        names = [r[0] for r in result]
        
        # Normlized names from mock data
        # Bibliocafe, Mystic Market (UVic)
        # Bean There, Fels, The Grill, Munchie Bar, Health Food Bar (SUB)
        assert "bibliocafe" in names
        assert "mystic market" in names
        assert "bean there" in names
        assert "fels" in names
