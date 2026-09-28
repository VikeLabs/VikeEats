from flask import Blueprint, jsonify, request
from sqlalchemy import select, and_
from collections import defaultdict

from .config import get_engine
from .create_db import (
    buildings,
    dietary_restrictions,
    food_outlets,
    menu_item_restrictions,
    menu_items,
)

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
    engine = get_engine()

    stmt = select(
        buildings.c.name.label("building_name"),
        food_outlets.c.name.label("outlet_name"),
        menu_items.c.category,
        menu_items.c.name.label("item_name"),
        menu_items.c.ingredients,
        menu_items.c.allergens,
        menu_items.c.id.label("item_id"),
    ).select_from(
        menu_items.join(food_outlets).join(buildings)
    ).order_by(buildings.c.id, food_outlets.c.id, menu_items.c.id)

    # ilike throughout: SQLite's LIKE ignores case but Postgres' does not, so
    # plain LIKE would quietly stop matching once the data moves to Neon.
    filters = []
    if outlet_name_query:
        # The UI's dropdown is populated from store.name, which is a building.
        filters.append(
            buildings.c.name.ilike(f'%{outlet_name_query}%')
            | food_outlets.c.name.ilike(f'%{outlet_name_query}%')
        )

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

    with engine.connect() as conn:
        rows = conn.execute(stmt).fetchall()
        if not rows:
            return {}

        # One query for the matched items' restrictions rather than one each.
        item_ids = [row.item_id for row in rows]
        restriction_rows = conn.execute(
            select(menu_item_restrictions.c.menu_item_id, dietary_restrictions.c.name)
            .select_from(menu_item_restrictions.join(dietary_restrictions))
            .where(menu_item_restrictions.c.menu_item_id.in_(item_ids))
        ).fetchall()

    item_restrictions = defaultdict(list)
    for item_id, name in restriction_rows:
        item_restrictions[item_id].append(name)

    # { building: { outlet: { category: { item: details } } } } -- the same
    # nesting depth the old shape had, so SearchBar.js needs no changes.
    results = {}
    for row in rows:
        outlets = results.setdefault(row.building_name, {})
        categories = outlets.setdefault(row.outlet_name, {})
        items = categories.setdefault(row.category, {})
        items[row.item_name] = {
            "dietary restrictions": item_restrictions.get(row.item_id, []),
            "ingredients": row.ingredients,
            "allergens": row.allergens,
        }

    return results
