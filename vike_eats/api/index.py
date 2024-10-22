import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import app

if __name__ == "__main__":
    app.run(port=5328, debug=True)
