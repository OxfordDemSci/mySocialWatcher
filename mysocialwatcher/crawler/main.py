from mysocialwatcher.crawler.utils import *
from dotenv import load_dotenv

load_dotenv()  # load_dotenv('./config/private/crawler.env')
token = os.environ.get('API_TOKEN')  # token = '4f839b5041802148995ee58024e6b583'
url = os.environ.get('API_URL')
data_dir = os.environ.get('DATA_DIR')


if __name__ == "__main__":

    crawler(data_dir=data_dir,
            token=token,
            url=url)
