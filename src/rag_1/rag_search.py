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

def perform_vector_search(query: str, k: int = 4, case_id: str = None):
    # 1. Convert query to vector
    query_vector = model.encode(query).tolist()

    # 2. Get index name from environment
    index_name = os.getenv("MONGODB_INDEX", "vector-search-1")

    # 3. Build MongoDB vector search pipeline
    vector_search_stage = {
        "index": index_name,
        "path": "embedding",
        "queryVector": query_vector,
        "numCandidates": 100,
        "limit": k * 3, # Pull 3x the documents initially so we can re-evaluate them
        "similarity": "cosine"
    }

    # 📌 NATIVE ATLAS CLOUD FILTERING
    # This natively filters the vector index exclusively inside the MongoDB cloud.
    if case_id:
        vector_search_stage["filter"] = {"parent_case_id": {"$eq": case_id}}

    pipeline = [
        {
            "$vectorSearch": vector_search_stage
        },
        {
            "$project": {
                "_id": 0,
                "chunk_text": 1,
                "title": 1,
                "year": 1,
                "parent_case_id": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    # 4. Run the query
    results = list(collection.aggregate(pipeline))

    # --- HYBRID SEARCH RERANKING ---
    # Pure Vector Search struggles with EXACT phrasing. This Python reranker manually 
    # boosts the score of chunks that literally contain the search terms.
    query_lower = query.lower().strip()
    for res in results:
        chunk_text_lower = (res.get("chunk_text") or "").lower()
        
        # Exact Phrase Match Boost
        if query_lower in chunk_text_lower:
            res["score"] = res.get("score", 0) + 0.3  # Huge artificial bump to push it to Rank #1
        elif len(query_lower.split()) > 1:
            # Partial Term Boost
            words = query_lower.split()
            matches = sum(1 for w in words if w in chunk_text_lower and len(w) > 3)
            # Smaller bump for partial vocabulary matches
            res["score"] = res.get("score", 0) + (0.05 * matches)

    # Re-sort descending using the newly calculated Hybrid Score
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # Normalize scores so they never exceed 99% visually on the frontend!
    if results and results[0].get("score", 0) > 0.99:
        max_score = results[0]["score"]
        for res in results:
            res["score"] = (res.get("score", 0) / max_score) * 0.99
    
    # Trim back down to the top 'k'
    results = results[:k]

    # 🟢 Terminal Logging (User requested)
    print(f"\n🔍 Vector Search retrieved {len(results)} chunks:")
    for i, res in enumerate(results, 1):
        score = res.get("score", 0)
        title = res.get("title", "Untitled Case")
        content_snippet = (res.get("chunk_text") or "")[:80].replace("\n", " ")
        print(f"  [{i}] Score: {score:.4f} | Case: {title[:30]} | {content_snippet}...")

    # 5. Convert to LangChain Document objects for pipeline compatibility
    docs = []
    for res in results:
        content = res.get("chunk_text") or ""
        metadata = {
            "score": res.get("score"),
            "title": res.get("title"),
            "year": res.get("year"),
            "parent_case_id": res.get("parent_case_id")
        }
        docs.append(Document(page_content=content, metadata=metadata))

    return docs