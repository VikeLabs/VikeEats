from flask import Blueprint, jsonify, url_for
import requests
from bs4 import BeautifulSoup

# Create a blueprint for menus
menu_blueprint = Blueprint('menu', __name__)

@menu_blueprint.route('/menu')
def menu_home():
    # return url_for('menu.cove_menu'), url_for('menu.mystic_menu')
    return "Welcome to the menu page <br>" + "<br>Cove Menu: " + url_for('menu.cove_menu') + "<br>Mystic Menu: " + url_for('menu.mystic_menu')

@menu_blueprint.route('/menu/cove')
def cove_menu():
    #TODO: Implement this function

    #get webpage and check its 200 ok

    #extract the menu items from the webpage

    #return the menu items as json

    #sample menu items feel free to delete
    menu_items = [
        {"name": "Cove Burger", "price": 9.99, "category": "Main Course"},
        {"name": "Cove Fries", "price": 3.99, "category": "Sides"},
        {"name": "Cove Coke", "price": 1.99, "category": "Drinks"},
        {"name": "Cove Salad", "price": 4.99, "category": "Appetizers"},
    ]
    return jsonify(menu_items)

#return json for different mystic locations

@menu_blueprint.route('/menu/mystic/chopbox')
def chopbox_menu():
    return mystic_menu('tabs-chopbox')

@menu_blueprint.route('/menu/mystic/fresco-taco')
def fresco_taco_menu():
    return mystic_menu('tabs-fresco-taco')

@menu_blueprint.route('/menu/mystic/flamin-good-chicken')
def flamin_good_chicken_menu():
    return mystic_menu('tabs-flamin-good-chicken')

@menu_blueprint.route('/menu/mystic/pickle-and-spice')
def pickle_and_spice_menu():
    return mystic_menu('tabs-pickle-and-spice')

#no menu for tofinos

def mystic_menu(location):
    #TODO: Implement this function

    #get webpage and check its 200 ok
    r = requests.get("https://www.uvic.ca/services/food/where/mysticmarket/index.php")
    if r.status_code != 200:
        return jsonify({"error": "Failed to retrieve page"}), 500
    
    #extract the menu items from the webpage
    soup = BeautifulSoup(r.content, 'html.parser')
    menu_items = parse(soup, location)

    #return the menu items as json
    return jsonify(menu_items)

def parse(soup, location):
    dict = {}

    section = soup.find(id=location)
    categories = section.find('div').find_all('h3', recursive=False)

    for category in categories:
        category_div = category.find_next_sibling('div').find('div')
        #get names of menu items
        menu_items = category_div.find_all('h3', recursive=False) 
        
        category_dict = {}

        for item in menu_items:
            #get dietary restriction information
            item_div = item.find_next_sibling('div')
            dietary_icons = item_div.find_all('img')
            print(len(dietary_icons))
            dietary_restrictions = []
            #find which icons apply
            for icon in dietary_icons:
                if 'vegan' in icon['src']:
                    dietary_restrictions.append('vegan')
                elif 'vegetarian' in icon['src']:
                    dietary_restrictions.append('vegetarian')
                elif 'gluten-free' in icon['src']:
                    dietary_restrictions.append('gluten free')
                elif 'dairy-free' in icon['src']:
                    dietary_restrictions.append('dairy free')
            print(dietary_restrictions)

            #get ingredients and allergens
            p_tags = item_div.find_all('p')
            ingredients = ''
            allergens = ''
            for tag in p_tags:
                tag_text = tag.text.strip()
                if 'Ingredients:' in tag_text:
                    ingredients = tag_text
                elif 'Contains:' in tag_text:
                    allergens = tag_text

            #get rid of "ingredients" and "contains" labels, and remove weird characters
            ingredients = ingredients.replace('\u00a0', ' ').split(': ')[1]
            allergens = allergens.replace('\u00a0', ' ').split(': ')[1]

            #add data to dictionary for that menu item
            menu_item_dict = {}
            menu_item_dict['dietary restrictions'] = dietary_restrictions
            menu_item_dict['ingredients'] = ingredients
            menu_item_dict['allergens'] = allergens
                
            #add to the category dictionary
            category_dict[item.string] = menu_item_dict
            
        #add to the main dictionary 
        dict[category.string] = category_dict
    return dict