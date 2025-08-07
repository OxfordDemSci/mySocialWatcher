from flask import Flask
from flask_cors import CORS
import logging
import sys

# configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# initialise flask app
app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.logger.propagate = True  # ensure Flask logger uses the root handlers
app.logger.info("🚀 Flask app initialized with logging enabled")
from mysocialwatcher.api import routes


# Cross Origin Resource Sharing (for AJAX)
CORS(app)

# specify the Google Analytics key here
app.config["GA_KEY"] = ""

# don't sort JSON elements alphabetically
app.config["JSON_SORT_KEYS"] = False
