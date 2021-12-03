""" Настройки проекта """

import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SERVICE_URL = os.getenv('SERVICE_URL')
MAX_UPLOAD_FILE_SIZE_KB = os.getenv('MAX_UPLOAD_FILE_SIZE_KB', None)
