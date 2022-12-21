from mysocialwatcher.api.utils import *
import sys
load_dotenv('docker/datahub/.env')
os.environ['POSTGRES_HOST'] = '18.135.72.18'


def query_test(sql, conn):

    t1 = datetime.datetime.now()

    data = pd.read_sql(sql, conn)

    result = data.to_json()

    t2 = datetime.datetime.now()

    elapsed_time = (t2 - t1).total_seconds()

    print('time: ' + str(elapsed_time) + ' seconds')
    print('rows: ' + str(len(data)))
    print('rows/sec: ' + str(round(len(data) / elapsed_time)))
    print('df size: ' + str(sys.getsizeof(data) * 1e-6) + ' MB')
    print('json size: ' + str(sys.getsizeof(result) * 1e-6) + ' MB')


query_test(sql="select * from facebook where country='UA';",
           conn=conn)

query_test(sql="select * from facebook where country='UA' and collection_date >= '2022-12-01' limit 100000;",
           conn=conn)

query_test(sql="select * from facebook where country='UA' limit 100000 ;",
           conn=conn)

query_test(sql="select * from facebook where country='UA' limit 200000 ;",
           conn=conn)

query_test(sql="select * from facebook where country='UA' limit 150000 ;",
           conn=conn)

query_test(sql="select * from facebook where country='UA' and collection_date >= '2022-11-01' and collection_date < '2022-12-01' and gender = 0 limit 100000;",
           conn=conn)

