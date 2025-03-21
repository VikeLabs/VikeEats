from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Boolean, VARCHAR, TEXT, ForeignKey

def create_database():
    engine = create_engine("sqlite:///vikeeats.db", echo=True)
    metadata_obj = MetaData()

    # Food outlets table
    food_outlets = Table(
        "food_outlets", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", VARCHAR, nullable=False),
        Column("location", VARCHAR)
    )

    # Operating hours for food outlets
    operating_hours = Table(
        "operating_hours", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("food_outlet_id", Integer, ForeignKey("food_outlets.id"), nullable=False),
        Column("day", VARCHAR, nullable=False),
        Column("is_closed", Boolean, default=False),
        Column("display_hours", VARCHAR)
    )

    # Time slots for operating hours
    time_slots = Table(
        "time_slots", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("operating_hours_id", Integer, ForeignKey("operating_hours.id"), nullable=False),
        Column("start_time", VARCHAR, nullable=False),
        Column("end_time", VARCHAR, nullable=False)
    )

    # Menu for each food outlet
    menus = Table(
        "menus", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("food_outlet_id", Integer, ForeignKey("food_outlets.id"), nullable=False),
        Column("name", VARCHAR, default="Main Menu")
    )

    # Menu categories
    menu_categories = Table(
        "menu_categories", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("menu_id", Integer, ForeignKey("menus.id"), nullable=False),
        Column("name", VARCHAR, nullable=False)
    )

    # Menu items
    menu_items = Table(
        "menu_items", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("category_id", Integer, ForeignKey("menu_categories.id"), nullable=False),
        Column("name", VARCHAR, nullable=False),
        Column("ingredients", TEXT),
        Column("allergens", VARCHAR)
    )

    # Dietary restrictions
    dietary_restrictions = Table(
        "dietary_restrictions", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", VARCHAR, nullable=False, unique=True)
    )

    # Junction table for menu items and dietary restrictions
    menu_item_restrictions = Table(
        "menu_item_restrictions", metadata_obj,
        Column("menu_item_id", Integer, ForeignKey("menu_items.id"), primary_key=True, nullable=False),
        Column("restriction_id", Integer, ForeignKey("dietary_restrictions.id"), primary_key=True, nullable=False)
    )

    metadata_obj.create_all(engine)
    print("Database and tables created successfully!")

if __name__ == "__main__":
    create_database()
