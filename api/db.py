from sqlalchemy import create_engine, MetaData, select
from . import sub_hours
from .food_outlets import get_food_outlets_dict
from .menu import mystic_cove_menu_dict, others_menus_dict
from . import create_db
import json
from flask import Flask, Blueprint, jsonify
import os
import re

# Database configuration
DB_PATH = 'vikeeats.db'
DB_URL = f"sqlite:///{DB_PATH}"

db_blueprint = Blueprint('db', __name__)
app = Flask(__name__)

MENU_MAPPING = {
    "the cove": {
        "type": "cove_mystic",
        "url": "https://www.uvic.ca/services/food/where/thecove/index.php",
        "sub_locations": {
            "Verde": "tabs-verde",
            "Mykonos": "tabs-mykonos",
            "Vikes Grill": "tabs-vikes-grill",
            "Bento": "tabs-bento",
            "The Sandwich Lab": "tabs-the-sandwich-lab",
            "Nonna's": "tabs-nonnas",
            "Feast": "tabs-feast",
            "Breads": "tabs-breads",
            "Halal": "tabs-halal",
            "Baked Goods": "tabs-baked-goods",
            "Soups": "tabs-soups"
        }
    },
    "mystic market": {
        "type": "cove_mystic",
        "url": "https://www.uvic.ca/services/food/where/mysticmarket/index.php",
        "sub_locations": {
            "Chopbox": "tabs-chopbox",
            "Fresco Taco": "tabs-fresco-taco",
            "Flamin' Good Chicken": "tabs-flamin-good-chicken",
            "Pickle and Spice": "tabs-pickle-and-spice",
            "Tofino's": "tabs-tofinos",
            "Yolk'd": "tabs-yolkd",
            "Shoyu": "tabs-shoyu",
            "Baked Goods": "tabs-baked-goods",
            "Soups": "tabs-soups"
        }
    },
    "biblio cafe": {
        "type": "other",
        "url": "https://www.uvic.ca/services/food/where/bibliocafe/index.php"
    },
    "arts cafe": {
        "type": "other",
        "url": "https://www.uvic.ca/services/food/where/artsplace/index.php"
    },
    "nibbles & bytes": {
        "type": "other",
        "url": "https://www.uvic.ca/services/food/where/nibblesbytes/index.php"
    },
    "sci cafe": {
        "type": "other",
        "url": "https://www.uvic.ca/services/food/where/scicafe/index.php"
    },
    "mac's": {
        "type": "other",
        "url": "https://www.uvic.ca/services/food/where/macs/index.php"
    }
}

# Main DB Route
@db_blueprint.route('/db')
def db_main():
    return jsonify("Welcome to the VikeEats Database :)")

# Route that creates DB
@db_blueprint.route('/db/create')
def db_create():
    create_db.create_database()
    return jsonify("Database Created :)")

# Function to Clear DB tables
def clear_db(conn, metadata):
    """Clears all data from the database tables in correct order."""
    table_order = [
        "menu_item_restrictions",
        "menu_items",
        "menu_categories",
        "menus",
        "time_slots",
        "operating_hours",
        "food_outlets",
        "dietary_restrictions"
    ]
    for table_name in table_order:
        if table_name in metadata.tables:
            conn.execute(metadata.tables[table_name].delete())
    conn.commit()

# Function to Normlize outlets names
def normalize_name(name):
    # Convert to lowercase
    name = name.lower().strip()
    
    # Remove 'the ' prefix if it exists
    if name.startswith('the '):
        name = name[4:]
    
    # Remove any trailing asterisks and whitespace
    name = re.sub(r'\*+$', '', name).strip()
    
    # Standardize apostrophes and quotes
    name = name.replace("’", "'").replace('"', "'")
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Specific case handling
    if "bibliocafe" in name:
        return "bibliocafe"
    
    return name

@db_blueprint.route('/db/update/all')
def db_update_all():
    """Triggers a full refresh of all database tables."""
    if not os.path.exists(DB_PATH):
        create_db.create_database()
    
    engine = create_engine(DB_URL)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)
    
    with engine.connect() as conn:
        clear_db(conn, metadata_obj)
        conn.commit() # Ensure changes are committed
    
    # Sequential updates
    db_ufo()
    db_uoh()
    db_uts()
    um_res = db_um()
    
    return jsonify({
        "status": "Full database refresh complete",
        "menus": um_res.get("status")
    })

'''
Updates FoodOutlets in DB
'''
@db_blueprint.route('/db/update/food_outlets')
def db_ufor():
    if not os.path.exists(DB_PATH):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        return jsonify(db_ufo())

def db_ufo():
    engine = create_engine(DB_URL)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    food_outlets = metadata_obj.tables["food_outlets"]

    # Inputing sub food outlets into the DB
    sub_hours_dict = sub_hours.get_sub_hours()
    with engine.connect() as conn:
        for day in sub_hours_dict:
            for name in sub_hours_dict[day]:
                norm_name = normalize_name(name)
                existing_entry = conn.execute(
                    food_outlets.select().where(food_outlets.c.name == norm_name)
                ).fetchone()
                if not existing_entry:
                    db_insert = food_outlets.insert().values(name=norm_name, location=sub_hours_dict[day][name]['Building'])
                    conn.execute(db_insert)
        conn.commit()
    
    # Mapping for UVic food outlets to buildings
    building_mapping = {
        "cove": "Cove",
        "mystic market": "Jamie Cassels Centre",
        "mac's": "MacLaurin",
        "mac's bistro": "MacLaurin",
        "bibliocafe": "McPherson Library",
        "biblio cafe": "McPherson Library",
        "arts place": "Fine Art's Building",
        "arts cafe": "Fine Art's Building",
        "nibbles & bytes": "Engineering Lab Wing",
        "sci cafe": "Bob Wright Center",
        # Cove kiosks
        "verde": "Cove",
        "mykonos": "Cove",
        "vikes grill": "Cove",
        "bento": "Cove",
        "sandwich lab": "Cove",
        "nonna's pasta": "Cove",
        "nonna's pizza": "Cove",
        "feast": "Cove",
        "port cafe": "Cove",
        "cove market express": "Cove",
        "breakfast parfait bar": "Cove",
        "feast brunch": "Cove",
        # Mystic kiosks
        "chop box": "Jamie Cassels Centre",
        "flamin' chicken": "Jamie Cassels Centre",
        "fresco": "Jamie Cassels Centre",
        "pickle & spice": "Jamie Cassels Centre",
        "shoyu": "Jamie Cassels Centre",
        "tofino's": "Jamie Cassels Centre",
        "yolk'd": "Jamie Cassels Centre",
        "general store": "Jamie Cassels Centre",
        "boardwalk": "Jamie Cassels Centre",
        "booster juice": "Jamie Cassels Centre"
    }

    # Inputing UVic food outlets into the DB
    uvic_hours_dict = get_food_outlets_dict()
    with engine.connect() as conn:
        for day_range in uvic_hours_dict:
            for name in uvic_hours_dict[day_range]:
                norm_name = normalize_name(name)
                existing_entry = conn.execute(
                    food_outlets.select().where(food_outlets.c.name == norm_name)
                ).fetchone()
                if not existing_entry:
                    location = building_mapping.get(norm_name, 'Unknown')
                    db_insert = food_outlets.insert().values(name=norm_name, location=location)
                    conn.execute(db_insert)
        conn.commit()

    result = engine.connect().execute(food_outlets.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return row_dict

'''
Updates Opperating Hours in DB
'''
@db_blueprint.route('/db/update/operating_hours')
def db_uohr():
    if not os.path.exists(DB_PATH):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        db_ufo()
        return jsonify(db_uoh())

def db_uoh():
    engine = create_engine(DB_URL)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    sub_hours_dict = sub_hours.get_sub_hours()
    uvic_hours_dict = get_food_outlets_dict()
    food_outlets = metadata_obj.tables["food_outlets"]
    operating_hours = metadata_obj.tables["operating_hours"]

    # Inputing sub operating hours into the DB
    with engine.connect() as conn:
        for day in sub_hours_dict:
            for name in sub_hours_dict[day]:
                food_outlet_id = conn.execute(
                        select(food_outlets.c.id).where(food_outlets.c.name == normalize_name(name))
                    ).scalar()
                
                if not food_outlet_id: continue

                existing_entry = conn.execute(
                    operating_hours.select().where(
                        (operating_hours.c.food_outlet_id == food_outlet_id) &
                        (operating_hours.c.day == day)
                    )).fetchone()
                
                if not existing_entry:
                    db_insert = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                                    day=day,
                                                                    is_closed=sub_hours_dict[day][name]['isClosed'],
                                                                    display_hours=sub_hours_dict[day][name]['displayHours'])
                    conn.execute(db_insert)
        conn.commit()

    # Inputing uvic operating hours into the DB
    with engine.connect() as conn:
        for day_range in uvic_hours_dict:
            for name in uvic_hours_dict[day_range]:
                if day_range == "Monday - Thursday":
                    days_to_insert = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
                elif day_range == "Saturday - Sunday":
                    days_to_insert = ['Saturday', 'Sunday']
                else:
                    days_to_insert = [day_range]

                food_outlet_id = conn.execute(
                        select(food_outlets.c.id).where(food_outlets.c.name == normalize_name(name))
                    ).scalar()
                
                if not food_outlet_id: continue

                for day in days_to_insert:
                    existing_entry = conn.execute(
                        operating_hours.select().where(
                            (operating_hours.c.food_outlet_id == food_outlet_id) &
                            (operating_hours.c.day == day)
                        )).fetchone()
                    
                    if not existing_entry:
                        db_insert = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                                        day=day,
                                                                        is_closed=uvic_hours_dict[day_range][name]['isClosed'],
                                                                        display_hours=uvic_hours_dict[day_range][name]['displayHours'])
                        conn.execute(db_insert)
        conn.commit()

    result = engine.connect().execute(operating_hours.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return row_dict

'''
Updates Time Slots in DB
'''
@db_blueprint.route('/db/update/time_slots')
def db_utsr():
    if not os.path.exists(DB_PATH):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        db_ufo()
        db_uoh()
        return jsonify(db_uts())

def db_uts():
    engine = create_engine(DB_URL)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    sub_hours_dict = sub_hours.get_sub_hours()
    uvic_hours_dict = get_food_outlets_dict()
    food_outlets = metadata_obj.tables["food_outlets"]
    operating_hours = metadata_obj.tables["operating_hours"]
    time_slots = metadata_obj.tables["time_slots"]

    # Inputing sub timeslots into the DB
    with engine.connect() as conn:
        for day in sub_hours_dict:
            for name in sub_hours_dict[day]:
                food_outlet_id = conn.execute(
                    select(food_outlets.c.id).where(food_outlets.c.name == normalize_name(name))
                ).scalar()

                if not food_outlet_id: continue

                operating_hours_id = conn.execute(
                    select(operating_hours.c.id).where(
                        (operating_hours.c.food_outlet_id == food_outlet_id) &
                        (operating_hours.c.day == day)
                    )
                ).scalar()

                if operating_hours_id is None: continue

                raw_hours = sub_hours_dict[day][name]['rawHours']
                if not raw_hours:
                    raw_hours = [{'start': None, 'end': None}]
                
                for slot in raw_hours:
                    existing_entry = conn.execute(
                        time_slots.select().where(
                            (time_slots.c.operating_hours_id == operating_hours_id) &
                            (time_slots.c.start_time == slot['start']) &
                            (time_slots.c.end_time == slot['end'])
                        )).fetchone()
                    if not existing_entry:
                        conn.execute(time_slots.insert().values(
                            operating_hours_id=operating_hours_id,
                            start_time=slot['start'],
                            end_time=slot['end']
                        ))

        # Inputing UVic timeslots into the DB
        for day_range in uvic_hours_dict:
            for name in uvic_hours_dict[day_range]:
                if day_range == "Monday - Thursday":
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
                elif day_range == "Saturday - Sunday":
                    days = ['Saturday', 'Sunday']
                else:
                    days = [day_range]
                
                food_outlet_id = conn.execute(
                    select(food_outlets.c.id).where(food_outlets.c.name == normalize_name(name))
                ).scalar()
                
                if not food_outlet_id: continue

                for day in days:
                    operating_hours_id = conn.execute(
                        select(operating_hours.c.id).where(
                            (operating_hours.c.food_outlet_id == food_outlet_id) &
                            (operating_hours.c.day == day)
                        )
                    ).scalar()
                    
                    if operating_hours_id is None: continue

                    raw_hours = uvic_hours_dict[day_range][name]['rawHours']
                    if not raw_hours:
                        raw_hours = [{'start': None, 'end': None}]
                    
                    for slot in raw_hours:
                        start_time = slot['start']
                        end_time = slot['end']
                        
                        if hasattr(start_time, 'strftime'):
                            start_time = start_time.strftime('%I:%M %p')
                        if hasattr(end_time, 'strftime'):
                            end_time = end_time.strftime('%I:%M %p')

                        existing_entry = conn.execute(
                            time_slots.select().where(
                                (time_slots.c.operating_hours_id == operating_hours_id) &
                                (time_slots.c.start_time == start_time) &
                                (time_slots.c.end_time == end_time)
                            )).fetchone()
                        if not existing_entry:
                            conn.execute(time_slots.insert().values(
                                operating_hours_id=operating_hours_id,
                                start_time=start_time,
                                end_time=end_time
                            ))
        conn.commit()

    result = engine.connect().execute(time_slots.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return row_dict

'''
Updates Menus in DB
'''
@db_blueprint.route('/db/update/menus')
def db_umr():
    if not os.path.exists(DB_PATH):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        db_ufo()
        return jsonify(db_um())

def db_um():
    engine = create_engine(DB_URL)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    food_outlets = metadata_obj.tables["food_outlets"]
    menus = metadata_obj.tables["menus"]
    menu_categories = metadata_obj.tables["menu_categories"]
    menu_items = metadata_obj.tables["menu_items"]
    dietary_restrictions = metadata_obj.tables["dietary_restrictions"]
    menu_item_restrictions = metadata_obj.tables["menu_item_restrictions"]

    with engine.connect() as conn:
        for outlet_norm_name, mapping in MENU_MAPPING.items():
            parent_id = conn.execute(
                select(food_outlets.c.id).where(food_outlets.c.name == normalize_name(outlet_norm_name))
            ).scalar()

            if not parent_id: continue

            if mapping["type"] == "cove_mystic":
                for sub_name, tab_id in mapping["sub_locations"].items():
                    # Attempt to find sub-outlet ID for direct association
                    sub_outlet_id = conn.execute(
                        select(food_outlets.c.id).where(food_outlets.c.name == normalize_name(sub_name))
                    ).scalar()
                    
                    # If not found, try common name variations
                    if not sub_outlet_id:
                        variations = [sub_name.lower() + " pasta", sub_name.lower() + " pizza"]
                        for var in variations:
                            sub_outlet_id = conn.execute(
                                select(food_outlets.c.id).where(food_outlets.c.name == normalize_name(var))
                            ).scalar()
                            if sub_outlet_id: break

                    # Target the sub-outlet if it exists, otherwise the parent
                    target_id = sub_outlet_id if sub_outlet_id else parent_id
                    
                    menu_id = conn.execute(
                        select(menus.c.id).where(
                            (menus.c.food_outlet_id == target_id) & (menus.c.name == sub_name)
                        )
                    ).scalar()
                    if not menu_id:
                        conn.execute(menus.insert().values(food_outlet_id=target_id, name=sub_name))
                        menu_id = conn.execute(select(menus.c.id).where((menus.c.food_outlet_id == target_id) & (menus.c.name == sub_name))).scalar()

                    try:
                        scraped_data = mystic_cove_menu_dict(mapping["url"], tab_id)
                        
                        first_value = next(iter(scraped_data.values()), None)
                        is_flat_items = isinstance(first_value, dict) and (
                            "dietary restrictions" in first_value
                        )

                        if is_flat_items:
                            cat_id = get_or_create_category(conn, menu_categories, menu_id, "Main")
                            for item_name, details in scraped_data.items():
                                process_menu_item(conn, menu_items, dietary_restrictions, menu_item_restrictions, cat_id, item_name, details)
                        else:
                            for cat_name, items in scraped_data.items():
                                cat_id = get_or_create_category(conn, menu_categories, menu_id, cat_name)
                                for item_name, details in items.items():
                                    process_menu_item(conn, menu_items, dietary_restrictions, menu_item_restrictions, cat_id, item_name, details)
                    except Exception as e:
                        print(f"Error scraping menu for {sub_name}: {e}")

            elif mapping["type"] == "other":
                menu_id = conn.execute(
                    select(menus.c.id).where(
                        (menus.c.food_outlet_id == parent_id) & (menus.c.name == "Main Menu")
                    )
                ).scalar()
                if not menu_id:
                    conn.execute(menus.insert().values(food_outlet_id=parent_id, name="Main Menu"))
                    menu_id = conn.execute(select(menus.c.id).where((menus.c.food_outlet_id == parent_id) & (menus.c.name == "Main Menu"))).scalar()

                try:
                    scraped_items = others_menus_dict(mapping["url"])
                    cat_id = get_or_create_category(conn, menu_categories, menu_id, "General")
                    for item_name in scraped_items:
                        details = {"dietary restrictions": [], "ingredients": "", "allergens": ""}
                        process_menu_item(conn, menu_items, dietary_restrictions, menu_item_restrictions, cat_id, item_name, details)
                except Exception as e:
                    print(f"Error scraping menu for {outlet_norm_name}: {e}")
        conn.commit()
    return {"status": "Menu update complete"}

def get_or_create_category(conn, table, menu_id, name):
    cat_id = conn.execute(select(table.c.id).where((table.c.menu_id == menu_id) & (table.c.name == name))).scalar()
    if not cat_id:
        conn.execute(table.insert().values(menu_id=menu_id, name=name))
        cat_id = conn.execute(select(table.c.id).where((table.c.menu_id == menu_id) & (table.c.name == name))).scalar()
    return cat_id

def process_menu_item(conn, menu_items_table, restrictions_table, junction_table, cat_id, item_name, details):
    item_id = conn.execute(
        select(menu_items_table.c.id).where(
            (menu_items_table.c.category_id == cat_id) & (menu_items_table.c.name == item_name)
        )
    ).scalar()

    if not item_id:
        conn.execute(menu_items_table.insert().values(
            category_id=cat_id,
            name=item_name,
            ingredients=details.get("ingredients", ""),
            allergens=details.get("allergens", "")
        ))
        item_id = conn.execute(
            select(menu_items_table.c.id).where(
                (menu_items_table.c.category_id == cat_id) & (menu_items_table.c.name == item_name)
            )
        ).scalar()
    
    # Handle restrictions (icons + parsed allergens)
    restrictions = list(details.get("dietary restrictions", []))
    allergens_str = details.get("allergens", "")
    if allergens_str:
        extra = [a.strip() for a in allergens_str.split(",") if a.strip()]
        for r in extra:
            if r not in restrictions:
                restrictions.append(r)

    for rest_name in restrictions:
        rest_id = conn.execute(
            select(restrictions_table.c.id).where(restrictions_table.c.name == rest_name)
        ).scalar()
        if not rest_id:
            conn.execute(restrictions_table.insert().values(name=rest_name))
            rest_id = conn.execute(select(restrictions_table.c.id).where(restrictions_table.c.name == rest_name)).scalar()
        
        existing_link = conn.execute(
            select(junction_table).where(
                (junction_table.c.menu_item_id == item_id) & (junction_table.c.restriction_id == rest_id)
            )
        ).fetchone()
        if not existing_link:
            conn.execute(junction_table.insert().values(menu_item_id=item_id, restriction_id=rest_id))

# Displays FoodOutlets Currently saved in DB
@db_blueprint.route('/db/food_outlets')
def db_fo():
    if not os.path.exists(DB_PATH):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        engine = create_engine(DB_URL)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    food_outlets = metadata_obj.tables["food_outlets"]

    result = engine.connect().execute(food_outlets.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return jsonify(row_dict)

# Displays operating hours Currently saved in DB
@db_blueprint.route('/db/operating_hours')
def db_oh():
    if not os.path.exists(DB_PATH):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        engine = create_engine(DB_URL)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    operating_hours = metadata_obj.tables["operating_hours"]

    result = engine.connect().execute(operating_hours.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return jsonify(row_dict)

# Displays time slots Currently saved in DB
@db_blueprint.route('/db/time_slots')
def db_ts():
    if not os.path.exists(DB_PATH):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        engine = create_engine(DB_URL)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    time_slots = metadata_obj.tables["time_slots"]

    result = engine.connect().execute(time_slots.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return jsonify(row_dict)
