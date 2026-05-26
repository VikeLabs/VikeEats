from flask import Blueprint, jsonify
from sqlalchemy import create_engine, MetaData, select, text
from datetime import datetime
import calendar
from collections import OrderedDict

# Database configuration
DB_PATH = 'vikeeats.db'
DB_URL = f"sqlite:///{DB_PATH}"

ui_blueprint = Blueprint('ui', __name__)


def build_menu_sections_from_rows(rows, item_diets=None):
    """
    Rows: (menu_name, category_name, item_name, ingredients, allergens, item_id)
    Returns { "sections": [ { "title", "categories": [ { "name", "items" } ] } ] }
    """
    if item_diets is None:
        item_diets = {}
    tree = OrderedDict()
    for r in rows:
        menu_name, category_name, item_name = r[0], r[1], r[2]
        ingredients, allergens = (r[3] or "").strip(), (r[4] or "").strip()
        item_id = r[5] if len(r) > 5 else None
        if menu_name not in tree:
            tree[menu_name] = OrderedDict()
        if category_name not in tree[menu_name]:
            tree[menu_name][category_name] = []
        entry = {"name": item_name}
        if ingredients:
            entry["description"] = ingredients
        if allergens:
            entry["allergens"] = allergens
        if item_id and item_id in item_diets:
            entry["dietaryRestrictions"] = item_diets[item_id]
        tree[menu_name][category_name].append(entry)

    sections = []
    for menu_name, categories in tree.items():
        sections.append(
            {
                "title": menu_name,
                "categories": [
                    {"name": cat_name, "items": items}
                    for cat_name, items in categories.items()
                ],
            }
        )
    return {"sections": sections}


# Building coordinates mapping
BUILDING_METADATA = {
    "Cove": {
        "coords": [-123.30727, 48.46423],
        "image": "https://www.uvic.ca/services/food/assets/images/cove-stairs"
    },
    "Jamie Cassels Centre": {
        "coords": [-123.31174, 48.46483],
        "image": "https://www.uvic.ca/services/food/where/noodlesweb.jpg"
    },
    "McPherson Library": {
        "coords": [-123.30987, 48.46351],
        "image": "https://www.uvic.ca/services/food/where/bibliocafe/cappweb.jpg"
    },
    "MacLaurin": {
        "coords": [-123.31338, 48.46275],
        "image": "https://www.uvic.ca/services/food/assets/images/photos/main/sandwichmain.jpg"
    },
    "Engineering Lab Wing": {
        "coords": [-123.31051, 48.46117],
        "image": "https://www.uvic.ca/news-management/stories/2018/funding-computer-science-engineering/photos/Engineering%20students%20in%20ECS-960x640.jpg"
    },
    "Bob Wright Center": {
        "coords": [-123.30892, 48.46203],
        "image": "https://www.uvic.ca/info/_assets/images/content-main/buildings-bwc.jpg"
    },
    "Fine Art's Building": {
        "coords": [-123.31668, 48.46196],
        "image": "https://www.uvic.ca/services/food/assets/images/photos/artsplace.jpg"
    },
    "The Sub": {
        "coords": [-123.31327, 48.46485],
        "image": "https://uvss.ca/wp-content/uploads/2021/06/SUB_LOGO_WHITE-300x300.png"
    }
}

# Specific store overrides
# STORE_METADATA = {
#     "the cove": {
#         "categories": ["all", "filter1", "filter2", "filter3", "filter4", "filter5"]
#     },
#     "biblio cafe": {
#         "categories": ["all", "filter1"]
#     },
#     "mac's bistro": {
#         "categories": ["all", "filter2"]
#     },
#     "mystic market": {
#         "categories": ["all", "filter3"]
#     },
#     "nibbles & bytes cafe": {
#         "categories": ["all", "filter4"]
#     },
#     "sci cafe": {
#         "categories": ["all", "filter5"]
#     },
#     "arts cafe": {
#         "categories": ["all", "filter1", "filter3", "filter5"]
#     },
#     "felicita's campus pub": {
#         "image": "https://uvss.ca/wp-content/uploads/2021/06/SUBBrands_FEL600px.png"
#     },
#     "bean there cafe": {
#         "image": "https://uvss.ca/wp-content/uploads/2021/06/SUBBrands_BT600px.png"
#     },
#     "the grill": {
#         "image": "https://uvss.ca/wp-content/uploads/2021/06/SUBBrands_GRILL600px.png"
#     },
#     "munchie bar": {
#         "image": "https://uvss.ca/wp-content/uploads/2021/06/SUBBrands_MUN600px.png"
#     },
#     "health food bar (hfb)": {
#         "image": "https://uvss.ca/wp-content/uploads/2021/06/SUBBrands_HFB600px.png"
#     }
# }

@ui_blueprint.route('/ui/stores')
def get_ui_stores():
    engine = create_engine(DB_URL)
    metadata = MetaData()
    metadata.reflect(bind=engine)

    food_outlets = metadata.tables["food_outlets"]
    operating_hours = metadata.tables["operating_hours"]
    
    today = calendar.day_name[datetime.now().weekday()]
    stores = []
    
    with engine.connect() as conn:
        outlets_rows = conn.execute(select(food_outlets)).fetchall()

        for outlet in outlets_rows:
            o_id, o_name, o_loc = outlet


            # Determine defaults based on building
            build_meta = BUILDING_METADATA.get(o_loc, {
                "coords": [-123.31219, 48.46319], # UVic center default
                "image": "https://www.uvic.ca/services/food/assets/images/photos/main/sandwichmain.jpg"
            })
            
            # Specific overrides
            # I just put STORE_METADATA = {} here in the loop for now temparorily since STORE_METADATA is not defined
            STORE_METADATA = {}
            store_meta = STORE_METADATA.get(o_name.lower(), {})
            
            # Merge logic
            coords = store_meta.get("coords", build_meta["coords"])
            image = store_meta.get("image", build_meta["image"])
            categories = store_meta.get("categories", ["all"])
            
            # Fetch today's hours
            hours_stmt = select(operating_hours.c.display_hours, operating_hours.c.is_closed).where(
                (operating_hours.c.food_outlet_id == o_id) & (operating_hours.c.day == today)
            )
            hours_row = conn.execute(hours_stmt).fetchone()
            
            display_hours = hours_row[0] if hours_row else "Closed"
            is_closed = hours_row[1] if hours_row else True
            
            # Fetch dietary restrictions
            diet_stmt = text(f"""
                SELECT DISTINCT dr.name 
                FROM dietary_restrictions dr
                JOIN menu_item_restrictions mir ON dr.id = mir.restriction_id
                JOIN menu_items mi ON mir.menu_item_id = mi.id
                JOIN menu_categories mc ON mi.category_id = mc.id
                JOIN menus m ON mc.menu_id = m.id
                WHERE m.food_outlet_id = {o_id}
            """)
            diets = [r[0] for r in conn.execute(diet_stmt).fetchall()]
            
            menu_stmt = text("""
                SELECT m.name AS menu_name, mc.name AS category_name, mi.name AS item_name,
                       mi.ingredients, mi.allergens, mi.id AS item_id
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.id
                JOIN menus m ON mc.menu_id = m.id
                WHERE m.food_outlet_id = :oid
                ORDER BY m.name, mc.name, mi.name
            """)
            menu_rows = conn.execute(menu_stmt, {"oid": o_id}).fetchall()

            known_diets = {"vegan", "vegetarian", "gluten free", "dairy free", "halal"}
            item_diets = {}
            for r in menu_rows:
                item_id = r[5]
                diet_query = text("""
                    SELECT dr.name FROM dietary_restrictions dr
                    JOIN menu_item_restrictions mir ON dr.id = mir.restriction_id
                    WHERE mir.menu_item_id = :iid
                """)
                diets_for_item = [
                    d[0] for d in conn.execute(diet_query, {"iid": item_id}).fetchall()
                    if d[0].lower() in known_diets
                ]
                if diets_for_item:
                    item_diets[item_id] = diets_for_item

            menu_payload = build_menu_sections_from_rows(menu_rows, item_diets)

            stores.append({
                "id": o_id,
                "name": o_name.title(),
                "location": o_loc,
                "coords": coords,
                "image": image,
                "categories": categories,
                "supportedDiets": diets,
                "time": display_hours,
                "isClosed": is_closed,
                "menu": menu_payload,
            })

    LOCATION_ORDER = {
        "Cove": 0,
        "Jamie Cassels Centre": 1,
        "The Sub": 2,
        "McPherson Library": 3,
    }
    stores.sort(key=lambda s: LOCATION_ORDER.get(s["location"], 99))

    return jsonify(stores)
