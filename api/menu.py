from flask import Blueprint, jsonify, url_for
import requests
from bs4 import BeautifulSoup

# Create a blueprint for menus
menu_blueprint = Blueprint('menu', __name__)

@menu_blueprint.route('/menu')
def menu_home():
    # return url_for('menu.cove_menu'), url_for('menu.mystic_menu')
    return "Welcome to the menu page <br>" + "<br>Cove Menu: " + url_for('menu.cove_menu') + "<br>Mystic Menu: " + url_for('menu.mystic_menu')

@menu_blueprint.route('/menu/cove')
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

@menu_blueprint.route('/menu/mystic')
def mystic_menu():
    #TODO: Implement this function

    #get webpage and check its 200 ok

    #extract the menu items from the webpage

    #return the menu items as json

    #sample menu items feel free to delete

    menu_items = [
        {"name": "Mystic Burger", "price": 9.99, "category": "Main Course"},
        {"name": "Mystic Fries", "price": 3.99, "category": "Sides"},
        {"name": "Mystic Coke", "price": 1.99, "category": "Drinks"},
        {"name": "Mystic Salad", "price": 4.99, "category": "Appetizers"},
    ]
    return jsonify(menu_items)