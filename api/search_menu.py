
from flask import Blueprint, jsonify
from api.menu import mystic_cove_menu_dict

# Create a blueprint for menus
search_blueprint = Blueprint('search', __name__)

#SEARCH STUFF
@search_blueprint.route('/search-menu/<restriction>')
def search_menu(restriction):
    return jsonify(search_for_dietary_restrictions(restriction))

#returns all the menu items that do not contain the allergen, grouped by food outlet
def search_for_allergens(allergen):
    return

#returns all the menu items that are safe for the specified dietary restriction (e.g. vegan), grouped by food outlet
def search_for_dietary_restrictions(restriction):
    #lists of all mystic and cove locations
    mystic_locations = ['Chopbox', 'Fresco Taco', 'Flamin Good Chicken', 'Pickle and Spice']
    cove_locations = ['Greens', 'Deli', 'Shawarma', 'Pizza', 'Grill', 'Entre', 'Halal', 'Bread', 'Asian Fusion']
    selected_menu_items = {}
    mystic_items = search_through_food_outlet(mystic_locations, "https://www.uvic.ca/services/food/where/mysticmarket/index.php", restriction)
    if (mystic_items != {}):
        selected_menu_items['Mystic Market'] = mystic_items
    cove_items = search_through_food_outlet(cove_locations, "https://www.uvic.ca/services/food/where/thecove/index.php", restriction)
    if (cove_items != {}):
        selected_menu_items['The Cove'] = cove_items
    return selected_menu_items
    


def search_through_food_outlet(locations, url, restriction):
    selected_menu_items = {}
    #loop through all locations
    for location in locations:
        #get menu items for that location
        formatted_location = 'tabs-' + location.lower().replace(' ', '-')
        menu_items = mystic_cove_menu_dict(url, formatted_location)

        #find dietary restrictions for asian fusion, bread, and halal - (no categories)
        if (location == 'Asian Fusion' or location == 'Bread' or location == 'Halal'):
            for key, value in menu_items.items():
                restrictions = value.get('dietary restrictions')
                if restrictions is not None and restriction in restrictions:
                    if location not in selected_menu_items:
                        selected_menu_items[location] = {}
                    selected_menu_items.get(location).update({key: value})
        else :
            #loop through all categories
            for category, menu_item in menu_items.items():
                for key, value in menu_item.items():
                    restrictions = value.get('dietary restrictions')
                    if restrictions is not None and restriction in restrictions:
                        if location not in selected_menu_items:
                            selected_menu_items[location] = {}
                        if category not in selected_menu_items.get(location):  
                            selected_menu_items.get(location).update({category: {key: value}})
                        else:
                            selected_menu_items.get(location).get(category).update({key: value})
    return selected_menu_items