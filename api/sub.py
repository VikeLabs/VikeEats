import json
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, Blueprint, Response, jsonify
from datetime import datetime

sub_hours_blueprint = Blueprint('sub_hours', __name__)
app = Flask(__name__)

SUB_MENUS = {
    "Bean There Cafe": {
        "categories": {
            "Menu": [
              {"name": "Brewed Coffee", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Espresso", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Latte", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Cappuccino", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Americano", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Mocha", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Hot Chocolate", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Iced Mocha", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Iced Latte", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Iced Americano", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Tea", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Steamed Milk", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Chai Latte", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "London Fog", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Matcha Latte", "dietary restrictions": ["vegan", "vegetarian", "gluten free"]},
              {"name": "Muffins", "dietary restrictions": ["vegetarian", "gluten free"]},
              {"name": "Bagels"},
              {"name": "Egg Muffins", "dietary restrictions": ["vegetarian"]},
              {"name": "Pasteries"},
              {"name": "Cookies", "dietary restrictions": ["vegetarian"]},
              {"name": "Sandwiches", "dietary restrictions": ["vegan", "vegetarian"]},
              {"name": "Wraps", "dietary restrictions": ["vegan", "vegetarian"]},
              {"name": "Sushi", "dietary restrictions": ["vegan", "gluten free"]},
          ]
        }
    },
    "Felicita’s Campus Pub": {
        "categories": {}
    },
    "The Grill": {
        "categories": {
            "Burgers": [
                {"name": "The Works Burger", "ingredients": "Charbroiled beef patty with bacon, cheddar cheese, mushrooms, onions, lettuce, tomato, pickles, burger sauce", "allergens": ""},
                {"name": "Cheese Burger", "ingredients": "Charbroiled beef patty with cheddar cheese, lettuce, tomato, pickles, burger sauce", "allergens": ""},
                {"name": "Double Cheese Burger", "ingredients": "2 charbroiled beef patties with 2 slices of cheddar cheese, burger sauce", "allergens": ""},
                {"name": "Bacon Cheddar Burger", "ingredients": "Charbroiled beef patty with bacon, cheddar cheese, lettuce, tomato, pickles, burger sauce", "allergens": ""},
                {"name": "BBQ Mushroom & Bacon Burger", "ingredients": "Charbroiled beef patty with bacon, fried onions, mushrooms, lettuce, BBQ sauce", "allergens": ""},
                {"name": "Basic Burger", "ingredients": "Charbroiled beef patty with lettuce, tomato, pickles, burger sauce", "allergens": ""},
                {"name": "West Coast Salmon Burger", "ingredients": "Alaskan wild caught salmon patty charbroiled and garnished with a tangy coleslaw", "allergens": ""},
                {"name": "Crispy Chicken Burger", "ingredients": "Breaded chicken strips with lettuce, tomato, pickles, burger sauce", "allergens": ""},
                {"name": "French Onion & Bacon Grilled Cheese Sandwich", "ingredients": "French bread topped with mixed cheese, fried onions, bacon", "allergens": ""},
                {"name": "Classic Grilled Cheese Sandwich", "ingredients": "French bread, garlic butter, cheddar cheese", "allergens": ""},
                {"name": "Grilled Chicken Sandwich", "ingredients": "Grilled chicken breast and mixed cheese on French bread with basil mayo", "allergens": ""},
            ],
            "International": [
                {"name": "Curry Noodle Soup", "ingredients": "Rice noodles in a spicy red Thai curry broth topped with fresh vegetables and your choice of chicken or tofu", "allergens": ""},
                {"name": "Sweet & Sour Pork", "ingredients": "Crispy pork tossed in a sweet & sour pineapple sauce served on steamed rice", "allergens": ""},
                {"name": "Hokkien Noodle Stirfry", "ingredients": "Thick wheat noodles stirfried with chicken or tofu, carrots, sui choy, and green onion in a sweet ginger & dark soy coconut sauce", "allergens": ""},
                {"name": "Ginger Beef Stirfry", "ingredients": "Crispy beef strips stirfried with peppers, onion, and carrot in a spicy sweet ginger sauce, served on rice", "allergens": ""},
                {"name": "Chicken Chow Mein", "ingredients": "Chow mein noodles and chicken stirfried with carrots, cabbage, bean sprouts, and green onion in a savoury sauce", "allergens": ""},
                {"name": "Indian Style Chicken Curry", "ingredients": "Diced chicken in a rich and spicy tomato curry served with rice and a warm pita", "allergens": ""},
                {"name": "Chicken Shawarma Bowl", "ingredients": "Spiced chicken served on rice with lettuce, tomato, banana peppers, sweet pickle relish, and Tahini yogurt sauce", "allergens": ""},
                {"name": "Meatball Sub", "ingredients": "Beef meatballs with Marinara sauce topped with mixed cheese and served in a sub bun", "allergens": ""},
                {"name": "Greek Gyro", "ingredients": "Sliced lamb and beef gyro wrapped in a pita with lettuce, tomato, diced onion and tzatziki", "allergens": ""},
                {"name": "East Coast Donair", "ingredients": "Beef and lamb gyro wrapped in a pita with diced onion, tomato, and a sweet garlic sauce", "allergens": ""},
                {"name": "Chicken Shawarma Wrap", "ingredients": "Spiced chicken wrapped in a pita with lettuce, tomato, banana peppers, sweet pickle relish, and Tahini yogurt sauce", "allergens": ""},
                {"name": "Black Bean Burrito", "ingredients": "Black beans, Spanish rice, cheese, lettuce, sour cream and salsa wrapped in a flour tortilla", "allergens": ""},
                {"name": "Pulled Pork Burrito", "ingredients": "Seasoned slow cooked BBQ pork wrapped in a flour tortilla with Spanish rice, sour cream and salsa", "allergens": ""},
                {"name": "Spaghetti & Meatballs", "ingredients": "Pork meatballs in a Marinara sauce served on spaghetti with parmesan cheese and garlic toast", "allergens": ""},
            ],
            "Favourites": [
                {"name": "Chicken Caesar Wrap", "ingredients": "Breaded chicken and Caesar salad with parmesan cheese wrapped in a flour tortilla, served with your choice of side", "allergens": ""},
                {"name": "Pulled Chicken Wrap", "ingredients": "Chipotle chicken rolled in a flour tortilla with lettuce, tomato and sour cream, served with your choice of side", "allergens": ""},
                {"name": "Black Bean Wrap", "ingredients": "Seasoned black beans with onions and peppers wrapped in a flour tortilla with lettuce, cheese, tomato, and sour cream, served with your choice of side", "allergens": ""},
                {"name": "Cod Wrap", "ingredients": "Battered cod and coleslaw wrapped in a flour tortilla, served with your choice of side", "allergens": ""},
                {"name": "Chicken Strips", "ingredients": "Breaded chicken strips fried until crispy and served with your choice of dipping sauce and side", "allergens": ""},
                {"name": "Pulled Pork or Chicken Quesadilla", "ingredients": "BBQ Pork or Chipotle Chicken with cheese folded in a flour tortilla and grilled, served with salsa, sour cream and your choice of side", "allergens": ""},
                {"name": "Chicken Caesar Salad", "ingredients": "Caesar salad topped with crispy chicken and parmesan cheese, served with garlic bread", "allergens": ""},
                {"name": "The Breakfast Kaiser", "ingredients": "Fried egg, cheddar cheese, bacon, lettuce, tomato and mayo on a Brioche bun, served with your choice of side", "allergens": ""},
                {"name": "Breakfast Wrap", "ingredients": "Scrambled eggs with cheese rolled in a flour tortilla with lettuce and burger sauce, served with your choice of side", "allergens": ""},
                {"name": "Kimchi Hash Bowl", "ingredients": "Hash browns topped with scrambled eggs, fresh kimchi, sriracha mayo and green onion", "allergens": ""},
                {"name": "Ranchero Breakfast Bowl", "ingredients": "Scrambled eggs tossed with hashbrowns, seasoned black beans, cheese, sour cream, salsa and sriracha mayo", "allergens": ""},
                {"name": "Farmers Wrap", "ingredients": "Scrambled eggs, bacon, cheese, hashbrowns and sriracha mayo in a flour tortilla, served with your choice of side", "allergens": ""},
                {"name": "The Grill Poutine", "ingredients": "French fries topped with mixed cheese and beef gravy", "allergens": ""},
                {"name": "BBQ Pork Poutine", "ingredients": "French fries topped with Pulled Pork, mixed cheese and BBQ sauce", "allergens": ""},
                {"name": "Fish & Chips", "ingredients": "Battered cod strips served with fries, coleslaw and tartar sauce", "allergens": ""},
            ],
        }
    },
    "Health Food Bar (HFB)": {
        "categories": {
            "Bowls & Salads": [
                {"name": "Chicken Rice Bowl", "ingredients": "Diced chicken marinated with Peanut, Teriyaki or Hoisin sauce served on brown rice with Asian slaw, corn and sesame seeds", "dietary restrictions": []},
                {"name": "Tofu Rice Bowl", "ingredients": "Diced tofu marinated with Peanut, Teriyaki or Hoisin sauce served on brown rice with Asian slaw, corn and sesame seeds", "dietary restrictions": []},
                {"name": "Chicken or Beef Taco Bowl", "ingredients": "Diced chicken or Seasoned Beef served on brown rice with black beans, salsa, jalapenos, olives, corn, sour cream, cheese, and tortilla chips", "dietary restrictions": []},
                {"name": "Chili Taco Bowl", "ingredients": "Vegetarian Chili served on brown rice and garnished with jalapenos, sour cream, cheese, and tortilla chips", "dietary restrictions": []},
                {"name": "Falafel Bowl", "ingredients": "Falafel on brown rice with cucumber, tomato, olives, tzatziki and tahini", "dietary restrictions": []},
                {"name": "Daal with Rice", "ingredients": "Lentils and split peas stewed with garlic, ginger and Indian spices, served with brown rice and mango chutney", "dietary restrictions": []},
                {"name": "Vegetarian Chili", "ingredients": "Our own vegan chili served with corn tortilla chips, cheese and sour cream", "dietary restrictions": []},
                {"name": "Chicken Taco Salad", "ingredients": "Mixed greens topped with chicken, cheese, salsa, sour cream, olives, tomato, jalapeno peppers and tortilla chips", "dietary restrictions": []},
                {"name": "Chili Taco Salad", "ingredients": "Mixed greens topped with chili, cheese, salsa, sour cream, olives, tomato, jalapeno peppers and tortilla chips", "dietary restrictions": []},
                {"name": "Chicken Caesar Salad", "ingredients": "Caesar Salad topped with diced chicken, Parmesan cheese and croutons", "dietary restrictions": []},
                {"name": "Falafel Caesar Salad", "ingredients": "Caesar Salad topped with falafel, Parmesan cheese and croutons", "dietary restrictions": []},
                {"name": "Caesar Salad", "ingredients": "Romaine lettuce tossed with our own Caesar dressing and topped with Parmesan cheese and croutons", "dietary restrictions": []},
                {"name": "House Salad", "ingredients": "Mixed greens tossed with your choice of dressing and topped with cucumber, tomato, carrots and roasted pumpkin seeds", "dietary restrictions": []},
            ],
            "Sandwiches": [
                {"name": "BLT Sandwich", "ingredients": "Bacon, lettuce, tomato and mayo on a ciabatta bun", "dietary restrictions": []},
                {"name": "Chicken & Swiss Sandwich", "ingredients": "Ciabatta bun with Smoked chicken, Swiss cheese, roasted red pepper, spinach and basil mayo", "dietary restrictions": []},
                {"name": "Turkey & Bacon Sandwich", "ingredients": "Ciabatta bun with sliced Turkey, Bacon, lettuce, tomato and pesto mayo", "dietary restrictions": []},
                {"name": "Roast Beef & Cheddar Sandwich", "ingredients": "Multigrain bread with sliced roast beef, Cheddar cheese, yellow mustard, mayo, onions and tomato", "dietary restrictions": []},
                {"name": "Ham and Swiss Sandwich", "ingredients": "Multigrain bread with ham, swiss cheese, dijon mustard, pickles and mayo", "dietary restrictions": []},
                {"name": "Toasted Tuna Melt", "ingredients": "Ciabatta bun topped with tuna salad and cheese then toasted", "dietary restrictions": []},
                {"name": "HFB Cheese Steak Melt", "ingredients": "Ciabatta bun with basil mayo topped with roast beef, roasted veg, onion, and Swiss cheese then toasted", "dietary restrictions": []},
                {"name": "Chicken Salad Melt", "ingredients": "Ciabatta bun topped with Cranberry Chicken Salad and Gouda Cheese then toasted", "dietary restrictions": []},
                {"name": "Pita Melt", "ingredients": "Black Forest Ham, cheese, spinach, mayo and Dijon mustard served toasted on a pita", "dietary restrictions": []},
            ],
            "Wraps": [
                {"name": "Mexi Chicken Wrap", "ingredients": "Diced chicken or seasoned beef wrapped in a whole wheat tortilla with lettuce, tomato, black olives, jalapenos, cheese, salsa and sour cream", "dietary restrictions": []},
                {"name": "Black Bean Wrap", "ingredients": "Seasoned black beans with brown rice, lettuce, tomato, black olives, jalapenos, cheese, salsa and sour cream wrapped in a whole wheat tortilla", "dietary restrictions": []},
                {"name": "Chicken Caesar Wrap", "ingredients": "Diced chicken with caesar salad and parmesan cheese wrapped in a whole wheat tortilla", "dietary restrictions": []},
                {"name": "Falafel Caesar Wrap", "ingredients": "Falafel with caesar salad and parmesan cheese wrapped in a whole wheat tortilla", "dietary restrictions": []},
                {"name": "Spicy Chicken Peanut Wrap", "ingredients": "Seasoned chicken wrapped in a whole wheat tortilla with lettuce, rice, carrot, cucumber, and peanut sauce", "dietary restrictions": []},
                {"name": "Teriyaki Chicken Wrap", "ingredients": "Diced chicken with teriyaki sauce, brown rice, lettuce, cucumber and carrot wrapped in a whole wheat tortilla", "dietary restrictions": []},
                {"name": "Hummus & Roast Veg Wrap", "ingredients": "Roasted vegetables, Hummus, carrots, lettuce, cucumber, spinach and Tzatziki wrapped in a whole wheat tortilla", "dietary restrictions": []},
                {"name": "Falafel Pita", "ingredients": "Falafel with lettuce, cucumber, carrot and Tzatziki wrapped in a Greek style pita", "dietary restrictions": []},
            ],
            "Yogurt Smoothies": [
                {"name": "Berry All The Way", "ingredients": "Raspberry, strawberry, blackberry, blueberry", "dietary restrictions": []},
                {"name": "Strawberry Pina Colada", "ingredients": "Strawberry, pineapple juice, banana, coconut", "dietary restrictions": []},
                {"name": "High Five", "ingredients": "Peach, mango, orange juice, pineapple juice, banana", "dietary restrictions": []},
                {"name": "Mango Sub", "ingredients": "Mango, strawberry, peach, banana", "dietary restrictions": []},
                {"name": "Matcha Cranberry", "ingredients": "Green tea powder, cranberry", "dietary restrictions": []},
                {"name": "Monkey Madness", "ingredients": "Peanut butter, banana, chocolate", "dietary restrictions": []},
                {"name": "Passion Fruit", "ingredients": "Passion fruit, strawberry, peach, banana, orange juice", "dietary restrictions": []},
                {"name": "Pink Panther", "ingredients": "Beet, cranberry, raspberry, banana", "dietary restrictions": []},
                {"name": "Strawberry Twist", "ingredients": "Strawberry nectar, strawberry, banana", "dietary restrictions": []},
                {"name": "Zig Zag", "ingredients": "Raspberry, strawberry, banana", "dietary restrictions": []},
            ],
            "Puree Smoothies": [
                {"name": "Mango Tropics", "ingredients": "Mango, pineapple, banana", "dietary restrictions": []},
                {"name": "Tropical Sunshine", "ingredients": "Pineapple, banana, guava, passion fruit", "dietary restrictions": []},
                {"name": "Pineapple Paradise", "ingredients": "Pineapple, banana, coconut", "dietary restrictions": []},
                {"name": "Strawberry", "ingredients": "", "dietary restrictions": []},
                {"name": "Peach Pear Apricot", "ingredients": "", "dietary restrictions": []},
            ],
        }
    },
}

# @app.route('/')
# def index():
#     return "Hello World"
#     # return render_template('index.html')

def scrape_felicitas_menu():
    """
    Scrape the Felicita's menu from felicitas.ca/menus/.
    Returns: {tab_name: {sub_category: [items]}}
    e.g. {"Daily Features": {"Monday": [...], "Tuesday": [...]}, "Drinks": {"On Tap": [...], ...}}
    """
    url = "https://www.felicitas.ca/menus/"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            print(f"Failed to fetch Felicita's menu: HTTP {r.status_code}")
            return {}
    except Exception as e:
        print(f"Error fetching Felicita's menu: {e}")
        return {}

    soup = BeautifulSoup(r.content, 'html.parser')

    tabs_container = soup.find('div', class_='e-n-tabs')
    if not tabs_container:
        print("Could not find tabs container on Felicita's menu page")
        return {}

    tab_buttons = tabs_container.find('div', class_='e-n-tabs-heading').find_all('button', class_='e-n-tab-title')
    tab_names = []
    for btn in tab_buttons:
        title_span = btn.find('span', class_='e-n-tab-title-text')
        tab_names.append(title_span.get_text(strip=True) if title_span else "")

    tab_panels = tabs_container.find('div', class_='e-n-tabs-content').find_all(
        'div', role='tabpanel', recursive=False
    )

    result = {}

    for i, panel in enumerate(tab_panels):
        tab_name = tab_names[i] if i < len(tab_names) else f"Section {i+1}"

        headings = panel.find_all(['h2', 'h3'], class_='elementor-heading-title')
        price_lists = panel.find_all('ul', class_='elementor-price-list')

        if not headings:
            items = extract_menu_items(price_lists)
            if items:
                result[tab_name] = {tab_name: items}
        else:
            all_elements = panel.find_all(
                lambda tag: (tag.name in ['h2', 'h3'] and 'elementor-heading-title' in tag.get('class', []))
                or (tag.name == 'ul' and 'elementor-price-list' in tag.get('class', []))
            )

            current_heading = tab_name
            grouped = {}
            heading_elements = {}
            for el in all_elements:
                if el.name in ['h2', 'h3'] and 'elementor-heading-title' in el.get('class', []):
                    heading_text = el.get_text(strip=True).rstrip(':')
                    current_heading = heading_text.title() if heading_text.isupper() else heading_text
                    heading_elements[current_heading] = el
                elif el.name == 'ul':
                    items = extract_menu_items([el])
                    if items:
                        if current_heading not in grouped:
                            grouped[current_heading] = []
                        grouped[current_heading].extend(items)

            for heading_name, heading_el in heading_elements.items():
                if heading_name not in grouped:
                    widget = heading_el.find_parent('div', class_='elementor-widget')
                    if widget:
                        container = widget.parent
                        if container:
                            seen = set()
                            texts = []
                            for el2 in container.find_all(['p', 'em']):
                                if el2.find_parent('div', class_='elementor-widget-heading'):
                                    continue
                                t = el2.get_text(strip=True).replace('\xa0', ' ')
                                if not t or t in seen:
                                    continue
                                if re.search(r'^\d+\.\d+\s', t):
                                    continue
                                seen.add(t)
                                texts.append(t)
                            if texts:
                                grouped[heading_name] = [{"name": heading_name, "ingredients": " ".join(texts)}]

            if grouped:
                result[tab_name] = grouped

    return result


def extract_menu_items(price_lists):
    """Extract menu items (name + description) from elementor-price-list <ul> elements."""
    items = []
    for ul in price_lists:
        for li in ul.find_all('li'):
            title_el = li.find('span', class_='elementor-price-list-title')
            desc_el = li.find('p', class_='elementor-price-list-description')

            name = title_el.get_text(strip=True) if title_el else None
            if not name:
                continue

            description = desc_el.get_text(strip=True) if desc_el else ""

            dietary = []
            full_text = f"{name} {description}".lower()
            if 'gf' in full_text.split() or 'gluten free' in full_text or 'gluten-free' in full_text:
                dietary.append("gluten-free")

            item = {"name": name}
            if description:
                item["ingredients"] = description
            if dietary:
                item["dietary restrictions"] = dietary

            items.append(item)
    return items


@sub_hours_blueprint.route('/sub_hours')
def get_sub_menu():
    sub_hours = get_sub_hours()

    # manually convert sub_hours to json, as jsonify hates special characters
    json_output = json.dumps(sub_hours, ensure_ascii=False, indent=4)
    return Response(json_output, mimetype='application/json')

def hours_to_datetime(time_range:str):
    # Handle the "Closed" case
    if time_range.strip().lower() == "closed":
        return None, None
    
    # Strip trailing asterisks and normalize the delimiter
    time_range = time_range.replace('*', '')
    time_range = time_range.replace('–', '-').replace(' ', '')
    
    # Split the input string into start and end time strings
    start_str, end_str = time_range.split('-')
    
    # Define the format for parsing the time strings
    time_format = "%I:%M%p"
    
    # Parse the start and end times into datetime objects
    start = datetime.strptime(start_str, time_format)
    end = datetime.strptime(end_str, time_format)
    
    return start, end

def get_sub_hours():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    r = requests.get("https://uvss.ca/thesub/", headers=headers)
    if r.status_code != 200:
        return jsonify({"error": "Failed to retrieve page"}), 500

    soup = BeautifulSoup(r.content, 'html.parser')
    
    sub_hours = {
    'Monday': {},
    'Tuesday': {},
    'Wednesday': {},
    'Thursday': {},
    'Friday': {},
    'Saturday': {},
    'Sunday': {}
    }

    bean_there_info = bean_there(soup)
    fels_info = fels(soup)
    the_grill_info = the_grill(soup)
    munchie_bar_info = munchie_bar(soup)
    health_food_bar_info = health_food_bar(soup)

    def update_sub_hours(days, name, hours):
        for day in days:
            start_time,end_time = hours_to_datetime(hours)
            if start_time == None:
                sub_hours[day][name] = {"Building":"The Sub",
                                        "isClosed":True,
                                        "rawHours":[{"start":None,
                                                    "end":None}],
                                        "displayHours":"Closed :)"}
            else:
                sub_hours[day][name] = {"Building":"The Sub",
                                        "isClosed":False,
                                        "rawHours":[{"start":f"{start_time.strftime('%I:%M %p')}",
                                                    "end":f"{end_time.strftime('%I:%M %p')}"}],
                                        "displayHours":f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"}
    
    for d in [bean_there_info, fels_info, the_grill_info, munchie_bar_info, health_food_bar_info]:
        for key, value in d.items():
            name = list(value.keys())[0]
            hours = list(value.values())[0]
            if 'Monday-Friday' in key:
                update_sub_hours(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], name, hours)
            elif 'Monday – Wednesday' in key:
                update_sub_hours(['Monday', 'Tuesday', 'Wednesday'], name, hours)
            elif 'Thursday & Friday' in key:
                update_sub_hours(['Thursday', 'Friday'], name, hours)
            elif 'Saturday & Sunday' in key:
                update_sub_hours(['Saturday', 'Sunday'], name, hours)
            elif 'Monday – Friday' in key:
                update_sub_hours(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], name, hours)

    return sub_hours

def bean_there(soup):
    """Parse the REGULAR HOURS for Bean There from the UVSS page."""
    # Initialize the dictionary
    bean_there_dict = {}
    
    # Find the section
    section = soup.find('div', class_='av-qz5xcuq-6b53e4556030f8b34efd6922e6eec393')
    
    # Check if the section exists
    if not section:
        print("Section not found.")
        return bean_there_dict
    
    # Extract the name (from the <h4> tag)
    name_tag = section.find('h4')
    if not name_tag:
        print("Name not found.")
        return bean_there_dict
    name = name_tag.get_text(strip=True)
    
    # Extract the days and hours (from <strong> and its next sibling)
    days_tag = section.find('strong')
    if not days_tag:
        print("Days not found.")
        return bean_there_dict
    days = days_tag.get_text(strip=True)
    
    # Use next_sibling, because hours are not stored in an easily grabbable tag
    hours = days_tag.next_sibling
    if not hours or (hasattr(hours, 'strip') and not hours.strip()):
        print("Hours not found.")
        return bean_there_dict
    
    if hasattr(hours, 'strip'):
        hours = hours.strip()
        
    days_add_weekend = [days,"Saturday & Sunday"]
    # Add the name and hours to the dictionary
    bean_there_dict[days_add_weekend[0]] = {name: hours}
    bean_there_dict[days_add_weekend[1]] = {name: "Closed"}
    
    return bean_there_dict

def fels(soup):
    """Parse the REGULAR HOURS for Felicitias from the UVSS page."""
    # Initialize the dict
    fels_hours = {}
    
    # Find the section
    section = soup.find('div', class_='av-lbo57w2-e12dc9c96d1fe83d80727fde07c33c51')
    
    # Check if the section exists
    if not section:
        print("Section not found.")
        return fels_hours
    
    # Extract the name (from the <h4> tag)
    name_tag = section.find('h4')
    if not name_tag:
        print("Name not found.")
        return fels_hours
    name = name_tag.get_text(strip=True)
    
    # Extract the days and hours (from <strong> and its next sibling)
    days_tag = section.find_all('strong')
    if not days_tag:
        print("Days not found.")
        return fels_hours
    
    # Save days and hours into lists, due to varying hours on certain days
    days = []
    hours = []
    for day in days_tag:
        days.append(day.get_text(strip=True))

        # Use next_sibling, because hours are not stored in an easily grabbable tag
        hour_text = day.next_sibling
        if hour_text and hasattr(hour_text, 'strip') and hour_text.strip():  # Check if the next sibling exists and has non-whitespace text
            hours.append(hour_text.strip())
        else:
            hours.append(None)
    
    
    # Add the name and hours to the dictionary
    for i in range(len(days)):
        if i < len(hours) and hours[i]:
            fels_hours[days[i]] = {name: hours[i]}

    return fels_hours

def the_grill(soup):
    """Parse the REGULAR HOURS for the Grill from the UVSS page."""
    # Initialize the dictionary
    the_grill_dict = {}
    
    # Find the section
    section = soup.find('div', class_='av-imdz45u-d92256a0f5db5bc1f1672ca1a89032cd')
    
    # Check if the section exists
    if not section:
        print("Section not found.")
        return the_grill_dict
    
    # Extract the name (from the <h4> tag)
    name_tag = section.find('h4')
    if not name_tag:
        print("Name not found.")
        return the_grill_dict
    name = name_tag.get_text(strip=True)
    
    # Extract the days and hours (from <strong> and its next sibling)
    days_tag = section.find('strong')
    if not days_tag:
        print("Days not found.")
        return the_grill_dict
    days = days_tag.get_text(strip=True)
    
    # Use next_sibling, because hours are not stored in an easily grabbable tag
    hours = days_tag.next_sibling
    if not hours or (hasattr(hours, 'strip') and not hours.strip()):
        print("Hours not found.")
        return the_grill_dict
        
    if hasattr(hours, 'strip'):
        hours = hours.strip()
    
    days_add_weekend = [days,"Saturday & Sunday"]
    # Add the name and hours to the dictionary
    the_grill_dict[days_add_weekend[0]] = {name: hours}
    the_grill_dict[days_add_weekend[1]] = {name: "Closed"}
    
    return the_grill_dict

def munchie_bar(soup):
    """Parse the REGULAR HOURS for the Munchie Bar from the UVSS page."""
    # Initialize the dict
    munchie_bar_hours = {}
    
    # Find the section
    section = soup.find('div', class_='av-h5xe04y-f24dc4a439427ce2811acc31f45959e7')
    
    # Check if the section exists
    if not section:
        print("Section not found.")
        return munchie_bar_hours
    
    # Extract the name (from the <h4> tag)
    name_tag = section.find('h4')
    if not name_tag:
        print("Name not found.")
        return munchie_bar_hours
    name = name_tag.get_text(strip=True)
    
    # Extract the days and hours (from <strong> and its next sibling)
    days_tag = section.find_all('strong')
    if not days_tag:
        print("Days not found.")
        return munchie_bar_hours
    
    days = []
    hours = []
    for day in days_tag:
        days.append(day.get_text(strip=True))
        '''
        This part is wack due to weird html on the uvss website
        for some reason they have "monday -" and "friday:"
        split across 2 strong tags, so in order to save all of the
        hours, it needs to skip the 'friday:'
        '''
        if getattr(day.next_sibling, 'name', None) != 'strong':
            hour_text = day.next_sibling
        else:
            hour_text = day.next_sibling.next_sibling

        if hour_text and hasattr(hour_text, 'get_text'):
            txt = hour_text.get_text(strip=True)
        elif hour_text and isinstance(hour_text, str):
            txt = hour_text.strip()
        else:
            txt = None

        if txt:
            hours.append(txt)
        else:
            hours.append(None)            
    # fixing werid html
    '''
    for some reason they have "monday -" and "friday:"
    split across 2 strong tags, this is just code to fix
    it so the info is correct
    '''
    fixed_day = days[0] + " " + days[1]
    days[1] = days[2]
    days[0] = fixed_day

    hours[1] = hours[2]
    
    # Add the name and hours to the dictionary
    munchie_bar_hours[days[0]] = {name: hours[0]}
    munchie_bar_hours[days[1]] = {name: hours[1]}
    
    return munchie_bar_hours

def health_food_bar(soup):
    """Parse the REGULAR HOURS for the Health Food Bar from the UVSS page."""
    # Initialize the dictionary
    hfb_dict = {}
    
    # Find the section
    section = soup.find('div', class_='av-1l6ow9e-2e42d03d912da35333f77a2547518cf6')
    
    # Check if the section exists
    if not section:
        print("Section not found.")
        return hfb_dict
    
    # Extract the name (from the <h4> tag)
    name_tag = section.find('h4')
    if not name_tag:
        print("Name not found.")
        return hfb_dict
    name = name_tag.get_text(strip=True)
    
    # Extract the days and hours (from <strong> and its next sibling)
    days_tag = section.find('strong')
    if not days_tag:
        print("Days not found.")
        return hfb_dict
    days = days_tag.get_text(strip=True)
    
    hours = days_tag.next_sibling
    if not hours or (hasattr(hours, 'strip') and not hours.strip()):
        print("Hours not found.")
        return hfb_dict
        
    if hasattr(hours, 'strip'):
        hours = hours.strip()
        
    days_add_weekend = [days,"Saturday & Sunday"]
    # Add the name and hours to the dictionary
    hfb_dict[days_add_weekend[0]] = {name: hours}
    hfb_dict[days_add_weekend[1]] = {name: "Closed"}
    
    return hfb_dict

if __name__ == '__main__':
    app.run(debug=True)
