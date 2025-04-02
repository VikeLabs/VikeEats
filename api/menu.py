from flask import Blueprint, jsonify, url_for
import requests
from bs4 import BeautifulSoup

# Create a blueprint for menus
menu_blueprint = Blueprint('menu', __name__)


#UPDATED FUNCTIONS
def mystic_cove_menu_dict(url, location):
    #get webpage and check its 200 ok
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Failed to retrieve page")
    
    #extract the menu items from the webpage
    soup = BeautifulSoup(r.content, 'html.parser')
    if location == 'tabs-asian-fusion' or location == 'tabs-bread' or location == 'tabs-halal':
        menu_items = parse_cove_alt(soup, location)
    else:
        menu_items = parse(soup, location)

    return menu_items

def mystic_cove_menu_response(url, location):
    try:
        menu_items = mystic_cove_menu_dict(url, location)
        return jsonify(menu_items)
    except:
        return jsonify({"error": "Failed to retrieve menu"}), 500
    
def others_menus(url):
    #get webpage and check its 200 ok
    r = requests.get(url)
    if r.status_code != 200:
        return jsonify({"error": "Failed to retrieve page"}), 500
    
    #extract the menu items from the webpage
    soup = BeautifulSoup(r.content, 'html.parser')
    menu_items = parse_list(soup)
    return jsonify(menu_items)

@menu_blueprint.route('/menu')
def menu_home():
    # return url_for('menu.cove_menu'), url_for('menu.mystic_menu')
    return "Welcome to the menu page <br>" + "<br>Cove Menu: " + url_for('menu.cove_menu') + "<br>Mystic Menu: " + url_for('menu.mystic_menu')

@menu_blueprint.route('/menu/cove/greens')
def greens_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/thecove/index.php", 'tabs-greens')
    
@menu_blueprint.route('/menu/cove/deli')
def deli_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/thecove/index.php", 'tabs-deli')

@menu_blueprint.route('/menu/cove/shawarma')
def shawarma_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/thecove/index.php", 'tabs-shawarma')  

@menu_blueprint.route('/menu/cove/asian-fusion')
def asian_fusion_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/thecove/index.php", 'tabs-asian-fusion')

@menu_blueprint.route('/menu/cove/pizza')
def pizza_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/thecove/index.php", 'tabs-pizza')

@menu_blueprint.route('/menu/cove/grill')
def grill_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/thecove/index.php", 'tabs-grill')

@menu_blueprint.route('/menu/cove/entre')
def entre_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/thecove/index.php", 'tabs-entre')

@menu_blueprint.route('/menu/cove/bread')
def bread_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/thecove/index.php", 'tabs-bread')

@menu_blueprint.route('/menu/cove/halal')
def halal_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/thecove/index.php", 'tabs-halal')



#return json for different mystic locations

@menu_blueprint.route('/menu/mystic/chopbox')
def chopbox_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/mysticmarket/index.php", 'tabs-chopbox')

@menu_blueprint.route('/menu/mystic/fresco-taco')
def fresco_taco_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/mysticmarket/index.php", 'tabs-fresco-taco')

@menu_blueprint.route('/menu/mystic/flamin-good-chicken')
def flamin_good_chicken_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/mysticmarket/index.php", 'tabs-flamin-good-chicken')

@menu_blueprint.route('/menu/mystic/pickle-and-spice')
def pickle_and_spice_menu():
    return mystic_cove_menu_response("https://www.uvic.ca/services/food/where/mysticmarket/index.php", 'tabs-pickle-and-spice')

#no menu for tofinos


@menu_blueprint.route('/menu/bibliocafe')
def biblio_menu():
    return others_menus('https://www.uvic.ca/services/food/where/bibliocafe/index.php')


@menu_blueprint.route('/menu/arts-place')
def arts_place_menu():
    return others_menus('https://www.uvic.ca/services/food/where/artsplace/index.php')
    

@menu_blueprint.route('/menu/nibbles-and-bytes')
def nibbles_and_bytes_menu():
    return others_menus('https://www.uvic.ca/services/food/where/nibblesbytes/index.php')


@menu_blueprint.route('/menu/sci-cafe')
def sci_cafe_menu():
    return others_menus('https://www.uvic.ca/services/food/where/scicafe/index.php')



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

            #get ingredients and allergens
            p_tags = item_div.find_all('p')
            # Div tag is used because one of the food items in entre has info kept in a div and not p
            div_tags = item_div.find_all('div')

            ingredients = ''
            allergens = ''
            for tag in p_tags:
                tag_text = tag.text.strip()
                if 'Ingredients:' in tag_text:
                    ingredients = tag_text
                elif 'Contains:' in tag_text:
                    allergens = tag_text
            
            # for loop runs through all of the div tags to find the one food item whose info is in a div
            for tag in div_tags:
                tag_text = tag.text.strip()
                if 'Ingredients:' in tag_text:
                    ingredients = tag_text
                elif 'Contains:' in tag_text:
                    allergens = tag_text

            #get rid of "ingredients" and "contains" labels, and remove weird characters
            if ingredients == 'Ingredients:':
                ingredients = ''
            else:
                try:
                    ingredients = ingredients.replace('\u00a0', ' ').split(': ')[1]
                except:
                    # One food item in entre has no space between its colon and ingredients
                    ingredients = ingredients.replace('\u00a0', ' ').split(':')[1]
            
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

# An alternate parse function to take care of cove items in: asian-fusion, bread, and halal
def parse_cove_alt(soup, location):
    dict = {}

    section = soup.find(id=location)
    categories = section.find('div').find_all('h3', recursive=False)

    for category in categories:
        # Get names of menu items
        item_div = category.find_next_sibling('div')
        
        category_dict = {}

        
        #get dietary restriction information
        
        dietary_icons = item_div.find_all('img')
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
            elif 'halal' in icon['src']:
                dietary_restrictions.append('halal')

        #get ingredients and allergens
        p_tags = item_div.find_all('p')
        # Div tag is used because one of the food items in entre has info kept in a div and not p
        div_tags = item_div.find_all('div')

        ingredients = ''
        allergens = ''
        for tag in p_tags:
            tag_text = tag.text.strip()
            if 'Ingredients:' in tag_text:
                ingredients = tag_text
            elif 'Contains:' in tag_text:
                allergens = tag_text
        
        # for loop runs through all of the div tags to find the one food item whose info is in a div
        for tag in div_tags:
            tag_text = tag.text.strip()
            if 'Ingredients:' in tag_text:
                ingredients = tag_text
            elif 'Contains:' in tag_text:
                allergens = tag_text

        #get rid of "ingredients" and "contains" labels, and remove weird characters
        if ingredients == 'Ingredients:':
            ingredients = ''
        else:
            try:
                ingredients = ingredients.replace('\u00a0', ' ').split(': ')[1]
            except:
                # One food item in entre has no space between its colon and ingredients
                ingredients = ingredients.replace('\u00a0', ' ').split(':')[1]
        
        if allergens == 'Contains:':
            allergens = ''
        else:
            allergens = allergens.replace('\u00a0', ' ').split(': ')[1]

        #add data to dictionary for that menu item
        menu_item_dict = {}
        menu_item_dict['dietary restrictions'] = dietary_restrictions
        menu_item_dict['ingredients'] = ingredients
        menu_item_dict['allergens'] = allergens\
            
        #add to the main dictionary 
        dict[category.string] = menu_item_dict
    return dict

def parse_list(soup):
    menu_items = []
    page_content = soup.find(id='content')
    lst = page_content.find('ul', recursive=False)
    items = lst.find_all('li', recursive=False) #get the list of menu items
    
    for item in items:
        item_str = item.string.replace('\u00a0', ' ') #remove weird characters
        menu_items.append(item_str)

    return menu_items