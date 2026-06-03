# from bs4 import BeautifulSoup
# from flask import Flask, render_template, jsonify
# import requests


from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, time, timedelta
from flask import Blueprint
# from flask_cors import CORS
import json
from .datetimeencoder import DateTimeEncoder
import calendar
import logging
from collections import OrderedDict


food_outlets_blueprint = Blueprint('food_outlets', __name__)
app = Flask(__name__)




@food_outlets_blueprint.route('/food_outlets')
def return_food_outlets():
    food_outlets = get_food_outlets()

    json_output = json.dumps(food_outlets, ensure_ascii=False, indent=4, cls=DateTimeEncoder)
    return Response(json_output, mimetype='application/json')

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

@food_outlets_blueprint.route('/food_outlets_with_buildings')
def add_names_of_food_outlets():
    response = get_food_outlets()
    json_dict = response.get_json()

    # Define mapping of food outlets to the building names
    building_mapping = {
        "The Cove": "Cove",
        "Mystic Market": "Farquhar Auditorium",
        "Mac's": "MacLaurin",
        "Bibliocafe": "McPherson Library",
        "Arts Place": "Fine Art's Building",
        "Nibbles & Bytes": "Engineering Lab Wing",
        "Sci Cafe": "Bob Wright Center"
    }

    for day, outlets in json_dict.items():
        current_building = None  # Keep track of the most recent building found

        for outlet_name in outlets.keys():  # Iterate in insertion order
            if outlet_name in building_mapping:
                current_building = building_mapping[outlet_name]  # Update building name

            if current_building:
                outlets[outlet_name] = {"Building": current_building, **outlets[outlet_name]}

    return json_dict






# example usage 
# /api/currently_open?time=14:20&day=monday
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
        # ALSO GET DAY OF MONTH OR JUST MONTH
        
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


        # Map day to schedule block
        if day in ['Saturday', 'Sunday']:
            schedule_block = 'Saturday - Sunday'
        elif day == 'Friday':
            schedule_block = 'Friday'
        else:
            schedule_block = 'Monday - Thursday'

        determine_date(food_outlets, )  
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

def parse(soup):
    """Parse the REGULAR HOURS for the food outlets from the UVic Food Services page."""
    food_outlets = {}
    
    # Find all accordion sections
    accordions = soup.find_all('div', class_='accordions')
    
    for section in accordions:
        headers = section.find_all('h3')
        for header in headers:
            # Get the header text (e.g., "Monday - Thursday")
            header_name = header.get_text(strip=True)
            if not header_name:
                continue
                
            # Initialize dictionary for this time period
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

# currently not used
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

    shortened_month = current_date.strftime('%b')
    day_of_week = current_date.strftime('%A')
    day_of_month = int(current_date.strftime('%d'))

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
