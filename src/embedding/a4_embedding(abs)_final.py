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

# 2. Initialize MongoDB client
client = MongoClient(MONGODB_URI)
collection = client[DB_NAME][COLLECTION_NAME]

# 3. Load the SentenceTransformer model
print("🔍 Loading embedding model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 4. Load the cleaned JSON file
with open("in_abs_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 5. Iterate over the documents, generate embeddings, and update the same collection
print(f"📥 Embedding and updating {len(data)} documents into '{COLLECTION_NAME}'...\n")

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

    # Update the existing document (by _id), adding the embedding field
    collection.update_one(
        {"_id": doc_id},
        {
            "$set": {
                "summary": summary,
                "document": document,
                "split": split,
                "embedding": embedding
            }
        },
        upsert=True  # Will insert the doc if it doesn't exist already
    )

print("\n✅ Embedding successfully added to the same collection!")
