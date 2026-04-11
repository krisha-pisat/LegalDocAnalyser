import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. Load Environment Variables
project_root = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(project_root, ".env"))

MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    print("❌ MONGODB_URI not found in .env file.")
    sys.exit(1)

# 2. Connect to MongoDB
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["legal-documents"]
source_collection = db["supreme-court-docs"]
chunk_collection = db["supreme-court-chunks"]

# 3. Initialize Embedding Model
print("Loading Embedding Model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 4. Initialize Text Splitter
# We use chunks of 1000 characters with a 150-character overlap
# Overlap ensures that a sentence split between two chunks keeps its context.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len
)

def process_and_store_chunks():
    print("Preparing to process documents...")
    
    # FETCH ONLY IDs FIRST! 
    # Because ML embedding is so slow, holding a MongoDB cursor open will always risk timeouts.
    # By just grabbing the 7130 IDs and doing simple find_one() calls, we completely bypass all cursor timeout problems.
    doc_ids_cursor = source_collection.find({"document": {"$exists": True, "$ne": ""}}, {"_id": 1})
    
    # NEW: Check what we already processed so we can skip them!
    print("Checking for previously processed documents so we can resume where it left off...")
    already_processed_ids = set(chunk_collection.distinct("parent_case_id"))
    
    doc_ids = [doc["_id"] for doc in doc_ids_cursor if str(doc["_id"]) not in already_processed_ids]
    total_docs = len(doc_ids)
    
    print(f"Skipped {len(already_processed_ids)} already done. Found {total_docs} remaining documents to chunk. Resuming processing...")
    chunks_inserted = 0

    for i, doc_id in enumerate(doc_ids, 1):
        try:
            # Fetch the actual document text fresh!
            doc = source_collection.find_one({"_id": doc_id})
            if not doc:
                continue

            parent_id = str(doc.get("_id"))
            full_text = doc.get("document", "")
            
            if not full_text:
                continue
                
            # Split the massive text into smaller, readable chunks
            texts = text_splitter.split_text(full_text)
            
            chunk_records = []
            for text_chunk in texts:
                # Create the numerical vector using the ML model
                embedding = model.encode(text_chunk).tolist()
                
                # Build the new document format
                chunk_record = {
                    "parent_case_id": parent_id,
                    "title": doc.get("title", ""), # Good to have for the frontend to display!
                    "year": doc.get("year", None),
                    "chunk_text": text_chunk,
                    "embedding": embedding
                }
                chunk_records.append(chunk_record)
                
            # Efficiently write all chunks for this case at once to MongoDB
            if chunk_records:
                chunk_collection.insert_many(chunk_records)
                chunks_inserted += len(chunk_records)
                
            # Print an update so the console isn't frozen
            print(f"[{i}/{total_docs}] Case ID {parent_id[-6:]}: created {len(chunk_records)} chunks.")
            
        except Exception as e:
            print(f"❌ Error processing document {doc_id}: {e}")

    print(f"\n✅ Finished! Successfully generated and inserted {chunks_inserted} total chunk records into 'supreme-court-chunks'.")

if __name__ == "__main__":
    process_and_store_chunks()
