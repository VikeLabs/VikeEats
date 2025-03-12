import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, Blueprint, Response, jsonify
from datetime import datetime

sub_hours_blueprint = Blueprint('sub_hours', __name__)
app = Flask(__name__)

# @app.route('/')
# def index():
#     return "Hello World"
#     # return render_template('index.html')

@sub_hours_blueprint.route('/sub_hours')
def get_sub_menu():
    r = requests.get("https://uvss.ca/thesub/")
    if r.status_code != 200:
        return jsonify({"error": "Failed to retrieve page"}), 500

    soup = BeautifulSoup(r.content, 'html.parser')
    # intialize sub_hours dict
    sub_hours = {
    'Monday': {},
    'Tuesday': {},
    'Wednesday': {},
    'Thursday': {},
    'Friday': {},
    'Saturday': {},
    'Sunday': {}
    }

    # store scraped hours into dicts
    bean_there_info = bean_there(soup)
    fels_info = fels(soup)
    the_grill_info = the_grill(soup)
    munchie_bar_info = munchie_bar(soup)
    health_food_bar_info = health_food_bar(soup)

    # a function to quickly update sub_hours dict
    def update_sub_hours(days, name, hours):
        for day in days:
            start_time,end_time = hours_to_datetime(hours)
            if start_time == None:
                sub_hours[day][name] = {"isClosed":True,
                                        "rawHours":[{"start":None,
                                                    "end":None}],
                                        "displayHours":"Closed :)"}
            else:
                sub_hours[day][name] = {"isClosed":False,
                                        "rawHours":[{"start":f"{start_time.strftime('%I:%M %p')}",
                                                    "end":f"{end_time.strftime('%I:%M %p')}"}],
                                        "displayHours":f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"}
    
    def hours_to_datetime(time_range:str):
        # Handle the "Closed" case
        if time_range.strip().lower() == "closed":
            return None, None
        
        # Normalize the delimiter by replacing variations with a standard one
        time_range = time_range.replace('–', '-').replace(' ', '')
        
        # Split the input string into start and end time strings
        start_str, end_str = time_range.split('-')
        
        # Define the format for parsing the time strings
        time_format = "%I:%M%p"
        
        # Parse the start and end times into datetime objects
        start = datetime.strptime(start_str, time_format)
        end = datetime.strptime(end_str, time_format)
        
        return start, end


    # go through all of the individual dicts, and combine them into one, where the key is the
    # day of the week, and the value is the name and hours
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
    
    # manually convert sub_hours to json, as jsonify hates special characters
    json_output = json.dumps(sub_hours, ensure_ascii=False, indent=4)
    return Response(json_output, mimetype='application/json')


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
    if not hours or not hours.strip():
        print("Hours not found.")
        return bean_there_dict
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
        if hour_text and hour_text.strip():  # Check if the next sibling exists and has non-whitespace text
            hours.append(hour_text.strip())
        else:
            hours.append(None)
    
    
    # Add the name and hours to the dictionary
    fels_hours[days[0]] = {name: hours[0]}
    fels_hours[days[1]] = {name: hours[1]}
    fels_hours[days[2]] = {name: hours[2]}
    
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
    if not hours or not hours.strip():
        print("Hours not found.")
        return the_grill_dict
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
        if day.next_sibling.name != 'strong':
            hour_text = day.next_sibling
        else:
            hour_text = day.next_sibling.next_sibling
        if hour_text and hour_text.strip():  # Check if the next sibling exists and has non-whitespace text
            hours.append(hour_text.strip())
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
    if not hours or not hours.strip():
        print("Hours not found.")
        return hfb_dict
    hours = hours.strip()
    
    days_add_weekend = [days,"Saturday & Sunday"]
    # Add the name and hours to the dictionary
    hfb_dict[days_add_weekend[0]] = {name: hours}
    hfb_dict[days_add_weekend[1]] = {name: "Closed"}
    
    return hfb_dict

if __name__ == '__main__':
    app.run(debug=True)
