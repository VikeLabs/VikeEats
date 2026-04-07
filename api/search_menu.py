
from flask import Blueprint, jsonify, request
from sqlalchemy import create_engine, MetaData, select, and_

# Database configuration
DB_PATH = 'vikeeats.db'
DB_URL = f"sqlite:///{DB_PATH}"

# Create a blueprint for search
search_blueprint = Blueprint('search', __name__)

@search_blueprint.route('/search')
def search_menu():
    """ 
    Searches the local database for menu items based on restrictions, outlets, and names.
    """
    restriction = request.args.get('restriction')
    if restriction:
        restriction = restriction.replace('-', ' ').lower()

    food_outlet_param = request.args.get('food-outlet')
    if food_outlet_param:
        food_outlet_param = food_outlet_param.lower()

    menu_item_query = request.args.get('menu-item')
    if menu_item_query:
        menu_item_query = menu_item_query.lower().replace('-', ' ')

    return jsonify(db_search(restriction, food_outlet_param, menu_item_query))

def db_search(restriction_name, outlet_name_query, item_name_query):
    engine = create_engine(DB_URL)
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Tables
    food_outlets = metadata.tables["food_outlets"]
    menus = metadata.tables["menus"]
    menu_categories = metadata.tables["menu_categories"]
    menu_items = metadata.tables["menu_items"]
    dietary_restrictions = metadata.tables["dietary_restrictions"]
    menu_item_restrictions = metadata.tables["menu_item_restrictions"]

    # Base query
    stmt = select(
        food_outlets.c.name.label("outlet_name"),
        menus.c.name.label("menu_name"),
        menu_categories.c.name.label("category_name"),
        menu_items.c.name.label("item_name"),
        menu_items.c.ingredients,
        menu_items.c.allergens,
        menu_items.c.id.label("item_id")
    ).select_from(
        food_outlets.join(menus).join(menu_categories).join(menu_items)
    )

    # Filtering
    filters = []
    if outlet_name_query:
        # Check if query is 'cove' or 'mystic' to match parent outlets
        if 'cove' in outlet_name_query:
            filters.append(food_outlets.c.name.like('%cove%'))
        elif 'mystic' in outlet_name_query:
            filters.append(food_outlets.c.name.like('%mystic%'))
        else:
            filters.append(food_outlets.c.name.like(f'%{outlet_name_query}%'))

    if item_name_query:
        filters.append(menu_items.c.name.ilike(f'%{item_name_query}%'))

    if restriction_name:
        # Subquery for items meeting the restriction
        restriction_stmt = select(menu_item_restrictions.c.menu_item_id).select_from(
            menu_item_restrictions.join(dietary_restrictions)
        ).where(dietary_restrictions.c.name.ilike(restriction_name))
        filters.append(menu_items.c.id.in_(restriction_stmt))

    if filters:
        stmt = stmt.where(and_(*filters))

    results = {}
    with engine.connect() as conn:
        rows = conn.execute(stmt).fetchall()

        # We need restrictions for each item to populate the result
        for row in rows:
            # Fetch restrictions for this item
            rest_stmt = select(dietary_restrictions.c.name).select_from(
                dietary_restrictions.join(menu_item_restrictions)
            ).where(menu_item_restrictions.c.menu_item_id == row.item_id)
            item_restrictions = [r[0] for r in conn.execute(rest_stmt).fetchall()]

            # Organize into nested structure
            # { outlet: { menu: { category: { item: { details } } } } }

            # Map database names back to "The Cove" / "Mystic Market" if applicable
            top_level = row.outlet_name.title()
            if 'cove' in row.outlet_name: top_level = "The Cove"
            elif 'mystic' in row.outlet_name: top_level = "Mystic Market"

            if top_level not in results: results[top_level] = {}

            # Use menu name as location (e.g. Greens, Chop Box)
            location = row.menu_name
            if location not in results[top_level]: results[top_level][location] = {}

            category = row.category_name
            # If category is "Main" or "General", we might want to skip one level of nesting
            # but for consistency with original search, we'll keep it if it's not a special location

            item_details = {
                "dietary restrictions": item_restrictions,
                "ingredients": row.ingredients,
                "allergens": row.allergens
            }

            if location in ['Asian Fusion', 'Bread', 'Halal', 'General']:
                results[top_level][location][row.item_name] = item_details
            else:
                if category not in results[top_level][location]:
                    results[top_level][location][category] = {}
                results[top_level][location][category][row.item_name] = item_details

    return results