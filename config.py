import os
from dotenv import load_dotenv
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GUARDIAN_API_KEY = os.getenv('GUARDIAN_API_KEY', 'bcaeaf9d-e4c2-4bb4-a13e-7e2b7dafa5bc')
    DEFAULT_DAYS = 3  # Load last month by default
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    BATCH_SIZE = 32
