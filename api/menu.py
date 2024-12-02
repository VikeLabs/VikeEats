from flask import Blueprint, jsonify, url_for
import requests
from bs4 import BeautifulSoup

# Create a blueprint for menus
menu_blueprint = Blueprint('menu', __name__)

@menu_blueprint.route('/menu')
def menu_home():
    # return url_for('menu.cove_menu'), url_for('menu.mystic_menu')
    return "Welcome to the menu page <br>" + "<br>Cove Menu: " + url_for('menu.cove_menu') + "<br>Mystic Menu: " + url_for('menu.mystic_menu')

@menu_blueprint.route('/menu/cove/greens')
def greens_menu():
    return cove_menu('tabs-greens')
    
@menu_blueprint.route('/menu/cove/deli')
def deli_menu():
    return cove_menu('tabs-deli')

@menu_blueprint.route('/menu/cove/shawarma')
def shawarma_menu():
    return cove_menu('tabs-shawarma')

@menu_blueprint.route('/menu/cove/asian-fusion')
def asian_fusion_menu():
    return cove_menu('tabs-asian-fusion')

@menu_blueprint.route('/menu/cove/pizza')
def pizza_menu():
    return cove_menu('tabs-pizza')

@menu_blueprint.route('/menu/cove/grill')
def grill_menu():
    return cove_menu('tabs-grill')

@menu_blueprint.route('/menu/cove/entre')
def entre_menu():
    return cove_menu('tabs-entre')

@menu_blueprint.route('/menu/cove/bread')
def bread_menu():
    return cove_menu('tabs-bread')

@menu_blueprint.route('/menu/cove/halal')
def halal_menu():
    return cove_menu('tabs-halal')


def cove_menu(location):
    #TODO: Implement this function

    #get webpage and check its 200 ok
    r = requests.get("https://www.uvic.ca/services/food/where/thecove/index.php")
    if r.status_code != 200:
        return jsonify({"error": "Failed to retrieve page"}), 500
    
    #extract the menu items from the webpage
    soup = BeautifulSoup(r.content, 'html.parser')
    menu_items = parse(soup, location)

    #return the menu items as json
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
            if ingredients == 'Ingredients:':
                ingredients = ''
            else:
                ingredients = ingredients.replace('\u00a0', ' ').split(': ')[1]
            
            if allergens == 'Contains:':
                allergens = ''
            else:
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