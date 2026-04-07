# from bs4 import BeautifulSoup
# from flask import Flask, render_template, jsonify
# import requests
# import json

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Blueprint
# from flask_cors import CORS

food_outlets_blueprint = Blueprint('food_outlets', __name__)
app = Flask(__name__)

# @app.route('/')
# def index():
#     return "Hello World"
#     # return render_template('index.html')

@food_outlets_blueprint.route('/food_outlets', methods=['GET'])
def get_food_outlets():
    try:
        food_outlets = get_food_outlets_dict()
        return jsonify(food_outlets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_food_outlets_dict():
    r = requests.get("https://www.uvic.ca/services/food/where/index.php")
    if r.status_code != 200:
        raise Exception("Failed to retrieve page")

    soup = BeautifulSoup(r.content, 'html.parser')
    food_outlets = parse(soup)
    return food_outlets

def clean_text(tag):
    #NEXT TO DO Made header in <strong> tag and it time a header for the sub outlets in the another json section
    text_list = (tag.stripped_strings)
    return text_list

def parse(soup):

    """Parse the REGULAR HOURS for the food outlets from the UVic Food Services page."""
    # Extract information
    # food_outlets = OrderedDict()
    food_outlets = dict()
    # food_outlets = OrderedDict(dict)
    sections = soup.find_all('div', class_='accordions')
    print(len(sections))
    # print(sections)

    
    for section in sections:
        headers = section.find_all('h3')
        for header in headers:
            header_name = str(header.get_text().strip())
            food_outlets[header_name] = {}
            tables = section.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) == 2:
                        outlet_names = clean_text(cols[0])
                        hours_texts = clean_text(cols[1])
                        
                        for name, hours_text in zip(outlet_names, hours_texts):
                            is_closed = "closed" in hours_text.lower()
                            raw_hours = []
                            if not is_closed:
                                try:
                                    # Simple parsing for now, could be improved
                                    parts = hours_text.split('-')
                                    if len(parts) == 2:
                                        # This is a very basic placeholder for rawHours parsing
                                        # since turn_to_datetime seems broken/incomplete
                                        raw_hours = [{"start": parts[0].strip(), "end": parts[1].strip()}]
                                except:
                                    pass
                            
                            food_outlets[header_name][name] = {
                                "isClosed": is_closed,
                                "displayHours": hours_text,
                                "rawHours": raw_hours
                            }

    return food_outlets

#currently doesnt work quite right
def turn_to_datetime(time_range):
    print("about to error on time_range: ", time_range)

    if time_range == "Closed": # Handle closed outlets
        return None
    
    # Split by comma to handle multiple ranges
    range_groups = time_range.split(',')  # e.g., "11am-2pm, 5pm-7:30pm" -> ["11am-2pm", "5pm-7:30pm"]
    all_ranges = []

    for group in range_groups:
        ranges = group.strip().split('-')  # Split each range on "-"
        if len(ranges) != 2:
            raise ValueError(f"Invalid time range format: {group}")
        
        processed_range = []
        for time in ranges:
            time = time.replace("\u00a0", "").strip().upper()  # Normalize and clean up
            time = time.replace(':AM', 'AM').replace(':PM', 'PM')  # Fix incorrect colon usage
            
            if not any(char in time for char in [':', 'AM', 'PM']):
                raise ValueError(f"Invalid time format: {time}")

            if ':' not in time:
                time = time[:-2] + ':00' + time[-2:]  # Add ':00' for missing minutes
            
            try:
                parsed_time = datetime.strptime(time, "%I:%M%p").time()
                processed_range.append(parsed_time)
            except ValueError:
                raise ValueError(f"Invalid time format: {time}")

    for key in food_outlets:
        if key == day_of_week:
            return {key: food_outlets[key]}
        else:
            try:
                key_list = key.split(" - ")
                lower_index = days.index(key_list[0])
                higher_index = days.index(key_list[1])
                today_index = days.index(day_of_week)
                if today_index >= lower_index and today_index <= higher_index:
                    return {key: food_outlets[key]}
            except:
                pass


def is_within_date_range(current_date, food_outlets):
    # Example date range format: "June 1 - June 30"
    print(food_outlets)
    return None
    return food_outlets[current_date]
    try:
        start_date_str, end_date_str = date_range_text.split('-')
        start_date = datetime.strptime(start_date_str.strip(), "%B %d")
        end_date = datetime.strptime(end_date_str.strip(), "%B %d")

        # Handle year for comparison
        start_date = start_date.replace(year=current_date.year)
        end_date = end_date.replace(year=current_date.year)

        return start_date <= current_date <= end_date
    except ValueError:
        return False

if __name__ == '__main__':
    app.run(debug=True)
