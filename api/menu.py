from flask import Blueprint, jsonify, url_for
import requests
from bs4 import BeautifulSoup

# Create a blueprint for menus
menu_blueprint = Blueprint('menu', __name__)

<<<<<<< Updated upstream
@menu_blueprint.route('/menu', methods=['GET'])
=======

#UPDATED FUNCTIONS
def mystic_cove_menu_dict(url, location):
    #get webpage and check its 200 ok
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Failed to retrieve page")
    
    #extract the menu items from the webpage
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Kiosks that don't have sub-categories (items listed directly under h3 headers)
    alt_locations = [
        'tabs-verde', 'tabs-mykonos', 'tabs-vikes-grill', 'tabs-bento',
        'tabs-the-sandwich-lab', 'tabs-nonnas', 'tabs-feast',
        'tabs-breads', 'tabs-halal', 'tabs-baked-goods', 'tabs-soups'
    ]
    
    if location in alt_locations:
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
    
def others_menus_dict(url):
    #get webpage and check its 200 ok
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Failed to retrieve page")
    
    #extract the menu items from the webpage
    soup = BeautifulSoup(r.content, 'html.parser')
    menu_items = parse_list(soup)
    return menu_items

def others_menus(url):
    try:
        menu_items = others_menus_dict(url)
        return jsonify(menu_items)
    except:
        return jsonify({"error": "Failed to retrieve menu"}), 500

@menu_blueprint.route('/menu')
>>>>>>> Stashed changes
def menu_home():
    # return url_for('menu.cove_menu'), url_for('menu.mystic_menu')
    return "Welcome to the menu page <br>" + "<br>Cove Menu: " + url_for('menu.cove_menu') + "<br>Mystic Menu: " + url_for('menu.mystic_menu')

@menu_blueprint.route('/menu/cove', methods=['GET'])
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

@menu_blueprint.route('/menu/mystic', methods=['GET'])
def mystic_menu():
    #TODO: Implement this function

    #get webpage and check its 200 ok

    #extract the menu items from the webpage

    #return the menu items as json

    #sample menu items feel free to delete

<<<<<<< Updated upstream
    menu_items = [
        {"name": "Mystic Burger", "price": 9.99, "category": "Main Course"},
        {"name": "Mystic Fries", "price": 3.99, "category": "Sides"},
        {"name": "Mystic Coke", "price": 1.99, "category": "Drinks"},
        {"name": "Mystic Salad", "price": 4.99, "category": "Appetizers"},
    ]
    return jsonify(menu_items)
=======
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
    if not section: return dict
    
    # Use find because items are usually wrapped in a container div
    container = section.find('div')
    if not container: return dict
    
    categories = container.find_all('h3', recursive=False)

    for category in categories:
        cat_name = category.get_text(strip=True)
        category_div = category.find_next_sibling('div')
        if not category_div: continue
        
        # Look for nested accordions
        inner_container = category_div.find('div')
        if not inner_container: continue
        
        menu_items = inner_container.find_all('h3', recursive=False) 
        
        category_dict = {}

        for item in menu_items:
            item_name = item.get_text(strip=True)
            #get dietary restriction information
            item_div = item.find_next_sibling('div')
            if not item_div: continue
            
            dietary_icons = item_div.find_all('img')
            dietary_restrictions = []
            #find which icons apply
            for icon in dietary_icons:
                src = icon.get('src', '').lower()
                if 'vegan' in src:
                    dietary_restrictions.append('vegan')
                elif 'vegetarian' in src:
                    dietary_restrictions.append('vegetarian')
                elif 'gluten-free' in src or 'without-gluten' in src:
                    dietary_restrictions.append('gluten free')
                elif 'dairy-free' in src or 'without-dairy' in src:
                    dietary_restrictions.append('dairy free')

            #get ingredients and allergens
            p_tags = item_div.find_all('p')
            div_tags = item_div.find_all('div')

            ingredients = ''
            allergens = ''
            for tag in p_tags + div_tags:
                tag_text = tag.text.strip()
                if 'Ingredients:' in tag_text:
                    ingredients = tag_text
                elif 'Contains:' in tag_text:
                    allergens = tag_text

            # Clean labels
            if ingredients.startswith('Ingredients:'):
                try:
                    ingredients = ingredients.replace('\u00a0', ' ').split(':', 1)[1].strip()
                except: pass
            
            if allergens.startswith('Contains:'):
                try:
                    allergens = allergens.replace('\u00a0', ' ').split(':', 1)[1].strip()
                except: pass

            menu_item_dict = {
                'dietary restrictions': dietary_restrictions,
                'ingredients': ingredients,
                'allergens': allergens
            }
            category_dict[item_name] = menu_item_dict
            
        dict[cat_name] = category_dict
    return dict

# An alternate parse function to take care of cove items without sub-categories
def parse_cove_alt(soup, location):
    dict = {}

    section = soup.find(id=location)
    if not section: return dict
    
    container = section.find('div')
    if not container: return dict
    
    items = container.find_all('h3', recursive=False)

    for item in items:
        item_name = item.get_text(strip=True)
        item_div = item.find_next_sibling('div')
        if not item_div: continue
        
        dietary_icons = item_div.find_all('img')
        dietary_restrictions = []
        for icon in dietary_icons:
            src = icon.get('src', '').lower()
            if 'vegan' in src:
                dietary_restrictions.append('vegan')
            elif 'vegetarian' in src:
                dietary_restrictions.append('vegetarian')
            elif 'gluten-free' in src or 'without-gluten' in src:
                dietary_restrictions.append('gluten free')
            elif 'dairy-free' in src or 'without-dairy' in src:
                dietary_restrictions.append('dairy free')
            elif 'halal' in src:
                dietary_restrictions.append('halal')

        p_tags = item_div.find_all('p')
        div_tags = item_div.find_all('div')

        ingredients = ''
        allergens = ''
        for tag in p_tags + div_tags:
            tag_text = tag.text.strip()
            if 'Ingredients:' in tag_text:
                ingredients = tag_text
            elif 'Contains:' in tag_text:
                allergens = tag_text

        if ingredients.startswith('Ingredients:'):
            try:
                ingredients = ingredients.replace('\u00a0', ' ').split(':', 1)[1].strip()
            except: pass
        
        if allergens.startswith('Contains:'):
            try:
                allergens = allergens.replace('\u00a0', ' ').split(':', 1)[1].strip()
            except: pass

        menu_item_dict = {
            'dietary restrictions': dietary_restrictions,
            'ingredients': ingredients,
            'allergens': allergens
        }
        dict[item_name] = menu_item_dict
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
>>>>>>> Stashed changes
