import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

# Load environment variables
project_root = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(project_root, ".env"))

MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    print("❌ MONGODB_URI not found.")
    exit(1)

# Connect to database
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
collection = client["legal-documents"]["supreme-court-docs"]

print("Connecting to database...")

# Emergency unlocking: Because you hit exactly 512MB, MongoDB locks the entire database into read-only mode.
# It won't even let you delete fields because deleting fields requires 1 byte of free space to write the "command log"!
# To fix this, we simply drop the new chunks we just started making (we can recreate them later).
print("1 -> Dropping partial supreme-court-chunks collection to unlock read-only mode...")
client["legal-documents"]["supreme-court-chunks"].drop()

print("2 -> Database is now unlocked! Deleting old document-level embeddings to free up space...")
result = collection.update_many({}, {"$unset": {"embedding": ""}})

print(f"✅ Success! Deleted old embeddings from {result.modified_count} cases.")
print("Your MongoDB storage is now massively freed up. You can go back to running create_chunks.py from scratch!")
