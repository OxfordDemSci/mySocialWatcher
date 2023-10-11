from mysocialwatcher.crawler.utils import *
from dotenv import load_dotenv

load_dotenv()  # load_dotenv('./config/private/crawler.env')
token = os.environ.get('API_TOKEN')  # token = '2a233d39993842cffb72cd24f281fb2a'
url = os.environ.get('API_URL')  # url = 'http://127.0.0.1/api/v1/write'
data_dir = os.environ.get('DATA_DIR')  # data_dir = '/research/git/OxfordDemSci/mySocialWatcher/data'


if __name__ == "__main__":

    crawler(data_dir=data_dir,
            token=token,
            url=url)
