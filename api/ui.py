from flask import Blueprint, jsonify
from sqlalchemy import select
from datetime import datetime
from collections import Counter, OrderedDict, defaultdict
import calendar

from .config import get_engine
from .create_db import (
    buildings,
    daily_hours,
    dietary_restrictions,
    food_outlets,
    menu_item_restrictions,
    menu_items,
)

ui_blueprint = Blueprint('ui', __name__)

# Dietary flags the UI renders as badges. Everything else in
# dietary_restrictions is parsed allergen text ("wheat", "milk", ...), which
# process_menu_item() also files there -- several hundred rows of it.
KNOWN_DIETS = {"vegan", "vegetarian", "gluten free", "dairy free", "halal"}

# Order the cards appear in; anything unlisted sorts to the end.
BUILDING_ORDER = {
    "The Cove": 0,
    "Mystic Market": 1,
    "The SUB": 2,
    "Biblio Cafe": 3,
}

DEFAULT_COORDS = [-123.31219, 48.46319]  # UVic centre
DEFAULT_IMAGE = "https://www.uvic.ca/services/food/assets/images/photos/main/sandwichmain.jpg"


def build_menu_sections_from_rows(rows, item_diets=None):
    """
    Rows: (outlet_name, category_name, item_name, ingredients, allergens, item_id)
    Returns { "sections": [ { "title", "categories": [ { "name", "items" } ] } ] }
    """
    if item_diets is None:
        item_diets = {}
    tree = OrderedDict()
    for r in rows:
        outlet_name, category_name, item_name = r[0], r[1], r[2]
        ingredients, allergens = (r[3] or "").strip(), (r[4] or "").strip()
        item_id = r[5] if len(r) > 5 else None
        if outlet_name not in tree:
            tree[outlet_name] = OrderedDict()
        if category_name not in tree[outlet_name]:
            tree[outlet_name][category_name] = []
        entry = {"name": item_name}
        if ingredients:
            entry["description"] = ingredients
        if allergens:
            entry["allergens"] = allergens
        if item_id and item_id in item_diets:
            entry["dietaryRestrictions"] = item_diets[item_id]
        tree[outlet_name][category_name].append(entry)

    sections = []
    for outlet_name, categories in tree.items():
        sections.append(
            {
                "title": outlet_name,
                "categories": [
                    {"name": cat_name, "items": items}
                    for cat_name, items in categories.items()
                ],
            }
        )
    return {"sections": sections}


def load_item_diets(conn, item_ids):
    """Map each menu item id to its dietary flags: {item_id: ["vegan", ...]}.

    One query for every item rather than one per item: selecting menu_item_id
    alongside the name is what lets the rows be grouped here instead of asking
    the database which item each belongs to. A full menu is ~716 items, and
    against a hosted Postgres each of those queries would be a network round
    trip. Items with no recognised diet get no key, so they stay out of the
    payload entirely.
    """

    diets = {}
    rows = conn.execute(
                select(menu_item_restrictions.c.menu_item_id, dietary_restrictions.c.name)
                .select_from(menu_item_restrictions.join(dietary_restrictions))
                .where(menu_item_restrictions.c.menu_item_id.in_(item_ids))
            ).fetchall()

    for item_id, name in rows:
        if name and name.lower() in KNOWN_DIETS:
            diets.setdefault(item_id, []).append(name)

    return diets


def summarize_hours(outlet_hours):
    """Collapse a building's per-outlet hours into the one line the card shows.

    A building has no hours of its own -- only its outlets do. It counts as
    open when any outlet is, and the label is the most common one among those,
    which surfaces the venue-wide span (most Cove kiosks inherit "7:30am-10pm").
    """
    open_labels = [
        display for display, is_closed in outlet_hours if not is_closed and display
    ]
    if not open_labels:
        return "Closed", True
    return Counter(open_labels).most_common(1)[0][0], False


def load_stores(today):
    """One entry per building, with a menu section per outlet inside it."""
    engine = get_engine()

    with engine.connect() as conn:
        building_rows = conn.execute(
            select(
                buildings.c.id,
                buildings.c.name,
                buildings.c.location,
                buildings.c.lat,
                buildings.c.lng,
                buildings.c.image,
            ).order_by(buildings.c.id)
        ).fetchall()

        outlet_rows = conn.execute(
            select(food_outlets.c.id, food_outlets.c.building_id)
            .order_by(food_outlets.c.building_id, food_outlets.c.id)
        ).fetchall()

        hours_rows = conn.execute(
            select(
                daily_hours.c.food_outlet_id,
                daily_hours.c.display_hours,
                daily_hours.c.is_closed,
            ).where(daily_hours.c.day == today)
        ).fetchall()

        item_rows = conn.execute(
            select(
                food_outlets.c.building_id,
                food_outlets.c.name,
                menu_items.c.category,
                menu_items.c.name,
                menu_items.c.ingredients,
                menu_items.c.allergens,
                menu_items.c.id,
            )
            .select_from(menu_items.join(food_outlets))
            .order_by(food_outlets.c.building_id, food_outlets.c.id, menu_items.c.id)
        ).fetchall()

        item_diets = load_item_diets(conn, [row[6] for row in item_rows])

    outlets_by_building = defaultdict(list)
    for outlet_id, building_id in outlet_rows:
        outlets_by_building[building_id].append(outlet_id)

    hours_by_outlet = {
        outlet_id: (display, bool(is_closed))
        for outlet_id, display, is_closed in hours_rows
    }

    rows_by_building = defaultdict(list)
    for building_id, outlet_name, category, name, ingredients, allergens, item_id in item_rows:
        rows_by_building[building_id].append(
            (outlet_name, category, name, ingredients, allergens, item_id)
        )

    stores = []
    for b_id, b_name, b_location, b_lat, b_lng, b_image in building_rows:
        outlet_hours = [
            hours_by_outlet.get(outlet_id, ("Closed", True))
            for outlet_id in outlets_by_building.get(b_id, [])
        ]
        display_hours, is_closed = summarize_hours(outlet_hours)

        menu_rows = rows_by_building.get(b_id, [])
        diets = sorted({
            diet for row in menu_rows for diet in item_diets.get(row[5], [])
        })

        has_coords = b_lng is not None and b_lat is not None
        stores.append({
            "id": b_id,
            "name": b_name,
            "location": b_location or "",
            "coords": [b_lng, b_lat] if has_coords else DEFAULT_COORDS,
            "image": b_image or DEFAULT_IMAGE,
            "categories": ["all"],
            "supportedDiets": diets,
            "time": display_hours,
            "isClosed": is_closed,
            "menu": build_menu_sections_from_rows(menu_rows, item_diets),
        })

    stores.sort(key=lambda s: BUILDING_ORDER.get(s["name"], 99))
    return stores


@ui_blueprint.route('/ui/stores')
def get_ui_stores():
    today = calendar.day_name[datetime.now().weekday()]
    return jsonify(load_stores(today))
