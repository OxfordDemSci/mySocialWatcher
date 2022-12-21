import os
from flask import request, current_app, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mysocialwatcher.api import app, endpoints
from dotenv import load_dotenv

load_dotenv()
limiter_host = os.environ.get('LIMITER_HOST')

if not limiter_host:
    limiter_host = 'datahub_limiter'

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


@app.route('/social_media_audience/query', methods=['GET','POST'])
@app.route('/query', methods=['GET','POST'])
def query():
    """API endpoint to select data from the 'social_media_audience' database."""
    args = dict(request.args)
    if len(args) == 0:
        return "<h1>400 Error</h1><p>Bad Request: This API endpoint requires arguments. " \
               "See <a href='./../'>API documentation</a> for more information.", \
               400
    else:
        result = endpoints.query_fun(args)
        return jsonify(result), result.get("status")


@app.route('/social_media_audience/write', methods=['GET','POST'])
@app.route('/write', methods=['GET', 'POST'])
@limiter.exempt()
def write():
    """API endpoint to insert data into the 'social_media_audience' database."""
    args = dict(request.args)
    if len(args) == 0:
        return "<h1>400 Error</h1><p>Bad Request: This API endpoint requires arguments. " \
               "See <a href='./../'>API documentation</a> for more information.", \
               400
    else:
        result = endpoints.write_fun(args)
        return jsonify(result), result.get("status")


@app.route('/social_media_audience/list_collections', methods=['GET','POST'])
@app.route('/list_collections', methods=['GET','POST'])
def collections():
    """API endpoint to query a complete list of collection names."""
    args = dict(request.args)
    if len(args) == 0:
        return "<h1>400 Error</h1><p>Bad Request: This API endpoint requires arguments. " \
               "See <a href='./../'>API documentation</a> for more information.", \
               400
    else:
        result = endpoints.collections_fun(args)
        return jsonify(result), result.get("status")


@app.route('/social_media_audience/monitor_collections', methods=['GET','POST'])
@app.route('/monitor_collections', methods=['GET','POST'])
def monitor_collections():
    """API endpoint to monitor collections."""
    args = dict(request.args)
    if len(args) == 0:
        return "<h1>400 Error</h1><p>Bad Request: This API endpoint requires arguments. " \
               "See <a href='./../'>API documentation</a> for more information.", \
               400
    else:
        result = endpoints.monitor_fun(args)
        return jsonify(result), result.get("status")
