""" Настройки проекта """

import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SERVICE_URL = os.getenv('SERVICE_URL')
