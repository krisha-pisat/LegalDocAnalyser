import os
import json
from tqdm import tqdm
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# 1. Load environment variables
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "legal-documents")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "supreme-court-docs")
NEW_COLLECTION_NAME = os.getenv("MONGODB_VECTOR_COLLECTION", "embedded-cluster")

# 2. Initialize MongoDB client
client = MongoClient(MONGODB_URI)
new_collection = client[DB_NAME][NEW_COLLECTION_NAME]

# 3. Load the SentenceTransformer model
print("🔍 Loading embedding model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 4. Load the cleaned JSON file
with open("in_abs_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 5. Iterate over the documents, embed them, and upload to the new collection
print(f"📥 Embedding and uploading {len(data)} documents to '{NEW_COLLECTION_NAME}' collection...\n")

for item in tqdm(data):
    doc_id = item.get("id")
    summary = item.get("summary", "")
    document = item.get("document", "")
    split = item.get("split", "train")

    if not summary.strip() and not document.strip():
        continue

    # Combine summary and document for embedding
    combined_text = summary + "\n" + document

    # Generate embedding
    embedding = model.encode(combined_text).tolist()

    # Prepare the document for insertion
    doc = {
        "_id": doc_id,
        "summary": summary,
        "document": document,
        "split": split,
        "embedding": embedding
    }

    # Upsert document into new collection
    new_collection.update_one({"_id": doc_id}, {"$set": doc}, upsert=True)

print("\n✅ Embedding upload completed successfully!")