import json
from datetime import datetime, date

class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle datetime objects.
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)
