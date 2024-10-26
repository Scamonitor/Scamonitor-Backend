import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')
    GCP_CLIENT_EMAIL = os.environ.get('GCP_CLIENT_EMAIL')
    GCP_PRIVATE_KEY = os.environ.get('GCP_PRIVATE_KEY').replace('\\n', '\n')