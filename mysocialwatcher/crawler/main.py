from mysocialwatcher.crawler.utils import *
from dotenv import load_dotenv

load_dotenv()  # load_dotenv('./config/private/crawler.env')
token = os.environ.get('API_TOKEN')  # token = 'ee0b578690a08e329038fabb567294b5' / API token = '50e62dc0a02dab6ddd6afb100dce3eee'
url = os.environ.get('API_URL')  # url = 'http://127.0.0.1/api/v1/write' / ASW API url = 'http://18.135.72.18/api/v1/social_media_audience/write'
data_dir = os.environ.get('DATA_DIR')  # data_dir = 'C:/Users/edithd/Documents/mySocialWatcher/data/saffron'


if __name__ == "__main__":

    crawler(data_dir=data_dir,
            token=token,
            url=url)
