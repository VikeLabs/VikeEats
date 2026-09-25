"""Schema definition for VikeEats.

The tables are declared at module level so the rest of the app can import them
directly instead of calling ``MetaData.reflect()`` against a live database on
every request:

    from .create_db import food_outlets, menu_items

The model is three levels: a **building** is a place on campus (The Cove,
Mystic Market, The SUB), a **food outlet** is a kiosk inside one (Verde,
Chopbox, Bean There Cafe), and **menu items** hang directly off an outlet with
their category as a plain string.
"""
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    TEXT,
    UniqueConstraint,
    VARCHAR,
)

metadata_obj = MetaData()

# Physical places on campus. Carries the map/card presentation data that used
# to be hardcoded as BUILDING_METADATA in ui.py.
buildings = Table(
    "buildings", metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", VARCHAR, nullable=False, unique=True),
    Column("location", VARCHAR),
    Column("lat", Float),
    Column("lng", Float),
    Column("image", VARCHAR),
)

# Individual kiosks/counters, each inside exactly one building.
food_outlets = Table(
    "food_outlets", metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", VARCHAR, nullable=False),
    Column("building_id", Integer, ForeignKey("buildings.id"), nullable=False),
    UniqueConstraint("building_id", "name", name="uq_outlet_per_building"),
)

# One row per outlet per weekday.
daily_hours = Table(
    "daily_hours", metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("food_outlet_id", Integer, ForeignKey("food_outlets.id"), nullable=False),
    Column("day", VARCHAR, nullable=False),
    Column("is_closed", Boolean, default=False),
    Column("display_hours", VARCHAR),
    UniqueConstraint("food_outlet_id", "day", name="uq_hours_per_outlet_day"),
)

# An outlet can open and close several times a day (Feast serves breakfast,
# lunch and dinner), so each daily_hours row owns zero or more slots.
time_slots = Table(
    "time_slots", metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("daily_hours_id", Integer, ForeignKey("daily_hours.id"), nullable=False),
    Column("start_time", VARCHAR),
    Column("end_time", VARCHAR),
)

# Category is a plain string rather than its own table: it only ever groups
# items within one outlet, and never carried data of its own.
menu_items = Table(
    "menu_items", metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("outlet_id", Integer, ForeignKey("food_outlets.id"), nullable=False),
    Column("category", VARCHAR, nullable=False, default="Main"),
    Column("name", VARCHAR, nullable=False),
    Column("ingredients", TEXT),
    Column("allergens", VARCHAR),
    UniqueConstraint("outlet_id", "category", "name", name="uq_item_per_category"),
)

dietary_restrictions = Table(
    "dietary_restrictions", metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", VARCHAR, nullable=False, unique=True),
)

menu_item_restrictions = Table(
    "menu_item_restrictions", metadata_obj,
    Column("menu_item_id", Integer, ForeignKey("menu_items.id"), primary_key=True, nullable=False),
    Column("restriction_id", Integer, ForeignKey("dietary_restrictions.id"), primary_key=True, nullable=False),
)

# Delete order for a full refresh: children before the rows they reference.
TABLE_CLEAR_ORDER = [
    "menu_item_restrictions",
    "menu_items",
    "time_slots",
    "daily_hours",
    "food_outlets",
    "buildings",
    "dietary_restrictions",
]


def create_database():
    from .config import get_engine
    engine = get_engine()
    metadata_obj.create_all(engine)
    print("Database and tables created successfully!")


if __name__ == "__main__":
    create_database()
