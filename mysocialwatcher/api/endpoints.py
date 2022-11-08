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
                        optional=['valid', 'contributor_id', 'collection', 'country', 'date_start', 'date_end',
                                  'gender', 'age_min', 'age_max'])
    args = result.get('args')
    status = result.get('status')
    message = result.get('message')
    data = None

    if status == 200:

        # validate token
        result = validate_token(token=args.get('token'))

        status = result.get('status')
        if status == 200:
            args['contributor_id'] = result.get('contributor_id')
            args.pop('token')
        else:
            message = result.get('message')

    if status == 200:

        # list query columns
        cols = ['id', 'collection', 'contributor_id', 'contributed_on', 'country', 'geo_locations',
                'date', 'timestamp', 'gender', 'age_min', 'age_max',
                'dau',  'mau', 'mau_lower', 'mau_upper', 'all_fields', 'targeting', 'response']

        # cast dates to text
        cast_cols = ['contributed_on', 'date']
        for i in range(len(cols)):
            if cols[i] in cast_cols:
                cols[i] = cols[i] + '::text'

        # table name
        table = args.get('table')
        args.pop('table')

        # create sql query
        sql = "SELECT " + ','.join(cols) + " FROM " + table + " WHERE "
        for i in set(args.keys()).intersection(['contributor_id', 'platform', 'country', 'gender', 'age_min', 'age_max']):
            sql +=  i + '=' + str(args.get(i)) + ' AND '
        if 'date_start' in args.keys():
            sql += "date >= " + str(args.get('date_start')) + " AND "
        if 'date_end' in args.keys():
            sql += "date <= " + str(args.get('date_end')) + " AND "
        sql = sql[:-5] + ';'

        # query database
        try:
            conn = conn_to_database()
            data = pd.read_sql(sql, conn)
            data = data.to_json()
            message = 'OK: Data successfully selected from database.'

        except Exception as e:

            status = 500
            message = 'Internal Server Error: PostgreSQL error ' + str(e)

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
                        required=['token', 'platform', 'timestamp', 'country', 'geo_locations', 'gender',
                                  'age_min', 'dau'],
                        required_oneof=['mau', 'mau_lower', 'mau_upper'],
                        optional=['valid', 'collection', 'age_max', 'all_fields', 'targeting', 'response'])
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
        args['date'] = "'" + dt_obj.strftime('%Y-%m-%d') + "'"
        # args['timestamp_iso'] = "'" + dt_obj.isoformat(sep=" ")[:-3] + "'"

        # table name
        table = args.pop('table')

        # create sql query
        sql = "INSERT INTO " + table + "({}) VALUES({});".format(','.join(args.keys()), ','.join([str(i) for i in args.values()]))

        # query database
        try:

            result = conn.execute(sql)
            message = 'OK: Data successfully written into database.'

        except Exception as e:

            status = 500
            message = 'Internal Server Error: PostgreSQL error ' + str(e)

        if status == 200 and 'invalid' in table:
            message += " Written with flag 'valid=false' so data will not persist in database."

    # return result
    return {"status": status, "message": message, "timestamp": timestr()}
