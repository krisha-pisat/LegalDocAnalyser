import os
import json
from dotenv import load_dotenv
from google.cloud import storage
from vertexai.language_models import TextEmbeddingModel
import vertexai
from pymongo import MongoClient

# Load secrets from .env file
load_dotenv()

# Initialize Vertex AI
vertexai.init(
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GCP_LOCATION", "us-central1")
)
model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")

# Connect to MongoDB Atlas
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["legal_docs"]
collection = db["in_abs_embeddings"]  # Change as needed

def process_file(event, context):
    file_name = event['name']
    if not file_name.endswith(".json"):
        return

    storage_client = storage.Client()
    bucket = storage_client.bucket(event['bucket'])
    blob = bucket.blob(file_name)
    content = blob.download_as_text()
    data = json.loads(content)

    batch = []
    for item in data:
        embedding = model.get_embeddings([item["document"]])[0].values
        batch.append({
            "id": item["id"],
            "embedding": embedding,
            "document": item["document"],
            "summary": item.get("summary", item.get("summary_a1", "")),
        })

    collection.insert_many(batch)
