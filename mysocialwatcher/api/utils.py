import os
import json
import datetime
import pandas as pd
import sqlalchemy, psycopg2
from ast import literal_eval
from dotenv import load_dotenv

load_dotenv()
# load_dotenv('docker/datahub/dev.env')


def timestr():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0).isoformat(sep=" ")[:-3]


def db_engine(pw=os.environ.get('POSTGRES_WPASS'),
              host=os.environ.get('POSTGRES_HOST'),
              port=os.environ.get('POSTGRES_PORT'),
              db=os.environ.get('POSTGRES_DB')):

    engine_string = 'postgresql+psycopg2://writer:' + pw + '@' + host + ':' + port + '/' + db

    db = sqlalchemy.create_engine(engine_string, poolclass=sqlalchemy.pool.NullPool)

    return db


def validate_token(token, conn, write_access=False):

    sql = "SELECT contributor_id FROM tokens WHERE token='{}';".format(token)
    if write_access:
        sql = sql.replace(';', ' and write=True;')

    df = pd.read_sql(sql, conn)

    result = list(df['contributor_id'])
    authenticated = len(result) > 0

    if authenticated:
        contributor_id = str(result[0])
        status = 200
        message = 'OK: Token authenticated successfully.'
    else:
        status = 401
        message = "Unauthorized: Token failed authentication."
        contributor_id = None

    return {'status': status, 'message': message, 'contributor_id': contributor_id}


def register_collection(collection_name, conn):

    collection_name = collection_name.strip('_')
    sql = f"SELECT id FROM collections WHERE name = '{collection_name}';"
    df = pd.read_sql(sql, conn)

    if len(df['id']) == 0:
        sql = f"INSERT INTO collections(name) VALUES('{collection_name}') RETURNING id;"
        df = pd.read_sql(sql, conn)

    result = int(df['id'][0])
    return result


def countries_from_geo_locations(geo_locations):

    if geo_locations.get('name') == 'countries':
        result = geo_locations.get('values')

    else:
        result = []

        if 'pySocialWatcherReference' in geo_locations.keys():
            x = list(filter(lambda k: 'country:' in k,
                            geo_locations.get('pySocialWatcherReference').split('; ')))
            result += list(set([item.split(':')[1] for item in x]))

        for value in geo_locations.get('values'):
            country_keys = [k for k in value.keys()
                            if 'country' in k and
                            isinstance(value.get(k), str) and
                            len(value.get(k)) == 2]

            for country_key in list(set(country_keys)):
                result.append(value.get(country_key))

    return list(set(result))


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
    date_args = ['date_start', 'date_end', 'collection_date']
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

        countries = countries_from_geo_locations(geo_locations)
        if len(countries) == 0:
            status = 400
            message = "Bad request: iso-2 country code could not be determined from 'geo_locations' argument."
        elif len(countries) > 1:
            status = 400
            message = "Bad request: More than one iso-2 country code identified from 'geo_locations' argument."
        elif not args.get('country') == countries[0]:
            args['country'] = countries[0]
            message += " Redefined 'country' using 'geo_locations' due to mismatch."

        if status == 200 and args.get('country') in ['XX']:
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

        # collection name
        if 'collection' in args.keys():
            args['collection'] = args.get('collection').strip('_')

        # quote strings
        for i in set(args.keys()).intersection(quote_args):
            args[i] = "'" + str(args[i].replace("'", '"')) + "'"

    return {'status': status, 'message': message, 'args': args}
