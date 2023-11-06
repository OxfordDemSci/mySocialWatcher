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
    city_key = pd.read_csv(os.path.join('config', 'specs', 'specs_explore', 'fb_cities_google_geocode', 'city_geocoded_google.csv'))

    # cities to geodataframe
    gdf = gpd.GeoDataFrame(city_key,
                           geometry = gpd.points_from_xy(city_key.lon, city_key.lat),
                           crs = "EPSG:4326")
    gdf = gdf[['key', 'name', 'country_code', 'geometry']]
    gdf = gdf.rename(columns={'key': 'meta_key', 'country_code': 'country'})

    # drop duplicate cities
    gdf = gdf.drop_duplicates(subset=['meta_key'])


    with engine.connect() as conn:
        # conn = engine.connect()

        # get existing meta_key's
        existing_keys = pd.read_sql(sql='select meta_key from cities;', con=conn)

        # drop cities already in database
        gdf = gdf[~gdf['meta_key'].isin(existing_keys['meta_key'])]

        # write new cities into database
        gdf.to_postgis(name='cities', con=conn, if_exists='append')

