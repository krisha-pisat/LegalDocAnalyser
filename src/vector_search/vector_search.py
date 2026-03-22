# vector_search/search.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# Load env
load_dotenv()

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "legal-documents")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "supreme-court-docs")
INDEX_NAME = os.getenv("MONGODB_INDEX", "vector-search-1")  # optional: use env var

# Connect
client = MongoClient(MONGODB_URI)
collection = client[DB_NAME][COLLECTION_NAME]

# Load embedding model only once
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def perform_vector_search(query_text, top_k=5):
    query_vector = model.encode(query_text).tolist()

    pipeline = [
        {
            "$vectorSearch": {
                "index": INDEX_NAME,
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": top_k,
                "similarity": "cosine"
            }
        },
        {
            "$project": {
                "_id": 1,
                "summary": 1,
                "document": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    return list(collection.aggregate(pipeline))