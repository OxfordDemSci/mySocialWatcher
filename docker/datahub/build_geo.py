import os
import pycountry
import pandas as pd
import geopandas as gpd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv


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


#---- gadm-0 boundaries ----#

def get_iso2(alpha_3):
    result = []
    for i in alpha_3:
        try:
            result.append(pycountry.countries.get(alpha_3=i).alpha_2)
        except:
            result.append(np.NAN)
    return result


#---- gadm0 boundaries ----#
gdf0 = gpd.read_file(os.path.join('data', 'tmp', 'gadm_410-levels.gpkg'), layer='ADM_0')

# column names to lower case
gdf0.columns = map(str.lower, gdf0.columns)
gdf0 = gdf0.rename(columns = {'country': 'name_0'})
gdf0['gid_1'] = np.NAN
gdf0['name_1'] = np.NAN

# meta_key (iso2 country codes)
gdf0['meta_key'] = get_iso2(gdf0['gid_0'])

# reorder columns
gdf0 = gdf0.loc[:, ['meta_key', 'gid_0', 'name_0', 'gid_1', 'name_1', 'geometry']]

# simplify geometries
gdf0['geometry'] = gdf0.simplify(tolerance=0.0005, preserve_topology=True)


#---- gadm1 boundaries ----#
gdf1 = gpd.read_file(os.path.join('data', 'tmp', 'gadm_410-levels.gpkg'), layer='ADM_1')

# column names to lower case
gdf1.columns = map(str.lower, gdf1.columns)
gdf1 = gdf1.rename(columns = {'country': 'name_0'})

# meta_key
gdf1['meta_key'] = np.NAN

# reorder columns
gdf1 = gdf1.loc[:, ['meta_key', 'gid_0', 'name_0', 'gid_1', 'name_1', 'geometry']]

# simplify geometries
gdf1['geometry'] = gdf1.simplify(tolerance=0.0005, preserve_topology=True)


# ---- concatenate data and write to database ----#
gdf = pd.concat([gdf0, gdf1])

with engine.connect() as conn:

    # write gadm-0 table into database
    gdf.to_postgis(name='gadm', con=conn, if_exists='replace')

    # create index on meta_key
    conn.execute("CREATE INDEX idx_gadm_meta_key ON gadm (meta_key);")

    # set table permissions
    conn.execute("GRANT SELECT ON gadm TO reader, writer;"
                 "GRANT UPDATE, INSERT ON gadm TO writer")
