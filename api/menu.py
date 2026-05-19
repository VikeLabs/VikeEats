from flask import Blueprint, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from io import BytesIO
import re
from pypdf import PdfReader

# Create a blueprint for menus
menu_blueprint = Blueprint('menu', __name__)
PDF_DETAILS_CACHE = {}

# French / bilingual PDF section headers (tolerant of mojibake between R and D).
_PDF_FR_INGREDIENTS_HEADER = re.compile(
    r'\s+INGR.{0,8}DIENTS\s*:|\s+Ingr[ée]dients\s*:|\s+LISTE\s+D[\'\u2019]?INGR[ÉE]DIENTS\s*:',
    re.IGNORECASE,
)
_PDF_ALLERGEN_BLEED = (
    re.compile(r'\s+\d{2}/\d{2}/\d{4}\b'),
    re.compile(r'\bwww\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'),
    re.compile(r'\b\d{3}-\d{3}-\d{4}\b'),
)

# Manual fallback skeleton: fill these values directly when source data is missing/noisy.
# Key format:
#   { "<tab-id>": { "<item name>": {"ingredients": "...", "allergens": "..."} } }
MANUAL_ITEM_DETAILS = {
    "tabs-soups": {
        "Boston Clam Chowder": {"ingredients": "", "allergens": ""},
        "Broccoli and Cheese": {"ingredients": "", "allergens": ""},
        "Butternut Squash": {"ingredients": "", "allergens": ""},
        "Cauliflower Cheese": {"ingredients": "", "allergens": ""},
        "Chicken Corn Chowder": {"ingredients": "", "allergens": ""},
        "Chicken Noodle": {"ingredients": "", "allergens": ""},
        "Chicken with Wild Rice": {"ingredients": "", "allergens": ""},
        "Cream of Mushroom": {"ingredients": "", "allergens": ""},
        "Cream of Potato and Bacon": {"ingredients": "", "allergens": ""},
        "Creamy Garden Cauliflower": {"ingredients": "", "allergens": ""},
        "Creole Chicken Gumbo": {"ingredients": "", "allergens": ""},
        "French Onion": {"ingredients": "", "allergens": ""},
        "Golden Autumn Carrot": {"ingredients": "", "allergens": ""},
        "Homestyle Minestrone": {"ingredients": "", "allergens": ""},
        "Homestyle Vegetable Beef and Barley": {"ingredients": "", "allergens": ""},
        "Italian Wedding": {"ingredients": "", "allergens": ""},
        "Loaded Baked Potato": {"ingredients": "", "allergens": ""},
        "Split Pea and Ham": {"ingredients": "", "allergens": ""},
        "Tomato Ravioli": {"ingredients": "", "allergens": ""},
        "Tomato Roasted Red Pepper": {"ingredients": "", "allergens": ""},
    }
}


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

    parsed = parse_heading_blocks(container, base_url, location)
    if not parsed:
        return {}

    # Keep existing response shape: flat item map when no category layer exists.
    if all(is_item_details(value) for value in parsed.values()):
        return parsed
    return parsed


def parse_heading_blocks(container, base_url, location):
    result = {}
    headers = container.find_all('h3', recursive=False)

    for header in headers:
        name = header.get_text(strip=True)
        if not name:
            continue

        block = next_div_sibling(header)
        if not block:
            continue

        nested = find_nested_menu_container(block)
        if nested:
            nested_result = parse_heading_blocks(nested, base_url, location)
            if nested_result:
                result[name] = nested_result
                continue
            if nested_menu_has_titled_headers(nested):
                continue

        details = parse_item_details(block, base_url)
        if details:
            details = apply_manual_item_overrides(location, name, details)
            result[name] = details

    return result


def next_div_sibling(tag):
    sibling = tag.next_sibling
    while sibling:
        if getattr(sibling, 'name', None) == 'div':
            return sibling
        sibling = sibling.next_sibling
    return None


def h3_has_menu_title(h3):
    if not h3:
        return False
    text = h3.get_text(strip=True).replace('\u00a0', ' ')
    if len(text) >= 3:
        return True
    return False


def nested_menu_has_titled_headers(container):
    return any(h3_has_menu_title(h) for h in container.find_all('h3'))


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


def find_nested_menu_container(block):
    """
    Locate inner accordion / submenu container. Handles:
    - Single chain of wrapper divs (original behaviour).
    - Multiple direct child divs (intro column + accordions).
    - Blocks where the only direct h3 rows are icon-only: treat as no nested menu
      so the section is parsed as one item (ingredients on siblings).
    """
    nested = first_child_container_with_headers(block)
    if nested is not None and nested is block:
        direct_h3 = block.find_all('h3', recursive=False)
        if direct_h3 and not any(h3_has_menu_title(h) for h in direct_h3):
            nested = None
    if nested is not None:
        return nested

    best = None
    best_count = -1
    for div in block.find_all('div', recursive=False):
        titled = sum(
            1 for h in div.find_all('h3', recursive=False) if h3_has_menu_title(h)
        )
        if titled > best_count:
            best = div
            best_count = titled
    if best is not None and best_count >= 1:
        return best
    return None


def refine_pdf_ingredient_text(raw):
    """Keep English ingredients; drop French duplicate block and trailing junk."""
    if not raw:
        return ''
    text = raw.strip()
    m = _PDF_FR_INGREDIENTS_HEADER.search(text)
    if m:
        text = text[: m.start()]
    return text.strip(' .;,')


def refine_pdf_allergen_text(raw):
    """English allergens only; trim French 'Contient' and product / URL bleed."""
    if not raw:
        return ''
    text = raw.strip()
    m = re.search(r'\s+Contient\s*:', text, re.IGNORECASE)
    if m:
        text = text[: m.start()]
    m = re.search(r'\s+Peut\s+contenir\s*:', text, re.IGNORECASE)
    if m:
        text = text[: m.start()]
    cut = len(text)
    for pat in _PDF_ALLERGEN_BLEED:
        m2 = pat.search(text)
        if m2 is not None:
            cut = min(cut, m2.start())
    text = text[:cut].strip(' .;,')
    # Product title merged after disclaimer when date/phone were stripped first.
    text = re.sub(
        r'\.\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,5}\s*$',
        '.',
        text,
    )
    return text.strip(' .;,')


def parse_item_details(item_div, base_url):
    dietary_restrictions = parse_dietary_restrictions(item_div)
    ingredients, allergens = parse_ingredients_and_allergens(item_div)
    details_link = find_detail_link(item_div, base_url)
    pdf_products = []
    if details_link and details_link.lower().endswith(".pdf"):
        pdf_ingredients, pdf_allergens, pdf_products = extract_pdf_ingredients_allergens(details_link)
        if not ingredients:
            ingredients = pdf_ingredients
        if not allergens:
            allergens = pdf_allergens

    if not dietary_restrictions and not ingredients and not allergens and not details_link:
        return None

    item_details = {
        'dietary restrictions': dietary_restrictions,
        'ingredients': ingredients,
        'allergens': allergens
    }
    if details_link:
        item_details['details link'] = details_link
    if pdf_products:
        item_details['pdf products'] = pdf_products

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


def extract_pdf_ingredients_allergens(pdf_url):
    if pdf_url in PDF_DETAILS_CACHE:
        return PDF_DETAILS_CACHE[pdf_url]

    ingredients = ''
    allergens = ''
    products = []
    try:
        response = requests.get(pdf_url, timeout=20)
        if response.status_code != 200:
            PDF_DETAILS_CACHE[pdf_url] = (ingredients, allergens, products)
            return ingredients, allergens, products

        reader = PdfReader(BytesIO(response.content))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text() or ''
            if page_text:
                text_parts.append(page_text)

        pdf_text = re.sub(r'\s+', ' ', ' '.join(text_parts)).strip()
        ingredients_match = re.search(
            r'Ingredients\s*:\s*(.*?)(?:Contains\s*:|Allergen\s+Information|Receiving\s+Specifications|Shelf\s+life|$)',
            pdf_text,
            re.IGNORECASE
        )
        allergens_match = re.search(
            r'Contains\s*:\s*(.*?)(?:Allergen\s+Information|Receiving\s+Specifications|Shelf\s+life|P\s*:\s*\d|$)',
            pdf_text,
            re.IGNORECASE
        )

        if ingredients_match:
            ingredients = refine_pdf_ingredient_text(ingredients_match.group(1))
        if allergens_match:
            allergens = refine_pdf_allergen_text(allergens_match.group(1))

        products = extract_products_from_pdf_text(pdf_text)
    except Exception:
        pass

    PDF_DETAILS_CACHE[pdf_url] = (ingredients, allergens, products)
    return ingredients, allergens, products


def extract_products_from_pdf_text(pdf_text):
    products = []
    seen_names = set()
    title_pattern = re.compile(r'([A-Z][A-Za-z0-9/&,\-\'+ ]{2,80})\s+\d{2}/\d{2}/\d{4}')
    title_matches = list(title_pattern.finditer(pdf_text))

    for idx, match in enumerate(title_matches):
        name = clean_product_name(match.group(1))
        if not is_valid_product_name(name) or name.lower() in seen_names:
            continue

        start = match.end()
        end = title_matches[idx + 1].start() if idx + 1 < len(title_matches) else len(pdf_text)
        segment = pdf_text[start:end]
        ingredients, allergens = extract_segment_ingredients_allergens(segment)
        if not ingredients and not allergens:
            continue

        seen_names.add(name.lower())
        products.append({
            "name": name,
            "ingredients": ingredients,
            "allergens": allergens
        })

    return products


def extract_segment_ingredients_allergens(segment_text):
    ingredients = ''
    allergens = ''
    ingredients_match = re.search(
        r'Ingredients?\s*[:;]?\s*(.*?)(?:Contains?|Allergen\s+Information|Allergens?|Receiving\s+Specifications|Shelf\s+life|$)',
        segment_text,
        re.IGNORECASE
    )
    allergens_match = re.search(
        r'(?:Contains?|Allergens?)\s*[:;]?\s*(.*?)(?:Allergen\s+Information|Receiving\s+Specifications|Shelf\s+life|P\s*:\s*\d|$)',
        segment_text,
        re.IGNORECASE
    )

    if ingredients_match:
        ingredients = refine_pdf_ingredient_text(ingredients_match.group(1))
    if allergens_match:
        allergens = refine_pdf_allergen_text(allergens_match.group(1))
    return ingredients, allergens


def clean_product_name(name):
    cleaned = re.sub(r'\s+', ' ', name).strip(" .;:-")
    return cleaned


def is_valid_product_name(name):
    if not name:
        return False
    lowered = name.lower()
    blocked = [
        "ingredients",
        "contains",
        "allergen information",
        "receiving specifications",
        "shelf life",
    ]
    if lowered in blocked:
        return False
    if len(name) < 3:
        return False
    return True


def apply_manual_item_overrides(location, item_name, item_details):
    section_overrides = MANUAL_ITEM_DETAILS.get(location, {})
    override = section_overrides.get(item_name, {})
    if not override:
        return item_details

    merged = dict(item_details)
    if override.get("ingredients"):
        merged["ingredients"] = override["ingredients"]
    if override.get("allergens"):
        merged["allergens"] = override["allergens"]
    return merged


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
