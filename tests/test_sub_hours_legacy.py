import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.sub_hours import get_sub_hours
import json

try:
    data = get_sub_hours()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
