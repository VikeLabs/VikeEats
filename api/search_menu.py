
from flask import Blueprint, jsonify, request
from api.menu import mystic_cove_menu_dict

# Create a blueprint for search
search_blueprint = Blueprint('search', __name__)

#SEARCH STUFF
@search_blueprint.route('/search')
def search_menu():

    #search by dietary restrictions
    restriction = request.args.get('restriction').replace('-', ' ')

    #search by food outlet
    food_outlet = request.args.get('food-outlet')

    #search by menu item
    menu_item = request.args.get('menu-item').lower().replace('-', ' ')

    return jsonify(search(restriction, food_outlet, menu_item))


#returns all the menu items that are safe for the specified dietary restriction (e.g. vegan), grouped by food outlet
def search(restriction, food_outlet, menu_item):

    selected_menu_items = {}
    mystic_locations = ['Chopbox', 'Fresco Taco', 'Flamin Good Chicken', 'Pickle and Spice']
    cove_locations = ['Greens', 'Deli', 'Shawarma', 'Pizza', 'Grill', 'Entre', 'Halal', 'Bread', 'Asian Fusion']

    #search through mystic if specified, or if none are specified
    if food_outlet == 'mystic' or food_outlet == None:
        mystic_items = search_through_food_outlet(mystic_locations, "https://www.uvic.ca/services/food/where/mysticmarket/index.php", restriction, menu_item)
        if mystic_items != {}:
            selected_menu_items['Mystic Market'] = mystic_items
    #search through cove if specified, or if none are specified
    if food_outlet == 'cove' or food_outlet == None:
        cove_items = search_through_food_outlet(cove_locations, "https://www.uvic.ca/services/food/where/thecove/index.php", restriction, menu_item)
        if cove_items != {}:
            selected_menu_items['The Cove'] = cove_items
    
    return selected_menu_items
    


def search_through_food_outlet(locations, url, restriction, searched_menu_item):
    selected_menu_items = {}
    #loop through all locations
    for location in locations:
        #get menu items for that location
        formatted_location = 'tabs-' + location.lower().replace(' ', '-')
        menu_items = mystic_cove_menu_dict(url, formatted_location)

        #find dietary restrictions for asian fusion, bread, and halal - (no categories)
        if location == 'Asian Fusion' or location == 'Bread' or location == 'Halal':
            for key, value in menu_items.items():
                #filter by menu item(s) if specified
                if (searched_menu_item is not None and searched_menu_item in key.lower()) or searched_menu_item is None:

                    restrictions = value.get('dietary restrictions')
                    if restrictions is not None and restriction in restrictions:
                        if location not in selected_menu_items:
                            selected_menu_items[location] = {}
                        selected_menu_items.get(location).update({key: value})
        else :
            #loop through all categories
            for category, menu_item in menu_items.items():
                for key, value in menu_item.items():
                    #filter by menu item(s) if specified
                    if (searched_menu_item is not None and searched_menu_item in key.lower()) or searched_menu_item is None:
                        restrictions = value.get('dietary restrictions')
                        if restrictions is not None and restriction in restrictions:
                            if location not in selected_menu_items:
                                selected_menu_items[location] = {}
                            if category not in selected_menu_items.get(location):  
                                selected_menu_items.get(location).update({category: {key: value}})
                            else:
                                selected_menu_items.get(location).get(category).update({key: value})
    return selected_menu_items