from pymongo import MongoClient
from contextlib import contextmanager
from dotenv import load_dotenv
import os


load_dotenv()

@contextmanager
def get_mongo_connection():
    MONGO_URI = os.getenv("MONGO_DB_URI")
    client = MongoClient(MONGO_URI)
    try:
        yield client
    finally:
        client.close()