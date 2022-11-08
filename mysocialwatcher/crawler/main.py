from mysocialwatcher.crawler.utils import *
from dotenv import load_dotenv

load_dotenv()  # load_dotenv('./config/private/crawler.env')
api_token = os.environ.get('API_TOKEN')  # api_token = '8aa714195bd2a87be0c33b0eb9ddc2f2'
api_url = os.environ.get('API_URL')


if __name__ == "__main__":

    crawler(crawl_dir='./data',
            token=api_token,
            url=api_url)
