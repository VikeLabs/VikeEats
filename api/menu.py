from flask import Blueprint, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
    
    menu_items = parse_location_section(soup, location, url)

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
def menu_home():
    return "Welcome to the menu page"

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



def parse_location_section(soup, location, base_url):
    section = soup.find(id=location)
    if not section:
        return {}

    container = section.find('div')
    if not container:
        return {}

    parsed = parse_heading_blocks(container, base_url)
    if not parsed:
        return {}

    # Keep existing response shape: flat item map when no category layer exists.
    if all(is_item_details(value) for value in parsed.values()):
        return parsed
    return parsed


def parse_heading_blocks(container, base_url):
    result = {}
    headers = container.find_all('h3', recursive=False)

    for header in headers:
        name = header.get_text(strip=True)
        if not name:
            continue

        block = next_div_sibling(header)
        if not block:
            continue

        nested = first_child_container_with_headers(block)
        if nested:
            nested_result = parse_heading_blocks(nested, base_url)
            if nested_result:
                result[name] = nested_result
                continue

        details = parse_item_details(block, base_url)
        if details:
            result[name] = details

    return result


def next_div_sibling(tag):
    sibling = tag.next_sibling
    while sibling:
        if getattr(sibling, 'name', None) == 'div':
            return sibling
        sibling = sibling.next_sibling
    return None


def first_child_container_with_headers(container):
    candidate = container
    for _ in range(4):
        direct_headers = candidate.find_all('h3', recursive=False)
        if direct_headers:
            return candidate
        child_divs = candidate.find_all('div', recursive=False)
        if len(child_divs) != 1:
            return None
        candidate = child_divs[0]
    return None


def parse_item_details(item_div, base_url):
    dietary_restrictions = parse_dietary_restrictions(item_div)
    ingredients, allergens = parse_ingredients_and_allergens(item_div)
    details_link = find_detail_link(item_div, base_url)

    if not dietary_restrictions and not ingredients and not allergens and not details_link:
        return None

    item_details = {
        'dietary restrictions': dietary_restrictions,
        'ingredients': ingredients,
        'allergens': allergens
    }
    if details_link:
        item_details['details link'] = details_link

    return item_details


def parse_dietary_restrictions(item_div):
    restrictions = []
    for icon in item_div.find_all('img'):
        src = icon.get('src', '').lower()
        if 'vegan' in src:
            restrictions.append('vegan')
        elif 'vegetarian' in src:
            restrictions.append('vegetarian')
        elif 'gluten-free' in src or 'without-gluten' in src:
            restrictions.append('gluten free')
        elif 'dairy-free' in src or 'without-dairy' in src:
            restrictions.append('dairy free')
        elif 'halal' in src:
            restrictions.append('halal')
    return restrictions


def parse_ingredients_and_allergens(item_div):
    ingredients = ''
    allergens = ''
    for tag in item_div.find_all(['p', 'div']):
        text = tag.get_text(" ", strip=True).replace('\u00a0', ' ')
        if not ingredients and 'Ingredients:' in text:
            ingredients = clean_detail_label(text, 'Ingredients:')
        if not allergens and 'Contains:' in text:
            allergens = clean_detail_label(text, 'Contains:')
    return ingredients, allergens


def clean_detail_label(value, label):
    if value.startswith(label):
        try:
            return value.split(':', 1)[1].strip()
        except Exception:
            return value
    return value


def find_detail_link(item_div, base_url):
    for link in item_div.find_all('a', href=True):
        href = link.get('href', '').strip()
        if not href:
            continue

        href_lower = href.lower()
        text_lower = link.get_text(' ', strip=True).lower()
        if (
            href_lower.endswith('.pdf')
            or '.pdf?' in href_lower
            or 'allergen' in text_lower
            or 'ingredient' in text_lower
            or 'menu' in text_lower
        ):
            return urljoin(base_url, href)
    return ''


def is_item_details(value):
    if not isinstance(value, dict):
        return False
    required_keys = {'dietary restrictions', 'ingredients', 'allergens'}
    return required_keys.issubset(set(value.keys()))

def parse_list(soup):
    menu_items = []
    page_content = soup.find(id='content')
    lst = page_content.find('ul', recursive=False)
    items = lst.find_all('li', recursive=False) #get the list of menu items
    
    for item in items:
        item_str = item.string.replace('\u00a0', ' ') #remove weird characters
        menu_items.append(item_str)

    return menu_items
