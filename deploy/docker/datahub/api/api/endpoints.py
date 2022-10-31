import datetime
import json
import pandas as pd
from ast import literal_eval
from .utils import timestr, conn_to_database
from dotenv import load_dotenv
load_dotenv()


def check_args(args, required=[], required_oneof=[], optional=[]):
    """Check arguments of GET request
    Args:
        args (dict): Arguments of GET request
        required (list): Names of required arguments
        required_oneof (list): Names of required arguments for which at least one is required
        optional (list): Names of optional arguments
    Returns:
        dict: http response compatible with json format along with modified args object
    """

    # argument lists
    # unlisted arguments: token
    required_globally = ['valid']

    integer_args = ['contributor_id', 'timestamp', 'geo_id', 'gender', 'age_min', 'age_max',
                    'dau', 'mau', 'mau_lower', 'mau_upper']
    json_args = ['geo_locations', 'all_fields', 'targeting', 'response']
    boolean_args = ['valid']
    date_args = ['date_start', 'date_end']
    quote_args = ['country'] + json_args + date_args

    platforms_allowed = ['facebook', 'instagram']

    # initialize response
    status = 200
    message = ""

    # remove unused arguments
    args = {key: value for key, value in args.items() if key in required + required_oneof + optional}

    # run checks
    for i in required_globally:
        if not i in required: required.append(i)
    if not all(i in args.keys() for i in required):
        status = 400
        message = "Bad Request: All of these arguments are required {}.".format(required)
    elif len(required_oneof) > 0 and not any(i in args.keys() for i in required_oneof):
        status = 400
        message = "Bad Request: At least one of these arguments are required {}.".format(required_oneof)
    elif not args.get('platform').lower() in platforms_allowed:
        status = 400
        message = "Bad Request: 'platform' must be one of {}.".format(platforms_allowed)
    elif 'country' in args.keys() and (not isinstance(args.get('country'), str) or len(args.get('country')) != 2):
            status = 400
            message = "Bad Request: 'country' must be a string with length 2."
    elif not all(isinstance(args.get(i), int) for i in set(args.keys()).intersection(integer_args)):
        for i in set(args.keys()).intersection(integer_args):
            try:
                int(float(args.get(i)))
            except:
                status = 400
                message = "Bad Request: '{}' cannot be coerced to an integer.".format(i)
                break
    elif not all(isinstance(args.get(i), datetime.date) for i in set(args.keys()).intersection(date_args)):
        for i in set(args.keys()).intersection(date_args):
            try:
                datetime.datetime.strptime(args.get(i), '%Y-%m-%d')
            except:
                status = 400
                message = "Bad Request: '{}' cannot be coerced to a date of format YYYY-MM-DD.".format(i)
                break
    elif 'gender' in args.keys() and not args.get('gender') in [0, 1, 2]:
        status = 400
        message = "Bad Request: 'gender' must be one of [0, 1, 2]."

    # check json
    if status == 200:
        for i in set(args.keys()).intersection(json_args):
            try:
                x = args.get(i).replace("'", '"')
                json.loads(x)
                args[i] = x
            except:
                status = 400
                message = "Bad Request: '{}' is not a valid json.".format(i)
                break

    # compare country to geo_locations
    if status == 200 and 'geo_locations' in args.keys():
        geo_locations = literal_eval(args.get('geo_locations'))
        if geo_locations.get('name') == 'countries':
            if len(geo_locations.get('values')) > 1:
                status = 400
                message = "Bad request: Each record may only contain data for a single geography (i.e. country)."
            elif not geo_locations.get('values')[0] == args.get('country'):
                args['country'] = geo_locations.get('values')[0]
                message += " Redefined 'country' using 'geo_locations' due to mismatch."
        elif geo_locations.get('name') == 'regions':
            if len(geo_locations.get('values')) > 1:
                status = 400
                message = "Bad request: Each record may only contain data for a single geography (i.e. region)."
            elif not geo_locations.get('values')[0].get('country_code') == args.get('country'):
                args['country'] = geo_locations.get('values')[0].get('country_code')
                message += " Redefined 'country' using 'geo_locations' due to mismatch."
        elif args.get('country') in ['XX']:
            status = 400
            message = "Bad request: '{}' is not a valid country code.".format(args.get('country'))

    # check estimate_ready
    if status == 200 and 'response' in args.keys():

        if args.get('response')[:2] == "b\'":
            response = json.loads(literal_eval(args.get('response')).decode('utf-8'))
        else:
            response = json.loads(args.get('response'))

        if not response.get('data')[0].get('estimate_ready'):
            args['valid'] = False

    if status == 200:

        # strings to boolean
        for i in boolean_args:
            if not isinstance(args.get(i), bool):
                args[i] = str(args.get(i)).lower() in ['true', 't', 'yes', 'y', 'on', '1']

        # identify table
        args['table'] = args['platform']
        if not args['valid']:
            args['table'] = args['table'] + '_invalid'
        args.pop('valid')
        args.pop('platform')

        # quote strings
        for i in set(args.keys()).intersection(quote_args):
            args[i] = "'" + str(args[i].replace("'", '"')) + "'"

    return {'status': status, 'message': message, 'args': args}


def validate_token(token):
    conn = conn_to_database()
    cur = conn.cursor()
    sql_query = "SELECT id FROM contributors WHERE token='{}';".format(token)
    cur.execute(sql_query)
    response = cur.fetchall()
    authenticated = len(response) > 0

    if authenticated:
        contributor_id = str(response[0][0])
        status = 200
        message = 'OK: Token authenticated successfully.'
    else:
        status = 401
        message = "Unauthorized: Token failed authentication."
        contributor_id = None
    conn.close()
    return {'status': status, 'message': message, 'contributor_id': contributor_id}


def query_fun(args):
    """Process requests to API endpoint '/api/v1/social_media_audience/query' by selecting queried data from a PostgreSQL table.
    Args:
        args (dict): Arguments of GET request passed from request.args
    Returns:
        dict: http response compatible with json format
    """

    # default valid = True
    if not 'valid' in args.keys():
        args['valid'] = True

    # check arguments
    result = check_args(args,
                        required=['platform'],
                        required_oneof=[],
                        optional=['valid', 'country', 'contributor_id', 'gender', 'age_min', 'age_max', 'date_start', 'date_end'])
    args = result.get('args')
    status = result.get('status')
    message = result.get('message')
    data = None

    if status == 200:

        # list query columns
        cols = ['id', 'geo_id', 'contributor_id', 'contributed_on', 'country', 'geo_locations',
                'timestamp_iso', 'timestamp', 'gender', 'age_min', 'age_max',
                'dau',  'mau', 'mau_lower', 'mau_upper', 'all_fields', 'targeting', 'response']

        # cast dates to text
        cast_cols = ['contributed_on', 'timestamp_iso']
        for i in range(len(cols)):
            if cols[i] in cast_cols:
                cols[i] = cols[i] + '::text'

        # table name
        table = args.get('table')
        args.pop('table')

        # create sql query
        sql_query = "SELECT " + ','.join(cols) + " FROM " + table + " WHERE "
        for i in set(args.keys()).intersection(['contributor_id', 'platform', 'country', 'gender', 'age_min', 'age_max']):
            sql_query +=  i + '=' + str(args.get(i)) + ' AND '
        if 'date_start' in args.keys():
            sql_query += "timestamp_iso::date >= " + str(args.get('date_start')) + " AND "
        if 'date_end' in args.keys():
            sql_query += "timestamp_iso::date <= " + str(args.get('date_start')) + " AND "
        sql_query = sql_query[:-5] + ';'

        # query database
        try:
            conn = conn_to_database()
            data = pd.read_sql(sql_query, conn)

            data = data.to_json()
            message = 'OK: Data successfully selected from database.'
        except:
            status = 500
            message = 'Internal Server Error: Error returned from PostgreSQL server on SELECT.'
        conn.close()

    # return result
    return {"status": status, "message": message, "timestamp": timestr(), "data": data}


def write_fun(args):
    """Process requests to API endpoint '/api/v1/social_media_audience/write' by inserting them into a PostgreSQL table.
    Args:
        args (dict): Arguments of GET request passed from request.args
    Returns:
        dict: http response compatible with json format
    """

    # default valid = False
    if not 'valid' in args.keys():
        args['valid'] = False

    # check arguments
    result = check_args(args,
                        required=['token', 'platform', 'timestamp', 'country', 'geo_locations', 'gender'],
                        required_oneof=['dau', 'mau', 'mau_lower', 'mau_upper'],
                        optional=['valid', 'age_min', 'age_max', 'all_fields', 'targeting', 'response'])
    args = result.get('args')
    status = result.get('status')
    message = result.get('message')

    if status == 200:

        # validate token
        result = validate_token(token=args.get('token'))

        status = result.get('status')
        if status == 200:
            args['contributor_id'] = result.get('contributor_id')
            args.pop('token')
        else:
            message = result.get('message')

    # process request
    if status == 200:

        # reformat timestamp
        args['timestamp_iso'] = "'" + datetime.datetime.fromtimestamp(int(args.get('timestamp')), tz=datetime.timezone.utc).isoformat(sep=" ")[:-3] + "'"

        # table name
        table = args.get('table')
        args.pop('table')

        # create sql query
        sql_query = "INSERT INTO " + table + "({}) VALUES({});".format(','.join(args.keys()), ','.join([str(i) for i in args.values()]))

        # query database
        try:
            conn = conn_to_database()
            cur = conn.cursor()
            cur.execute(sql_query)
            conn.commit()
            message = 'OK: Data successfully written into database.'
        except:
            status = 500
            message = 'Internal Server Error: UNIQUE constraint or other error returned from PostgreSQL server on INSERT.'
        conn.close()

        if status == 200 and 'invalid' in table: message += " Written with flag 'valid=false' so data will not persist in database."

    # return result
    return {"status": status, "message": message, "timestamp": timestr()}


def write_geo(args):
    result = {"status": 404,
              "message": "Not Found: API endpoint 'write_geo' does not exist yet.",
              "timestamp": timestr()}
    return result
