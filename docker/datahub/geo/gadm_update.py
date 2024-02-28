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


    # load geo_keys
    gadm_key = pd.read_csv(os.path.join('config', 'specs', 'specs_explore', 'fb_gadm_match', 'region',
                                         'region_matched.csv'))
    gadm_key = gadm_key.rename(columns={'key': 'meta_key'})
    gadm_key = gadm_key[['meta_key', 'GID_1']]
    gadm_key = gadm_key.dropna(subset=['meta_key', 'GID_1'], how='any')

    # update gadm table with meta_keys for regions
    with engine.connect() as conn:
        # conn = engine.connect()

        # get existing meta_key's
        existing_keys = pd.read_sql(sql='select meta_key from gadm where meta_key is not null;', con=conn)

        # drop cities already in database
        gadm_key = gadm_key[~gadm_key['meta_key'].apply(str).isin(existing_keys['meta_key'])]

        for idx, row in gadm_key.iterrows():
            print(idx)
            sql = (f"UPDATE gadm "
                   f"SET meta_key = {int(row['meta_key'])} "
                   f"WHERE gid_1 = '{row['GID_1']}';")
            conn.execute(sql)


