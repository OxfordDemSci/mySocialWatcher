import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv


if __name__=='__main__':
    # load database credentials
    load_dotenv(os.path.join('docker', 'datahub', '.env'))
    POSTGRES_HOST='18.135.72.18'
    POSTGRES_PORT=os.getenv('POSTGRES_PORT')
    POSTGRES_DB=os.getenv('POSTGRES_DB')
    POSTGRES_USER=os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')

    # connect to database
    engine = create_engine(f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
                           f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
                           f"{POSTGRES_DB}")

    #---- regions ----#

    # load geo_keys
    gadm_key = (pd.read_csv(os.path.join('docker','datahub','geo','data','meta_gadm1_key.csv')).
                dropna(subset=['meta_key'], how='all'))

    # update gadm table with meta_keys for regions
    with engine.connect() as conn:
        for idx, row in gadm_key.iterrows():
            sql = (f"UPDATE gadm "
                   f"SET meta_key = {int(row['meta_key'])} "
                   f"WHERE gid_1 = '{row['gid_1']}';")
            conn.execute(sql)



