# from bs4 import BeautifulSoup
# from flask import Flask, render_template, jsonify
# import requests


import re
from collections import OrderedDict


from flask import Flask, render_template, jsonify, current_app, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, time
from flask import Blueprint
import copy
import logging
# from flask_cors import CORS
import json
from .datetimeencoder import DateTimeEncoder
import calendar

food_outlets_blueprint = Blueprint('food_outlets', __name__)
app = Flask(__name__)

# @app.route('/')
# def index():
#     return "Hello World"
#     # return render_template('index.html')

# // Example frontend usage:
# fetch('/food_outlets')
#   .then(response => response.json())
#   .then(data => {
#     // Access formatted hours
#     console.log(data['Monday']['Cafe']['displayHours']); // "11:00 AM - 2:00 PM"
    
#     // Access raw hours for custom formatting
#     data['Monday']['Cafe']['rawHours'].forEach(range => {
#       console.log(`Opens: ${range.start}, Closes: ${range.end}`);
#     });
#   });

import logging

#RANDOM TESTING DELETE LATER
# @food_outlets_blueprint.route('/outlets')
# def get_all_outlets():
#     try:
#         r = requests.get("https://www.uvic.ca/services/food/where/index.php")
#         if r.status_code != 200:
#             return jsonify({"error": "Failed to retrieve page"}), 500

#         soup = BeautifulSoup(r.content, 'html.parser')
#         food_outlets = parse(soup)
#         formatted_outlets = format_outlet_hours(food_outlets)
        
#         # Debug logging
#         logging.debug(f"Formatted outlets before serialization: {formatted_outlets}")
        
#         # Use manual JSON encoding with custom encoder
#         json_str = json.dumps(formatted_outlets, cls=DateTimeEncoder)
#         return current_app.response_class(
#             response=json_str,
#             status=200,
#             mimetype='application/json'
#         )
#     except Exception as e:
#         logging.error(f"Error in get_food_outlets: {str(e)}")
#         return jsonify({"error": str(e)}), 500

@food_outlets_blueprint.route('/food_outlets')
def get_food_outlets():
    try:
        r = requests.get("https://www.uvic.ca/services/food/where/index.php")
        if r.status_code != 200:
            return jsonify({"error": "Failed to retrieve page"}), 500

        soup = BeautifulSoup(r.content, 'html.parser')
        food_outlets = parse(soup)
        is_date = determine_date(food_outlets)

        formatted_outlets = format_outlet_hours(food_outlets)
        # Debug logging
        logging.debug(f"Formatted outlets before serialization: {formatted_outlets}")
        
        # Use manual JSON encoding with custom encoder
        json_str = json.dumps(formatted_outlets, cls=DateTimeEncoder)
        return current_app.response_class(
            response=json_str,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logging.error(f"Error in get_food_outlets: {str(e)}")
        return jsonify({"error": str(e)}), 500


# needs fixing
# @food_outlets_blueprint.route('/currently_open')
# def get_currently_open():
#     r = requests.get("https://www.uvic.ca/services/food/where/index.php")
#     if r.status_code != 200:
#         return jsonify({"error": "Failed to retrieve page"}), 500

#     soup = BeautifulSoup(r.content, 'html.parser')
#     food_outlets = parse(soup)

#     #for now, pass with "friday" block
#     open_outlets = is_within_date_range(datetime.now().time(), food_outlets['Friday'])
#     return jsonify(open_outlets)


# split into multiple functions
@food_outlets_blueprint.route('/currently_open')
def get_currently_open():
    try:
        r = requests.get("https://www.uvic.ca/services/food/where/index.php")
        if r.status_code != 200:
            return jsonify({"error": "Failed to retrieve page"}), 500

        soup = BeautifulSoup(r.content, 'html.parser')
        food_outlets = parse(soup)
        formatted_outlets = format_outlet_hours(food_outlets)

        # Get current day and time
        # Get custom time from query parameter (format: HH:MM)
        custom_time = request.args.get('time', None)
        custom_day = request.args.get('day', None)
        
        if custom_time:
            try:
                hour, minute = map(int, custom_time.split(':'))
                current_time = time(hour, minute)
            except ValueError:
                return jsonify({"error": "Invalid time format. Use HH:MM"}), 400
        else:
            current_time = datetime.now().time()

        if custom_day:
            if custom_day.title() not in calendar.day_name:
                return jsonify({"error": "Invalid day. Use full day name"}), 400
            day = custom_day.title()
        else:
            day = calendar.day_name[datetime.now().weekday()]

        # now = datetime.now()
        # current_time = now.time()
        # day = calendar.day_name[now.weekday()]

        # Map day to schedule block
        if day in ['Saturday', 'Sunday']:
            schedule_block = 'Saturday - Sunday'
        elif day == 'Friday':
            schedule_block = 'Friday'
        else:
            schedule_block = 'Monday - Thursday'

        # Get outlets for current schedule block
        current_outlets = formatted_outlets.get(schedule_block, {})
        
        # Check which outlets are open
        open_outlets = {}
        for outlet, hours in current_outlets.items():
            if not hours['isClosed']:
                for time_range in hours['rawHours']:
                    if time_range['start'] <= current_time <= time_range['end']:
                        open_outlets[outlet] = {
                            'displayHours': hours['displayHours'],
                            'closes_at': time_range['end'].strftime("%I:%M %p")
                        }
                        break

        return jsonify({
            'timestamp': current_time.strftime("%I:%M %p"),
            'day': day,
            'open_outlets': open_outlets
        })

    except Exception as e:
        logging.error(f"Error in get_currently_open: {str(e)}")
        return jsonify({"error": str(e)}), 500        

def format_outlet_hours(food_outlets):
    formatted_outlets = {}
    
    for day_range, outlets in food_outlets.items():
        formatted_outlets[day_range] = {}
        
        for outlet_name, hours in outlets.items():
            if hours is None:  # Handle closed locations or invalid times
                formatted_outlets[day_range][outlet_name] = {
                    'isClosed': True,
                    'rawHours': None,
                    'displayHours': 'Closed'
                }
                continue
                
            try:
                # Format each time range
                formatted_ranges = []
                display_ranges = []
                
                for time_range in hours:
                    if not isinstance(time_range, tuple) or len(time_range) != 2:
                        print(f"Warning: Invalid time range format for {outlet_name}: {time_range}")
                        continue
                        
                    start_time, end_time = time_range
                    formatted_ranges.append({
                        'start': start_time,
                        'end': end_time
                    })
                    display_ranges.append(
                        f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
                    )
                
                if not formatted_ranges:  # If no valid ranges were found
                    formatted_outlets[day_range][outlet_name] = {
                        'isClosed': True,
                        'rawHours': None,
                        'displayHours': 'Hours unavailable'
                    }
                else:
                    formatted_outlets[day_range][outlet_name] = {
                        'isClosed': False,
                        'rawHours': formatted_ranges,
                        'displayHours': ', '.join(display_ranges)
                    }
            except Exception as e:
                print(f"Error processing hours for {outlet_name}: {str(e)}")
                formatted_outlets[day_range][outlet_name] = {
                    'isClosed': True,
                    'rawHours': None,
                    'displayHours': 'Error processing hours'
                }
    
    return formatted_outlets

# def clean_text_list(tag):
#     #NEXT TO DO Made header in <strong> tag and it time a header for the sub outlets in the another json section
#     text_list = (tag.stripped_strings)
#     text_list = [text.replace('\u00a0', ' ') for text in text_list]
#     # text_list = [text.replace('*', '') for text in text_list]
#     text_list = [text.strip() for text in text_list]
#     return text_list



def parse(soup):
    """Parse the REGULAR HOURS for the food outlets from the UVic Food Services page."""
    food_outlets = {}
    
    # Find all accordion sections
    accordions = soup.find_all('div', class_='accordions')
    
    for accordion in accordions:
        # Get all h3 headers (these are the main time periods like "Monday - Thursday")
        headers = accordion.find_all('h3')
        
        for header in headers:
            # Get the header text (e.g., "Monday - Thursday")
            header_name = header.get_text(strip=True)
            if not header_name:
                continue
                
            # Initialize dictionary for this time period
            food_outlets[header_name] = {}
            
            # Find the div that follows this header (contains the table)
            content_div = header.find_next_sibling('div')
            if not content_div:
                continue
                
            # Find all tables in this div
            tables = content_div.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) == 2:  # We expect two columns: outlet name and hours
                        # Get all text from both columns, preserving line breaks
                        outlet_names = [text.strip() for text in cols[0].stripped_strings]
                        hours = [text.strip() for text in cols[1].stripped_strings]
                        
                        # Remove empty strings and special characters
                        outlet_names = [name for name in outlet_names if name and name != '\xa0']
                        hours = [hour for hour in hours if hour and hour != '\xa0']
                        
                        # Pair each outlet with its corresponding hours
                        for outlet_name, hour in zip(outlet_names, hours):
                            # Skip if the outlet name is actually a header (starts with *)
                            if outlet_name.startswith('*'):
                                continue
                                
                            # Clean the outlet name and hours
                            clean_outlet = outlet_name.replace('\u00a0', ' ').strip()
                            clean_hours = hour.replace('\u00a0', ' ').strip()
                            
                            # Add to our dictionary
                            if clean_outlet:  # Only add if we have a valid outlet name
                                food_outlets[header_name][clean_outlet] = clean_hours
    #process hours into date time objects
    time_ranges = copy.deepcopy(food_outlets)
    for day_range in food_outlets:
        for outlet, time_range in food_outlets[day_range].items():
            print(f"Raw time range for {outlet}: {time_range}")  # Add this line
            time_ranges[day_range][outlet] = turn_to_datetime(time_range)
    return time_ranges

    return food_outlets
# def parse(soup):

#     """Parse the REGULAR HOURS for the food outlets from the UVic Food Services page."""

#     # Extract information
#     # food_outlets = dict()
#     food_outlets = {}
#     sections = soup.find_all('div', class_='accordions')

#     print(f"header_name: ({header_name})")
#     tables = section.find_all('table')
#     print("number of tables: ", len(tables))
#     for table in tables:
#         rows = table.find_all('tr')
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) == 2:
                
#                     # splits the outlet names and hours into a list of strings
#                     outlet_name = cols[0].get_text(separator="\n", strip=True)
#                     outlet_name = outlet_name.split('\n')
                    
#                     hours = cols[1].get_text(separator="\n", strip=True)
#                     hours = hours.split('\n')
                    
#                     outlet_list  = clean_text(cols[0])
#                     # outlet_name = outlet_name.split('\n')
#                     # print(f"outlet_name {outlet_name}")
                    
#                     hours_list  = clean_text(cols[1])

#                     print(f"outlet_list {outlet_list}")
#                     print(f"hours_list {hours_list}")

#                     for outlet, hours in zip(outlet_list, hours_list):
#                         food_outlets[header_name][outlet] = hours
                    
#                     food_outlets[header_name].update(dict(zip(outlet_list , hours_list ))) #adds the outlet name and hours to the dictionary
#                     print(f"food_outlets: {food_outlets}")
#     #process hours into date time objects
#     time_ranges = copy.deepcopy(food_outlets)
#     for day_range in food_outlets:
#         for outlet, time_range in food_outlets[day_range].items():
#             time_ranges[day_range][outlet] = turn_to_datetime(time_range)

    
#     return food_outlets


def turn_to_datetime(time_range):
    """
    Convert time range strings to datetime.time objects.
    
    Args:
        time_range (str): String representing time ranges (e.g., "11am-2pm" or "11:30am-2:30pm, 5pm-10pm")
        
    Returns:
        list of tuples: Each tuple contains (start_time, end_time) as datetime.time objects
        None: If the location is closed
    """
    # First check if it's closed - handle case-insensitive
    if isinstance(time_range, str) and time_range.lower().strip() == "closed":
        return None
        
    # Handle empty or None input
    if not time_range:
        return None
        
    try:
        # Clean up the input string
        time_range = ' '.join(time_range.split())  # Normalize spaces
        time_range = time_range.replace(',', ' ')  # Convert commas to spaces
        
        # Split into individual time ranges
        ranges = [r.strip() for r in time_range.split() if '-' in r]
        
        all_ranges = []
        for time_slot in ranges:
            # Split into start and end times
            start_str, end_str = time_slot.split('-')
                
            # Clean and standardize each time string
            times = []
            for time_str in [start_str, end_str]:
                # Remove whitespace and convert to uppercase
                time_str = time_str.strip().upper()
                
                # Add missing AM/PM based on context
                if not time_str.endswith(('AM', 'PM')):
                    # If end time doesn't have AM/PM, use the same period as start time
                    if 'AM' in start_str.upper():
                        time_str += 'AM'
                    elif 'PM' in start_str.upper():
                        time_str += 'PM'
                    else:
                        # Default to PM for times without AM/PM indicator
                        time_str += 'PM'
                
                # Add ':00' if no minutes specified
                if ':' not in time_str:
                    time_str = time_str.replace('AM', ':00AM').replace('PM', ':00PM')
                
                try:
                    parsed_time = datetime.strptime(time_str, "%I:%M%p").time()
                    times.append(parsed_time)
                except ValueError:
                    print(f"Warning: Could not parse time: {time_str}")
                    continue
            
            if len(times) == 2:  # Only add if we successfully parsed both times
                all_ranges.append(tuple(times))
        
        return all_ranges if all_ranges else None
        
    except Exception as e:
        print(f"Warning: Error processing time range '{time_range}': {str(e)}")
        return None

#currently doesnt work quite right
# def turn_to_datetime(time_range):
#     # print("about to error on time_range: ", time_range)
#     # Split by comma to handle multiple ranges
#     if time_range == "Closed":
#         return None
#     range_groups = time_range.split(',')  # e.g., "11am-2pm, 5pm-10-pm" -> ["11am-2pm", "5pm-10-pm"]
#     all_ranges = []

#     for group in range_groups:
#         ranges = group.strip().split('-')
        
#         # Merge improperly split parts like "10" and "pm" in "10-pm"
#         normalized_ranges = []
#         i = 0
#         while i < len(ranges):
#             if i + 1 < len(ranges) and (ranges[i+1].strip().upper() in ["AM", "PM"] or ranges[i+1].strip().endswith(("AM", "PM"))):
#                 normalized_ranges.append(ranges[i] + ranges[i+1])
#                 i += 2
#             else:
#                 normalized_ranges.append(ranges[i])
#                 i += 1
        
#         if len(normalized_ranges) != 2:
#             raise ValueError(f"Invalid time range format: {group}")
        
#         processed_range = []
#         for time in normalized_ranges:
#             time = time.replace("\u00a0", "").strip().upper()  # Normalize and clean up
#             time = time.replace(':AM', 'AM').replace(':PM', 'PM')  # Fix incorrect colon usage

#             if not any(char in time for char in [':', 'AM', 'PM']):
#                 raise ValueError(f"Invalid time format: {time}")

#             if ':' not in time:
#                 time = time[:-2] + ':00' + time[-2:]  # Add ':00' for missing minutes
            
#             try:
#                 parsed_time = datetime.strptime(time, "%I:%M%p").time()
#                 processed_range.append(parsed_time)
#             except ValueError:
#                 raise ValueError(f"Invalid time format: {time}")

#         all_ranges.append(tuple(processed_range))
        

#     return all_ranges  # Returns a list of time tuples


def is_within_date_range(current_date, food_outlets):
    open_outlets = {}

    #iterate through the dictionary
    for outlet in food_outlets:
        #convert to datetime object if not closed
        if food_outlets[outlet] != 'Closed':
            hours_range = turn_to_datetime(food_outlets[outlet])
            open_time = hours_range[0][0]
            close_time = hours_range[0][1]

            #append to dictionary if open
            if current_date >= open_time and current_date <= close_time:
                open_outlets[outlet] = food_outlets[outlet]
    
    return open_outlets


def determine_date(food_outlets):

    current_date = datetime.now()

    shortened_month = current_date.strftime('%b')
    day_of_week = current_date.strftime('%A')
    day_of_month = current_date.strftime('%d')

    for key in food_outlets:
        if re.match(f"^{day_of_week},* {shortened_month} {day_of_month}$", key):
            return {key: food_outlets[key]}
        else:
            key_list = key.split(" - ")
            try:
                upper_date = int(key_list[1].split(" ")[2])
                lower_date = int(key_list[0].split(" ")[2])
                menu_month = key_list[1].split(" ")[1]
                menu_day_week = key_list[1]
                if menu_month == shortened_month and day_of_month <= upper_date and day_of_month >= lower_date:
                    return {key: food_outlets[key]}
            except:
                pass
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for key in food_outlets:
        if key == day_of_week:
            return {key: food_outlets[key]}
        else:
            key_list = key.split(" - ")
            lower_index = days.index(key_list[0])
            higher_index = days.index(key_list[1])
            today_index = days.index(day_of_week)
            if today_index >= lower_index and today_index <= higher_index:
                return {key: food_outlets[key]}


    #given a list of datetime objects, determine which list is the current day


if __name__ == '__main__':
    app.run(debug=True)
