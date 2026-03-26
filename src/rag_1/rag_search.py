import os
import sys
# ✅ Add the project root to sys.path so 'src' can always be found
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from src.db.mongo_client import collection

# Load the embedding model locally (efficient for search)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def perform_vector_search(query: str, k: int = 4):
    # 1. Convert query to vector
    query_vector = model.encode(query).tolist()

    # 2. Get index name from environment
    index_name = os.getenv("MONGODB_INDEX", "vector-search-1")

    # 3. Build MongoDB vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": index_name,
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": k,
                "similarity": "cosine"
            }
        },
        {
            "$project": {
                "_id": 0,
                "document": 1,
                "summary": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    # 4. Run the query
    results = list(collection.aggregate(pipeline))

    # 🟢 Terminal Logging (User requested)
    print(f"\n🔍 Vector Search retrieved {len(results)} chunks:")
    for i, res in enumerate(results, 1):
        score = res.get("score", 0)
        content_snippet = (res.get("document") or res.get("summary") or "")[:100].replace("\n", " ")
        print(f"  [{i}] Score: {score:.4f} | {content_snippet}...")

    # 5. Convert to LangChain Document objects for pipeline compatibility
    docs = []
    for res in results:
        content = res.get("document") or res.get("summary") or ""
        docs.append(Document(page_content=content, metadata={"score": res.get("score")}))

    return docs