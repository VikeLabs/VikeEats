from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify
import requests
import json
import re
from collections import OrderedDict


app = Flask(__name__, static_url_path='/static')

@app.route('/')
def extract():
    return render_template('index.html')

@app.route('/api/food_outlets')
def get_food_outlets():
    r = requests.get("https://www.uvic.ca/services/food/where/index.php")
    if r.status_code != 200:
        print("Failed to retrieve page")
        return
    
    soup = BeautifulSoup(r.content, 'html.parser')
    #print(soup.prettify())
    
    food_outlets = parse(soup)
    return jsonify(food_outlets)

def parse(soup):

    # Extract information
    food_outlets = OrderedDict()
    # Find the first hours_section
    regular_hours = soup.find_all('h3')[0]

    #print(regular_hours.text.strip()) #Test line to see the hours

    # Finds the links in each section
    # links = soup.find_all('a', href=True)
    # for link in links:
    #     print(link['href'])

    #attempting to filter by different accoridon panels
    #monday_thursday = links.find_all('a', href='#acc-monday---thursday')

    #getts a list of all the tables
    tables = regular_hours.find_all('table')
    
    #this overrides all previous attempts to get the tables but should be removed once the above is working
    tables = soup.find_all('table')
        
    #for each table in tables it will find all the rows and then all the columns in each row
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                
                #splits the outlet names and hours into a list of strings
                outlet_name = cols[0].get_text(separator="\n", strip=True)
                outlet_name = outlet_name.split('\n')
                
                hours = cols[1].get_text(separator="\n", strip=True)
                hours = hours.split('\n')
     
                food_outlets.update(dict(zip(outlet_name, hours))) #adds the outlet name and hours to the dictionary

    data_array = [[key, value] for key, value in food_outlets.items()]
    #print(data_array)
    return data_array


    

if __name__ == '__main__':
    app.run()
