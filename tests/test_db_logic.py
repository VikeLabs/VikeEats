import pytest
from api.db import db_ufo, process_menu_item
import sqlalchemy as sa
from sqlalchemy import MetaData, select

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


def test_process_menu_item_clears_allergens_on_rescrape(mock_db):
    """Re-scrape with empty allergens must not leave stale allergen text (safety)."""
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=mock_db)
    menu_items = metadata_obj.tables["menu_items"]
    dietary_restrictions = metadata_obj.tables["dietary_restrictions"]
    menu_item_restrictions = metadata_obj.tables["menu_item_restrictions"]
    menu_categories = metadata_obj.tables["menu_categories"]

    with mock_db.connect() as conn:
        conn.execute(
            menu_categories.insert().values(id=1, menu_id=1, name="Test Cat")
        )
        conn.commit()

    details_old = {
        "dietary restrictions": [],
        "ingredients": "flour, water",
        "allergens": "gluten, soy",
    }
    details_new = {
        "dietary restrictions": [],
        "ingredients": "flour, water",
        "allergens": "",
    }

    with mock_db.connect() as conn:
        process_menu_item(
            conn,
            menu_items,
            dietary_restrictions,
            menu_item_restrictions,
            1,
            "Test Item",
            details_old,
        )
        conn.commit()

    with mock_db.connect() as conn:
        process_menu_item(
            conn,
            menu_items,
            dietary_restrictions,
            menu_item_restrictions,
            1,
            "Test Item",
            details_new,
        )
        conn.commit()

    with mock_db.connect() as conn:
        row = conn.execute(
            select(menu_items.c.ingredients, menu_items.c.allergens).where(
                menu_items.c.name == "Test Item"
            )
        ).fetchone()

    assert row is not None
    assert row[0] == "flour, water"
    assert row[1] == ""
