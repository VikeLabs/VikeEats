from flask import Flask, jsonify
from flask_cors import CORS

# Import your blueprints
from .food_outlets import food_outlets_blueprint
from .menu import menu_blueprint
from .datetimeencoder import DateTimeEncoder
import logging

logging.basicConfig(level=logging.DEBUG)

# Create and configure the app
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.json_encoder = DateTimeEncoder
    app.register_blueprint(food_outlets_blueprint, url_prefix='/api')
    app.register_blueprint(menu_blueprint, url_prefix='/api')
    return app

app = create_app()

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the Flask API"})


if __name__ == "__main__":
    app.run(port=5328, debug=True)
    