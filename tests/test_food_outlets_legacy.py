import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.food_outlets import get_food_outlets
import json
from api.datetimeencoder import DateTimeEncoder

try:
    data = get_food_outlets()
    print(json.dumps(data, indent=2, cls=DateTimeEncoder))
except Exception as e:
    print(f"Error: {e}")
