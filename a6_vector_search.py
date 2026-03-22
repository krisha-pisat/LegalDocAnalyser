import os
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# Load .env file
load_dotenv()

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "legal-documents")
COLLECTION_NAME = os.getenv("MONGODB_VECTOR_COLLECTION", "embedded-cluster")

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
collection = client[DB_NAME][COLLECTION_NAME]

# Load the embedding model
print("🔍 Loading model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Get user query
query_text = input("📥 Enter your search query: ")

# Convert query to vector
query_vector = model.encode(query_text).tolist()

# Build vector search pipeline
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector-search-1",  # use the actual index name if different
            "path": "embedding",
            "queryVector": query_vector,
            "numCandidates": 100,
            "limit": 5,
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

# Run the query
print("\n🔎 Searching MongoDB...\n")
results = list(collection.aggregate(pipeline))

# Show results
if not results:
    print("❌ No results found.")
else:
    for i, doc in enumerate(results, start=1):
        print(f"📄 Result #{i}")
        print(f"🆔 ID: {doc['_id']}")
        print(f"⭐ Score: {doc['score']:.4f}")
        print(f"📌 Summary: {doc.get('summary', '')[:500]}...\n")
