import json
from datetime import datetime, time

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling datetime and time objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, time)):
            return obj.strftime("%I:%M %p")  # Returns format like "11:30 AM"
        return super().default(obj)