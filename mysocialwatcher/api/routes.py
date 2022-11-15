import os
from flask import request, current_app, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mysocialwatcher.api import app, endpoints
from dotenv import load_dotenv

load_dotenv()
limiter_host = os.environ.get('LIMITER_HOST')

# define rate limiting
limiter = Limiter(app,
                  key_func=get_remote_address,
                  # application_limits=['60/minute', '1000/hour', '10000/day'],
                  default_limits=['60/minute', '1000/hour', '10000/day'],
                  strategy='fixed-window-elastic-expiry',
                  storage_uri="memcached://" + limiter_host + ":11211",
                  storage_options={}
                  )


@app.errorhandler(404)
def page_not_found(e):
    return f"<h1>404 Error</h1><p>The resource could not be found. {e}</p>", 404


@app.route('/')
def home():
    return current_app.send_static_file('docs.html')


@app.route('/social_media_audience/query', methods=['GET'])
@app.route('/query', methods=['GET'])
def fb_query():
    """API endpoint to select data from the 'social_media_audience' database."""
    args = dict(request.args)
    if len(args) == 0:
        return "<h1>400 Error</h1><p>Bad Request: This API endpoint requires arguments. " \
               "See <a href='./../'>API documentation</a> for more information.", \
               400
    else:
        result = endpoints.query_fun(args)
        return jsonify(result), result.get("status")


@app.route('/social_media_audience/write', methods=['GET'])
@app.route('/write', methods=['GET'])
@limiter.exempt()
def fb_write():
    """API endpoint to insert data into the 'social_media_audience' database."""
    args = dict(request.args)
    if len(args) == 0:
        return "<h1>400 Error</h1><p>Bad Request: This API endpoint requires arguments. " \
               "See <a href='./../'>API documentation</a> for more information.", \
               400
    else:
        result = endpoints.write_fun(args)
        return jsonify(result), result.get("status")


# @app.route('/social_media_audience/write_geo', methods=['GET'])
# @app.route('/write_geo', methods=['GET'])
# def fb_write_geo():
#     result = endpoints.write_geo_fun(dict(request.args))
#     return jsonify(result), result.get("status")
