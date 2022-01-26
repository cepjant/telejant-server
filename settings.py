""" Настройки проекта """

import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
MAX_UPLOAD_FILE_SIZE_KB = os.getenv('MAX_UPLOAD_FILE_SIZE_KB', None)
TARGET_SYSTEM_URL = os.getenv('TARGET_SYSTEM_URL') or os.getenv('SERVICE_URL')
