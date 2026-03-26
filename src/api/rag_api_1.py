# src/api/rag_api_1.py
import os, sys
from flask      import Flask, request, jsonify
from flask_cors import CORS
from dotenv     import load_dotenv

# ─── Load your .env FIRST, so environvars are available
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(dotenv_path=os.path.join(project_root, ".env"))

# ─── Make sure Python can see src/ as a package root
sys.path.append(os.path.join(project_root, "src"))

# ─── Now import your RAG entrypoint
from rag_1.pipeline import rag_pipeline

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json() or {}
    query   = payload.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query is missing"}), 400

    try:
        answer, docs = rag_pipeline(query)
        
        # Convert Document objects to plain dictionaries for JSON
        sources = []
        for d in docs:
            sources.append({
                "content": d.page_content,
                "score": d.metadata.get("score", 0)
            })

        return jsonify({
            "answer": answer,
            "sources": sources
        })
    except Exception as e:
        print("❌ /chat error:", e, file=sys.stderr)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # From project root run:
    #   python -m src.api.rag_api_1
    app.run(port=8000, debug=True)