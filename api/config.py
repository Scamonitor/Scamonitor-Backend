import os
from dotenv import load_dotenv
import datetime

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')
    GCP_CLIENT_EMAIL = os.environ.get('GCP_CLIENT_EMAIL')
    GCP_PRIVATE_KEY = os.environ.get('GCP_PRIVATE_KEY').replace('\\n', '\n')
    AUDIO_MODEL_URL = os.environ.get('AUDIO_MODEL_URL')
    IMAGE_MODEL_URL = os.environ.get('IMAGE_MODEL_URL')
    GPT_API_KEY = os.environ.get('GPT_API_KEY')
    SENDER_EMAIL_PASSWORD = os.environ.get('SENDER_EMAIL_PASSWORD')

    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=1)
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True  
    SESSION_COOKIE_PATH = '/'