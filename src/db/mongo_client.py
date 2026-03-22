# src/db/mongo_client.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION")

client = MongoClient(MONGODB_URI)
collection = client[DB_NAME][COLLECTION_NAME]
