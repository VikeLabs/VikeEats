# from bs4 import BeautifulSoup
# from flask import Flask, render_template, jsonify
# import requests
# import json

import re
from collections import OrderedDict


from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Blueprint
from datetime import datetime
import copy
# from flask_cors import CORS

food_outlets_blueprint = Blueprint('food_outlets', __name__)
app = Flask(__name__)

# @app.route('/')
# def index():
#     return "Hello World"
#     # return render_template('index.html')

@food_outlets_blueprint.route('/food_outlets')
def get_food_outlets():
    r = requests.get("https://www.uvic.ca/services/food/where/index.php")
    if r.status_code != 200:
        return jsonify({"error": "Failed to retrieve page"}), 500

    soup = BeautifulSoup(r.content, 'html.parser')
    food_outlets = parse(soup)
    key_var = 'Monday - Thursday'
    key_var = 'Tuesday, July 2 - Wednesday, July 31'
    # date_adusted_list = is_within_date_range(key_var, food_outlets)

    # ordered_list_of_pairs = [{"key": k, "value": v} for k, v in date_adusted_list.items()]
    # ordered_list_of_pairs = [[key, value] for key, value in date_adusted_list.items()]

    return jsonify(food_outlets)
    # return jsonify(ordered_list_of_pairs)

def clean_text(tag):
    #NEXT TO DO Made header in <strong> tag and it time a header for the sub outlets in the another json section
    text_list = (tag.stripped_strings)
    text_list = [text.replace('\u00a0', ' ') for text in text_list]
    return text_list

def clean_time_format(time_string):
    pass
    # Regex to find the gap between the time and the am/pm part
    # pattern = re.compile(r'(?<=\d{1,2}[: ]?\d{0,2})\s(?=am|pm)')
    # # Substitute the space with an empty string to remove it
    # corrected_time_string = re.sub(pattern, '', time_string)
    # return corrected_time_string

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
        print(len(headers))
        for header in headers:
            header_name = str(header.get_text().strip())
            food_outlets[header_name] = {}
            print(f"header_name: ({header_name})")
            tables = section.find_all('table')
            print("number of tables: ", len(tables))
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) == 2:
                        
                        #splits the outlet names and hours into a list of strings
                        # outlet_name = cols[0].get_text(separator="\n", strip=True)
                        # outlet_name = outlet_name.split('\n')
                        
                        # hours = cols[1].get_text(separator="\n", strip=True)
                        # hours = hours.split('\n')
                        
                        outlet_name = clean_text(cols[0])
                        # outlet_name = outlet_name.split('\n')
                        # print(f"outlet_name {outlet_name}")
                        
                        hours = clean_text(cols[1])
                        # hours = 
                        # print(f"hours {hours}")
                        # hours = hours.split('\n')


                        

                        food_outlets[header_name].update(dict(zip(outlet_name, hours))) #adds the outlet name and hours to the dictionary
                        # print(f"food_outlets: {food_outlets}")

    #process hours into date time objects
    time_ranges = copy.deepcopy(food_outlets)
    for day_range in food_outlets:
        for outlet, time_range in food_outlets[day_range].items():
            time_ranges[day_range][outlet] = turn_to_datetime(time_range)
            print(f"food_outlets: {outlet}: {time_ranges[day_range][outlet]}")
    print("SUCCESS\n\n")

    # parsed_outlets = {}
    # for day_range, outlets in food_outlets.items():
    #     parsed_outlets[day_range] = {}
    #     for outlet, hours in outlets.items():
    #         parsed_outlets[day_range][outlet] = turn_to_datetime(hours)

    return food_outlets



#currently doesnt work quite right
def turn_to_datetime(time_range):
    # print("about to error on time_range: ", time_range)
    # Split by comma to handle multiple ranges
    if time_range == "Closed":
        return None
    range_groups = time_range.split(',')  # e.g., "11am-2pm, 5pm-10-pm" -> ["11am-2pm", "5pm-10-pm"]
    all_ranges = []

    for group in range_groups:
        ranges = group.strip().split('-')
        
        # Merge improperly split parts like "10" and "pm" in "10-pm"
        normalized_ranges = []
        i = 0
        while i < len(ranges):
            if i + 1 < len(ranges) and (ranges[i+1].strip().upper() in ["AM", "PM"] or ranges[i+1].strip().endswith(("AM", "PM"))):
                normalized_ranges.append(ranges[i] + ranges[i+1])
                i += 2
            else:
                normalized_ranges.append(ranges[i])
                i += 1
        
        if len(normalized_ranges) != 2:
            raise ValueError(f"Invalid time range format: {group}")
        
        processed_range = []
        for time in normalized_ranges:
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

        all_ranges.append(tuple(processed_range))

    return all_ranges  # Returns a list of time tuples


def is_within_date_range(current_date, food_outlets):
    # Example date range format: "June 1 - June 30"
    print(food_outlets)
    pass


def determine_date():
    pass
    #given a list of datetime objects, determine which list is the current day


if __name__ == '__main__':
    app.run(debug=True)
