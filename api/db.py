from sqlalchemy import select, update, delete
from . import sub
from .sub import SUB_MENUS, scrape_felicitas_menu
from .food_outlets import get_food_outlets_dict
from .menu import mystic_cove_menu_dict, others_menus_dict
from . import create_db
from .create_db import (
    TABLE_CLEAR_ORDER,
    buildings,
    daily_hours,
    dietary_restrictions,
    food_outlets,
    menu_item_restrictions,
    menu_items,
    metadata_obj,
    time_slots,
)
from .config import database_exists, get_engine
from flask import Flask, Blueprint, jsonify
import logging
import re

db_blueprint = Blueprint('db', __name__)
app = Flask(__name__)

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# UVic consolidated every kiosk menu onto the Ingredients & Allergens page; the
# per-outlet pages under /where/ are now description-only and carry no tabs.
UVIC_MENU_URL = "https://www.uvic.ca/services/food/nutrition/ingredientsandallergens/index.php"

# The curated source of truth: which buildings exist, and which outlets live in
# each. The scrapers may only attach hours and menus to what is declared here.
# A name UVic invents that is not declared and not aliased is logged and
# dropped, rather than silently becoming an outlet with its own map pin.
#
# "coords" are [longitude, latitude] to match the frontend's fromLonLat().
# An outlet's value is its menu tab id on UVIC_MENU_URL, or None when the
# outlet has hours but no published menu.
VENUES = {
    "The Cove": {
        "location": "Čeqʷəŋín ʔéʔləŋ (Cheko'nien House), beside The SUB",
        "coords": [-123.30727, 48.46423],
        "image": "https://www.uvic.ca/services/food/assets/images/cove-stairs",
        "type": "cove_mystic",
        "url": UVIC_MENU_URL,
        "outlets": {
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
            "Soups": "tabs-soups",
            "Port Cafe": None,
            "Cove Market Express": None,
        },
    },
    "Mystic Market": {
        "location": "Jamie Cassels Centre",
        "coords": [-123.31174, 48.46483],
        "image": "https://www.uvic.ca/services/food/where/noodlesweb.jpg",
        "type": "cove_mystic",
        "url": UVIC_MENU_URL,
        "outlets": {
            "Chopbox": "tabs-chopbox",
            "Fresco Taco": "tabs-fresco-taco",
            "Flamin' Good Chicken": "tabs-flamin-good-chicken",
            "Pickle and Spice": "tabs-pickle-and-spice",
            "Tofino's": "tabs-tofinos",
            "Yolk'd": "tabs-yolkd",
            "Shoyu": "tabs-shoyu",
            "Baked Goods": "tabs-baked-goods",
            "Soups": "tabs-soups",
            "Boardwalk": None,
            "Booster Juice": None,
            "General Store": None,
        },
    },
    "The SUB": {
        "location": "Student Union Building",
        "coords": [-123.31327, 48.46485],
        "image": "https://uvss.ca/wp-content/uploads/2021/06/SUB_LOGO_WHITE-300x300.png",
        "type": "sub",
        "url": "https://uvss.ca/thesub/",
        "outlets": {
            "Bean There Cafe": None,
            "Felicita’s Campus Pub": None,
            "The Grill": None,
            "Munchie Bar": None,
            "Health Food Bar (HFB)": None,
        },
    },
    "Biblio Cafe": {
        "location": "McPherson Library",
        "coords": [-123.30987, 48.46351],
        "image": "https://www.uvic.ca/services/food/where/bibliocafe/cappweb.jpg",
        "type": "other",
        "url": "https://www.uvic.ca/services/food/where/bibliocafe/index.php",
        "outlets": {"Biblio Cafe": None},
    },
    "Arts Cafe": {
        "location": "Fine Arts Building",
        "coords": [-123.31668, 48.46196],
        "image": "https://www.uvic.ca/services/food/assets/images/photos/artsplace.jpg",
        "type": "other",
        "url": "https://www.uvic.ca/services/food/where/artsplace/index.php",
        "outlets": {"Arts Cafe": None},
    },
    "Sci Cafe": {
        "location": "Bob Wright Centre",
        "coords": [-123.30892, 48.46203],
        "image": "https://www.uvic.ca/info/_assets/images/content-main/buildings-bwc.jpg",
        "type": "other",
        "url": "https://www.uvic.ca/services/food/where/scicafe/index.php",
        "outlets": {"Sci Cafe": None},
    },
    "Mac's": {
        "location": "MacLaurin Building",
        "coords": [-123.31338, 48.46275],
        "image": "https://www.uvic.ca/services/food/assets/images/photos/main/sandwichmain.jpg",
        "type": "other",
        "url": "https://www.uvic.ca/services/food/where/macs/index.php",
        "outlets": {"Mac's": None},
    },
}

# Names the UVic hours page uses that differ from what VENUES declares. Keys
# are normalize_name() output; values are a declared venue or outlet name.
# Feast's dayparts collapse onto one outlet -- the several sittings become
# several time_slots rows, which is what that table is for.
ALIASES = {
    # Venue-level
    "bibliocafe": "Biblio Cafe",
    "arts place": "Arts Cafe",
    "mac's bistro": "Mac's",
    # Cove outlets
    "nonna's pasta": "Nonna's",
    "nonna's pizza": "Nonna's",
    "nonna's pizza and pasta": "Nonna's",
    "feast breakfast": "Feast",
    "feast brunch": "Feast",
    "feast lunch": "Feast",
    "feast dinner": "Feast",
    "feast lunch, dinner": "Feast",
    "soup": "Soups",
    # Mystic outlets
    "chop box": "Chopbox",
    "fresco": "Fresco Taco",
    "fresco taco bar": "Fresco Taco",
    "flamin' chicken": "Flamin' Good Chicken",
    "pickle & spice": "Pickle and Spice",
    "tofino's (pizza & pasta)": "Tofino's",
}


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


def _build_name_index():
    venues, outlets = {}, {}
    for venue_name, venue in VENUES.items():
        venues[normalize_name(venue_name)] = venue_name
        for outlet_name in venue["outlets"]:
            # Baked Goods and Soups exist in both Cove and Mystic; first wins,
            # and the loser simply inherits its venue's hours.
            outlets.setdefault(normalize_name(outlet_name), (venue_name, outlet_name))
    return venues, outlets


_VENUE_INDEX, _OUTLET_INDEX = _build_name_index()


def resolve_scraped_name(scraped):
    """Map a scraped name onto (venue, outlet).

    An outlet of None means the hours describe the venue as a whole and should
    be copied down to every outlet inside it. Returns None for a name we do not
    recognise, so the caller can log and skip it.
    """
    norm = normalize_name(scraped)
    declared = ALIASES.get(norm)
    if declared is not None:
        norm = normalize_name(declared)
    if norm in _VENUE_INDEX:
        return _VENUE_INDEX[norm], None
    if norm in _OUTLET_INDEX:
        return _OUTLET_INDEX[norm]
    return None


def parse_day_header(header):
    """Map a UVic hours heading onto weekdays, plus how specific it is.

    The page mixes generic blocks ("Monday - Thursday", "Saturday-Sunday")
    with dated overrides for the current week ("Wednesday Sept 30"). The dated
    rows carry the hours that are actually in effect, so they have to outrank
    the generic ones -- Verde reads "Closed" all week generically while the
    dated row has it open 11am-2:45pm.

    Returns (days, specificity); specificity 0 means unrecognised.
    """
    text = ' '.join(header.split())
    lowered = text.lower()

    for day in DAYS:
        if lowered.startswith(day.lower()):
            rest = text[len(day):].strip()
            if not rest:
                return [day], 2                                  # generic single day
            if any(ch.isdigit() for ch in rest):
                return [day], 3                                  # dated override
            break                                                # e.g. "Monday - Thursday"

    parts = [p.strip().title() for p in re.split(r'[-–—]', text) if p.strip()]
    if len(parts) == 2 and parts[0] in DAYS and parts[1] in DAYS:
        start, end = DAYS.index(parts[0]), DAYS.index(parts[1])
        if start <= end:
            return DAYS[start:end + 1], 1
    return [], 0


def collect_hours():
    """Scrape once and resolve hours for every declared outlet.

    Returns {(venue, outlet): {day: {isClosed, displayHours, rawHours}}}.
    An outlet's own scraped hours win; otherwise it inherits its venue's; an
    outlet with neither is closed. db_udh() and db_uts() share this so the two
    can never disagree about which outlet is open when.
    """
    venue_hours, outlet_hours = {}, {}
    unknown = set()

    def record(store, key, day, hours, specificity):
        """Keep the most specific hours seen for a day."""
        existing = store.setdefault(key, {}).get(day)
        if existing is None or specificity > existing[1]:
            store[key][day] = (hours, specificity)

    def ingest(scraped_name, hours, days, specificity):
        resolved = resolve_scraped_name(scraped_name)
        if resolved is None:
            unknown.add(scraped_name)
            return
        venue_name, outlet_name = resolved
        for day in days:
            if outlet_name is None:
                record(venue_hours, venue_name, day, hours, specificity)
            else:
                record(outlet_hours, (venue_name, outlet_name), day, hours, specificity)

    for header, entries in get_food_outlets_dict().items():
        days, specificity = parse_day_header(header)
        if not days:
            logging.error("Unrecognized hours heading, skipped: %r", header)
            continue
        for scraped_name, hours in entries.items():
            ingest(scraped_name, hours, days, specificity)

    for day, entries in sub.get_sub_hours().items():
        for scraped_name, hours in entries.items():
            ingest(scraped_name, hours, [day], 2)

    for name in sorted(unknown):
        logging.error("Unrecognized outlet on a hours page, skipped: %r", name)

    closed = {"isClosed": True, "displayHours": "Closed", "rawHours": []}
    resolved_hours = {}
    for venue_name, venue in VENUES.items():
        inherited = venue_hours.get(venue_name, {})
        for outlet_name in venue["outlets"]:
            own = outlet_hours.get((venue_name, outlet_name), {})
            resolved_hours[(venue_name, outlet_name)] = {
                day: (own.get(day) or inherited.get(day) or (closed, 0))[0]
                for day in DAYS
            }
    return resolved_hours


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
def clear_db(conn):
    """Clears all data from the database tables in correct order."""
    for table_name in TABLE_CLEAR_ORDER:
        conn.execute(metadata_obj.tables[table_name].delete())


@db_blueprint.route('/db/update/all')
def db_update_all():
    """Triggers a full refresh of all database tables."""
    if not database_exists():
        create_db.create_database()

    engine = get_engine()
    with engine.begin() as conn:
        clear_db(conn)

    # Sequential updates
    db_ub()
    db_ufo()
    db_udh()
    db_uts()
    um_res = db_um()

    return jsonify({
        "status": "Full database refresh complete",
        "menus": um_res.get("status")
    })


'''
Updates Buildings in DB
'''
@db_blueprint.route('/db/update/buildings')
def db_ubr():
    if not database_exists():
        return jsonify("Database not found, create it at /api/db/create")
    return jsonify(db_ub())


def db_ub():
    engine = get_engine()
    with engine.begin() as conn:
        for venue_name, venue in VENUES.items():
            lng, lat = venue["coords"]
            values = {
                "location": venue.get("location"),
                "lat": lat,
                "lng": lng,
                "image": venue.get("image"),
            }
            building_id = conn.execute(
                select(buildings.c.id).where(buildings.c.name == venue_name)
            ).scalar()
            if building_id is None:
                conn.execute(buildings.insert().values(name=venue_name, **values))
            else:
                conn.execute(
                    update(buildings).where(buildings.c.id == building_id).values(**values)
                )

    with engine.connect() as conn:
        result = conn.execute(buildings.select())
        return {idx + 1: str(row) for idx, row in enumerate(result)}


'''
Updates FoodOutlets in DB
'''
@db_blueprint.route('/db/update/food_outlets')
def db_ufor():
    if not database_exists():
        return jsonify("Database not found, create it at /api/db/create")
    db_ub()
    return jsonify(db_ufo())


def db_ufo():
    engine = get_engine()
    with engine.begin() as conn:
        for venue_name, venue in VENUES.items():
            building_id = conn.execute(
                select(buildings.c.id).where(buildings.c.name == venue_name)
            ).scalar()
            if building_id is None:
                logging.error("Building %r missing; run db_ub() first", venue_name)
                continue

            for outlet_name in venue["outlets"]:
                existing = conn.execute(
                    select(food_outlets.c.id).where(
                        (food_outlets.c.building_id == building_id)
                        & (food_outlets.c.name == outlet_name)
                    )
                ).scalar()
                if existing is None:
                    conn.execute(
                        food_outlets.insert().values(
                            name=outlet_name, building_id=building_id
                        )
                    )

    with engine.connect() as conn:
        result = conn.execute(food_outlets.select())
        return {idx + 1: str(row) for idx, row in enumerate(result)}


def outlet_id_map(conn):
    """{(venue, outlet): food_outlets.id} for every declared outlet present."""
    rows = conn.execute(
        select(food_outlets.c.id, food_outlets.c.name, buildings.c.name)
        .select_from(food_outlets.join(buildings))
    ).fetchall()
    return {(building_name, outlet_name): oid for oid, outlet_name, building_name in rows}


'''
Updates Daily Hours in DB
'''
@db_blueprint.route('/db/update/daily_hours')
def db_udhr():
    if not database_exists():
        return jsonify("Database not found, create it at /api/db/create")
    db_ub()
    db_ufo()
    return jsonify(db_udh())


def db_udh():
    engine = get_engine()
    resolved = collect_hours()

    with engine.begin() as conn:
        outlet_ids = outlet_id_map(conn)
        for (venue_name, outlet_name), by_day in resolved.items():
            outlet_id = outlet_ids.get((venue_name, outlet_name))
            if outlet_id is None:
                continue

            for day, hours in by_day.items():
                existing = conn.execute(
                    select(daily_hours.c.id).where(
                        (daily_hours.c.food_outlet_id == outlet_id)
                        & (daily_hours.c.day == day)
                    )
                ).scalar()
                values = {
                    "is_closed": bool(hours.get("isClosed")),
                    "display_hours": hours.get("displayHours") or "Closed",
                }
                if existing is None:
                    conn.execute(
                        daily_hours.insert().values(
                            food_outlet_id=outlet_id, day=day, **values
                        )
                    )
                else:
                    conn.execute(
                        update(daily_hours).where(daily_hours.c.id == existing).values(**values)
                    )

    with engine.connect() as conn:
        result = conn.execute(daily_hours.select())
        return {idx + 1: str(row) for idx, row in enumerate(result)}


'''
Updates Time Slots in DB
'''
@db_blueprint.route('/db/update/time_slots')
def db_utsr():
    if not database_exists():
        return jsonify("Database not found, create it at /api/db/create")
    db_ub()
    db_ufo()
    db_udh()
    return jsonify(db_uts())


def format_slot_time(value):
    """Scrapers hand back either a string or a datetime; store a string."""
    return value.strftime('%I:%M %p') if hasattr(value, 'strftime') else value


def db_uts():
    engine = get_engine()
    resolved = collect_hours()

    with engine.begin() as conn:
        outlet_ids = outlet_id_map(conn)
        for (venue_name, outlet_name), by_day in resolved.items():
            outlet_id = outlet_ids.get((venue_name, outlet_name))
            if outlet_id is None:
                continue

            for day, hours in by_day.items():
                hours_id = conn.execute(
                    select(daily_hours.c.id).where(
                        (daily_hours.c.food_outlet_id == outlet_id)
                        & (daily_hours.c.day == day)
                    )
                ).scalar()
                if hours_id is None:
                    continue

                for slot in hours.get("rawHours") or []:
                    start = format_slot_time(slot.get("start"))
                    end = format_slot_time(slot.get("end"))
                    existing = conn.execute(
                        select(time_slots.c.id).where(
                            (time_slots.c.daily_hours_id == hours_id)
                            & (time_slots.c.start_time == start)
                            & (time_slots.c.end_time == end)
                        )
                    ).scalar()
                    if existing is None:
                        conn.execute(
                            time_slots.insert().values(
                                daily_hours_id=hours_id, start_time=start, end_time=end
                            )
                        )

    with engine.connect() as conn:
        result = conn.execute(time_slots.select())
        return {idx + 1: str(row) for idx, row in enumerate(result)}


'''
Updates Menus in DB
'''
@db_blueprint.route('/db/update/menus')
def db_umr():
    if not database_exists():
        return jsonify("Database not found, create it at /api/db/create")
    db_ub()
    db_ufo()
    return jsonify(db_um())


def db_um():
    engine = get_engine()

    with engine.begin() as conn:
        outlet_ids = outlet_id_map(conn)

        for venue_name, venue in VENUES.items():
            if venue["type"] == "cove_mystic":
                for outlet_name, tab_id in venue["outlets"].items():
                    outlet_id = outlet_ids.get((venue_name, outlet_name))
                    if outlet_id is None or tab_id is None:
                        continue

                    try:
                        scraped_data = mystic_cove_menu_dict(venue["url"], tab_id)
                        if not scraped_data:
                            # Empty means the tab vanished from the page, not that the
                            # kiosk has no food. Stay loud: this is how UVic moving the
                            # menus went unnoticed until the UI showed empty outlets.
                            logging.error(
                                "No menu data for %s (tab %s) at %s", outlet_name, tab_id, venue["url"]
                            )
                            continue

                        clear_outlet_menu_items(conn, outlet_id)

                        # Flat: every top-level value is one dish. Nested: values are category dicts.
                        if all(is_item_details(v) for v in scraped_data.values()):
                            for item_name, details in scraped_data.items():
                                process_scraped_item(conn, outlet_id, "Main", item_name, details)
                        else:
                            for cat_name, items in scraped_data.items():
                                for item_name, details in iter_leaf_menu_items(items):
                                    process_scraped_item(conn, outlet_id, cat_name, item_name, details)
                    except Exception as e:
                        logging.error("Error scraping menu for %s (tab %s): %s", outlet_name, tab_id, e)

            elif venue["type"] == "sub":
                for outlet_name in venue["outlets"]:
                    outlet_id = outlet_ids.get((venue_name, outlet_name))
                    if outlet_id is None:
                        continue

                    clear_outlet_menu_items(conn, outlet_id)
                    if "felicita" in outlet_name.lower():
                        # Felicita's publishes tabs (Daily Features, Drinks, Burgers...)
                        # which flatten into "Tab - Heading" categories on the one outlet.
                        try:
                            felicitas_data = scrape_felicitas_menu()
                        except Exception as e:
                            logging.error("Error scraping Felicita's menu: %s", e)
                            felicitas_data = {}
                        for tab_name, tab_categories in felicitas_data.items():
                            for cat_name, items in tab_categories.items():
                                category = cat_name if cat_name == tab_name else f"{tab_name} - {cat_name}"
                                for item in items:
                                    process_menu_item(conn, outlet_id, category, item["name"], item)
                    else:
                        sub_menu_data = SUB_MENUS.get(outlet_name, {})
                        for cat_name, items in sub_menu_data.get("categories", {}).items():
                            for item in items:
                                process_menu_item(conn, outlet_id, cat_name, item["name"], item)

            elif venue["type"] == "other":
                for outlet_name in venue["outlets"]:
                    outlet_id = outlet_ids.get((venue_name, outlet_name))
                    if outlet_id is None:
                        continue
                    try:
                        scraped_items = others_menus_dict(venue["url"])
                        clear_outlet_menu_items(conn, outlet_id)
                        for item_name in scraped_items:
                            process_menu_item(conn, outlet_id, "General", item_name, {})
                    except Exception as e:
                        logging.error("Error scraping menu for %s: %s", venue_name, e)

    return {"status": "Menu update complete"}


def is_item_details(details):
    return isinstance(details, dict) and {
        "dietary restrictions",
        "ingredients",
        "allergens",
    }.issubset(details.keys())


def clear_outlet_menu_items(conn, outlet_id):
    """Drop an outlet's items so a rescrape does not leave stale rows behind."""
    item_ids = [
        r[0]
        for r in conn.execute(
            select(menu_items.c.id).where(menu_items.c.outlet_id == outlet_id)
        ).fetchall()
    ]
    if not item_ids:
        return
    conn.execute(
        delete(menu_item_restrictions).where(
            menu_item_restrictions.c.menu_item_id.in_(item_ids)
        )
    )
    conn.execute(delete(menu_items).where(menu_items.c.id.in_(item_ids)))


def iter_leaf_menu_items(menu_dict):
    """
    Yield only lowest-level menu items from nested menu dictionaries.
    Parent headers (grouping nodes) are skipped.
    """
    if not isinstance(menu_dict, dict):
        return

    for key, value in menu_dict.items():
        if is_item_details(value):
            yield key, value
            continue

        if isinstance(value, dict):
            for item_name, details in iter_leaf_menu_items(value):
                yield item_name, details


def process_menu_item(conn, outlet_id, category, item_name, details):
    new_ingredients = details.get("ingredients") or ""
    new_allergens = details.get("allergens") or ""

    item_id = conn.execute(
        select(menu_items.c.id).where(
            (menu_items.c.outlet_id == outlet_id)
            & (menu_items.c.category == category)
            & (menu_items.c.name == item_name)
        )
    ).scalar()

    if not item_id:
        conn.execute(menu_items.insert().values(
            outlet_id=outlet_id,
            category=category,
            name=item_name,
            ingredients=new_ingredients,
            allergens=new_allergens
        ))
        item_id = conn.execute(
            select(menu_items.c.id).where(
                (menu_items.c.outlet_id == outlet_id)
                & (menu_items.c.category == category)
                & (menu_items.c.name == item_name)
            )
        ).scalar()
    else:
        existing_row = conn.execute(
            select(menu_items.c.ingredients, menu_items.c.allergens).where(
                menu_items.c.id == item_id
            )
        ).fetchone()
        if existing_row:
            updates = {}
            old_ingredients = existing_row[0] or ""
            old_allergens = existing_row[1] or ""
            if new_ingredients != old_ingredients:
                updates["ingredients"] = new_ingredients
            if new_allergens != old_allergens:
                updates["allergens"] = new_allergens
            if updates:
                conn.execute(
                    update(menu_items)
                    .where(menu_items.c.id == item_id)
                    .values(**updates)
                )

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
            select(dietary_restrictions.c.id).where(dietary_restrictions.c.name == rest_name)
        ).scalar()
        if not rest_id:
            conn.execute(dietary_restrictions.insert().values(name=rest_name))
            rest_id = conn.execute(
                select(dietary_restrictions.c.id).where(dietary_restrictions.c.name == rest_name)
            ).scalar()

        existing_link = conn.execute(
            select(menu_item_restrictions).where(
                (menu_item_restrictions.c.menu_item_id == item_id)
                & (menu_item_restrictions.c.restriction_id == rest_id)
            )
        ).fetchone()
        if not existing_link:
            conn.execute(menu_item_restrictions.insert().values(
                menu_item_id=item_id, restriction_id=rest_id
            ))


def process_scraped_item(conn, outlet_id, category, item_name, details):
    pdf_products = details.get("pdf products", [])
    if isinstance(pdf_products, list) and pdf_products:
        for product in pdf_products:
            product_name = str(product.get("name", "")).strip()
            if not product_name:
                continue
            product_details = {
                "dietary restrictions": details.get("dietary restrictions", []),
                "ingredients": product.get("ingredients", ""),
                "allergens": product.get("allergens", ""),
            }
            process_menu_item(conn, outlet_id, category, product_name, product_details)
        return

    process_menu_item(conn, outlet_id, category, item_name, details)


def dump_table(table_name):
    """Row dump shared by the read-only /db/<table> display routes."""
    if not database_exists():
        return jsonify("Database not found, create it at /api/db/create")

    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(metadata_obj.tables[table_name].select())
        return jsonify({idx + 1: str(row) for idx, row in enumerate(result)})

# Displays Buildings Currently saved in DB
@db_blueprint.route('/db/buildings')
def db_b():
    return dump_table("buildings")

# Displays FoodOutlets Currently saved in DB
@db_blueprint.route('/db/food_outlets')
def db_fo():
    return dump_table("food_outlets")

# Displays daily hours Currently saved in DB
@db_blueprint.route('/db/daily_hours')
def db_dh():
    return dump_table("daily_hours")

# Displays time slots Currently saved in DB
@db_blueprint.route('/db/time_slots')
def db_ts():
    return dump_table("time_slots")
