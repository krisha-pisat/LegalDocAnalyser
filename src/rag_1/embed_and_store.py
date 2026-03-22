import os
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from src.rag_1.load_and_chunk import load_json_and_chunk

# — adjust paths as needed —
JSON_PATH  = os.path.abspath(os.path.join(os.getcwd(), "legal-documents.supreme-court-docs.json"))
FAISS_PATH = os.path.abspath(os.path.join(os.getcwd(), "vectorstore", "db_faiss"))
BATCH_SIZE = 5000
TOTAL_DOCS = 100000  # set to len(JSON)

def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

def store_embeddings_in_batches():
    embeddings = get_embedding_model()
    vs = None

    for start in range(0, TOTAL_DOCS, BATCH_SIZE):
        end = min(start + BATCH_SIZE, TOTAL_DOCS)
        print(f"🔹 Processing docs {start}–{end}…")

        docs = load_json_and_chunk(JSON_PATH, start, end)
        print(f"📄 Chunks in this batch: {len(docs)}")
        if not docs:
            continue

        if vs is None:
            vs = FAISS.from_documents(docs, embeddings)
        else:
            new_vs = FAISS.from_documents(docs, embeddings)
            vs.merge_from(new_vs)

    if vs:
        os.makedirs(FAISS_PATH, exist_ok=True)
        vs.save_local(FAISS_PATH)
        print(f"✅ Stored embeddings at: {FAISS_PATH}")
    else:
        print("⚠️ No data processed.")

if __name__ == "__main__":
    store_embeddings_in_batches()