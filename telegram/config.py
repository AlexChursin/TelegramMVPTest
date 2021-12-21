import os
from dotenv import load_dotenv
load_dotenv()

URL_API_BACKEND = os.environ.get('URL_API_BACKEND')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
URL_SERVER = os.environ.get('URL_SERVER')
SERVER_PREFIX = os.environ.get('SERVER_PREFIX')
URL_API_DJANGO = os.environ.get('URL_API_DJANGO')
BOT_NAME = os.environ.get('BOT_NAME')
