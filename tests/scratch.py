import os
from dotenv import load_dotenv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

load_dotenv('./config/private/collector.env')

# submit_psw_csv
valid = False
filename = 'tests/dataframe_collected_finished_test.csv'
url = os.getenv('API_URL')
token = os.getenv('API_TOKEN')
