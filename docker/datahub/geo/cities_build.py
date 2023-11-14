import os
import pandas as pd
import geopandas as gpd
import pycountry
from sqlalchemy import create_engine
from dotenv import load_dotenv


if __name__=='__main__':

    # load database credentials
    load_dotenv(os.path.join('docker', 'datahub', '.env'))
    POSTGRES_HOST = '18.135.72.18'
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')
    POSTGRES_DB = os.getenv('POSTGRES_DB')
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

    # connect to database
    engine = create_engine(f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
                           f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
                           f"{POSTGRES_DB}")

    # load city data
    city_key = pd.read_csv(os.path.join('docker','datahub','geo','data','meta_cities.csv'))
    city_key = city_key.drop_duplicates(subset=['meta_key'])

    # cities to geodataframe
    gdf = gpd.GeoDataFrame(city_key,
                           geometry = gpd.points_from_xy(city_key.longitude, city_key.latitude),
                           crs = "EPSG:4326")
    gdf = gdf[['meta_key','name','country','geometry']]


    with engine.connect() as conn:

        # add unique constraint to cities table
        conn.execute("CREATE UNIQUE INDEX idx_cities_meta_key ON cities (meta_key);")

        # set table permissions
        conn.execute("GRANT SELECT ON cities TO reader, writer;"
                     "GRANT UPDATE, INSERT ON cities TO writer")
