import sqlalchemy.exc
from mysocialwatcher.api.utils import *


def query_fun(args):
    """Process requests to API endpoint '/api/v1/social_media_audience/query' by selecting queried data from a PostgreSQL table.
    Args:
        args (dict): Arguments of GET request passed from request.args
    Examples:
        - args = {'platform': 'facebook', 'country': 'AT', 'date_start': '2022-10-01'}
    Returns:
        dict: http response compatible with json format
    """

    # default valid = True
    if 'valid' not in args.keys():
        args['valid'] = True

    # check arguments
    result = check_args(args,
                        required=['token', 'platform'],
                        required_oneof=[],
                        optional=['valid', 'country', 'contributor_id', 'collection', 'date_start', 'date_end',
                                  'gender', 'age_min', 'age_max'])
    args = result.get('args')
    status = result.get('status')
    message = result.get('message')
    data = None

    if status == 200:

        # connect to database
        conn = conn_to_database()

        # validate token
        result = validate_token(token=args.get('token'), conn=conn)

        status = result.get('status')
        if status == 200:
            contributor_id = result.get('contributor_id')
            args.pop('token')
        else:
            message = result.get('message')

    if status == 200:

        # list query columns
        cols = ['collection_id', 'contributor_id', 'contributed_on', 'collection_date', 'timestamp',
                'country', 'gender', 'age_min', 'age_max',
                'dau',  'mau', 'mau_lower', 'mau_upper',
                'geo_locations', 'all_fields', 'targeting', 'response']

        # cast dates to text
        cast_cols = ['contributed_on', 'collection_date']
        for i in range(len(cols)):
            if cols[i] in cast_cols:
                cols[i] = cols[i] + '::text'

        # table name
        table = args.get('table')
        args.pop('table')

        # ----  create sql query ---- #

        # select: from table
        sql = "SELECT " + ",".join(cols) + f" FROM {table} WHERE "

        # where: arguments
        for i in set(args.keys()).intersection(['country', 'gender', 'age_min', 'age_max']):
            sql +=  f"{i} = {str(args.get(i))} AND "

        # where: date range
        if 'date_start' in args.keys():
            sql += f"collection_date >= {str(args.get('date_start'))} AND "
        if 'date_end' in args.keys():
            sql += f"collection_date <= {str(args.get('date_end'))} AND "

        # where: collection_id from collection name
        if 'collection' in args.keys():
            sql += f"collection_id = (SELECT id FROM collections WHERE name = {args.get('collection')}) AND "

        # where: access permissions for collaborators' data or entire collections
        sql += "(" + \
               f"collection_id IN (SELECT UNNEST(collections) FROM contributors WHERE id={contributor_id}) OR " \
               f"contributor_id IN (SELECT UNNEST(collaborators) FROM contributors WHERE id={contributor_id})" + \
               ");"

        #---- query database ----#
        try:
            data = pd.read_sql(sql, conn)
            data = data.to_json()
            message = 'OK: Data successfully selected from database.'

        except Exception as e:
            exc = e.__dict__
            status = exc.get('code')
            message = exc.get('orig')

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
    if 'valid' not in args.keys():
        args['valid'] = False

    # check arguments
    result = check_args(args,
                        required=['token', 'platform', 'timestamp', 'geo_locations', 'gender', 'age_min', 'dau'],
                        required_oneof=['mau', 'mau_lower', 'mau_upper'],
                        optional=['valid', 'country', 'collection', 'age_max', 'all_fields', 'targeting', 'response'])
    args = result.get('args')
    status = result.get('status')
    message = result.get('message')

    if status == 200:

        # connect to database
        conn = conn_to_database()

        # validate token
        result = validate_token(token=args.get('token'), conn=conn, write_access=True)

        status = result.get('status')
        if status == 200:
            args['contributor_id'] = result.get('contributor_id')
            args.pop('token')
        else:
            message = result.get('message')

    # process request
    if status == 200:

        # collection id
        if 'collection' in args.keys():
            collection_name = args.pop('collection')
            collection_id = register_collection(collection_name, conn)
            if isinstance(collection_id, int):
                args['collection_id'] = collection_id

        # reformat timestamp
        dt_obj = datetime.datetime.fromtimestamp(int(args.get('timestamp')))
        args['collection_date'] = "'" + dt_obj.strftime('%Y-%m-%d') + "'"
        # args['timestamp_iso'] = "'" + dt_obj.isoformat(sep=" ")[:-3] + "'"

        # table name
        table = args.pop('table')

        # create sql query
        sql = "INSERT INTO " + table + "({}) VALUES({});".format(','.join(args.keys()), ','.join([str(i) for i in args.values()]))

        # query database
        try:
            result = conn.execute(sql)
            message = 'OK: Data successfully written into database.'

        except sqlalchemy.exc.SQLAlchemyError as e:
            # exc = e
            if isinstance(e, sqlalchemy.exc.IntegrityError) and isinstance(e.orig, psycopg2.errors.UniqueViolation):
                status = 409
                message = '(sqlalchemy code: ' + str(e.code) + ') Conflict: Data already in database with UNIQUE constraint. '
            else:
                status = e.code
                message = e._message()

        if status == 200 and 'invalid' in table:
            message += " Written with flag 'valid=false' so data will not persist in database."

    # return result
    return {"status": status, "message": message, "timestamp": timestr()}


def collections_fun():

    status = 200

    try:

        conn = conn_to_database()

        response = conn.execute('select id, name from collections;').fetchall()

        data = dict(response)

        message = 'OK: Collections successfully queried.'

    except sqlalchemy.exc.SQLAlchemyError as e:
        status = e.code
        message = e._message()

    return {'status': status, 'message': message, 'data': data, 'timestamp': timestr()}
