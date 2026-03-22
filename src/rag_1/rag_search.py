import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
BASE_DIR        = os.path.abspath(os.path.dirname(__file__))
FAISS_INDEX_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "vectorstore", "db_faiss"))

def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

def perform_vector_search(query: str, k: int = 4):
    db = FAISS.load_local(
        FAISS_INDEX_DIR,
        embeddings=get_embedding_model(),
        allow_dangerous_deserialization=True
    )
    return db.similarity_search(query, k=k)