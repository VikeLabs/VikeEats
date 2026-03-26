from flask import Blueprint, jsonify
from sqlalchemy import create_engine, MetaData, select, text
from datetime import datetime
import calendar

# Database configuration
DB_PATH = 'vikeeats.db'
DB_URL = f"sqlite:///{DB_PATH}"

ui_blueprint = Blueprint('ui', __name__)

# Building coordinates mapping
BUILDING_METADATA = {
    "Cove": {
        "coords": [-123.30727, 48.46423],
        "image": "https://www.uvic.ca/services/food/assets/images/cove-stairs"
    },
    "Farquhar Auditorium": {
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
        "image": "https://uvss.ca/wp-content/uploads/2021/08/Bean-There-1.jpg"
    }
}

# Specific store overrides
STORE_METADATA = {
    "the cove": {
        "categories": ["all", "filter1", "filter2", "filter3", "filter4", "filter5"]
    },
    "biblio cafe": {
        "categories": ["all", "filter1"]
    },
    "mac's bistro": {
        "categories": ["all", "filter2"]
    },
    "mystic market": {
        "categories": ["all", "filter3"]
    },
    "nibbles & bytes cafe": {
        "categories": ["all", "filter4"]
    },
    "sci cafe": {
        "categories": ["all", "filter5"]
    },
    "arts cafe": {
        "categories": ["all", "filter1", "filter3", "filter5"]
    },
    "felicita's campus pub": {
        "image": "https://uvss.ca/wp-content/uploads/2021/08/Felicita-1.jpg"
    }
}

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
            
            # Fetch menu sample
            menu_stmt = text(f"""
                SELECT mi.name, mi.ingredients
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.id
                JOIN menus m ON mc.menu_id = m.id
                WHERE m.food_outlet_id = {o_id}
                LIMIT 5
            """)
            menu_items = [{"name": r[0], "description": r[1]} for r in conn.execute(menu_stmt).fetchall()]

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
                "menu": menu_items
            })

    return jsonify(stores)
