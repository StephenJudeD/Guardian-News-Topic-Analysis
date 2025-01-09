import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GUARDIAN_API_KEY = os.getenv('GUARDIAN_API_KEY', 'bcaeaf9d-e4c2-4bb4-a13e-7e2b7dafa5bc')
    DEPLOYMENT_TYPE = os.getenv('DEPLOYMENT_TYPE', 'heroku')  # heroku, gcp, or aws
    USE_LIGHTWEIGHT = os.getenv('USE_LIGHTWEIGHT', 'True').lower() == 'true'
    REDIS_URL = os.getenv('REDIS_URL', None)
