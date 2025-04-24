# app/config.py
# app/config.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoConfig:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client[os.getenv("MONGO_DBNAME")]

    def get_collection(self, name):
        return self.db[name]
