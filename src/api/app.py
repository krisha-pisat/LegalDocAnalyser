from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client["legal-documents"]
collection = db["supreme-court-docs"]

print("Mongo URI:", mongo_uri)
print("Databases:", client.list_database_names())
print("Collections in legal-documents:", db.list_collection_names())


@app.route("/search", methods=["GET"])
def search_cases():
    keyword = request.args.get("query")
    year = request.args.get("year")
    location = request.args.get("location")
    case_type = request.args.get("case_type")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = {}

    # Keyword Search (for the main dashboard search bar)
    if keyword:
        try:
            from src.rag_1.rag_search import perform_vector_search
            from bson.objectid import ObjectId
            
            seen_cases = set()
            vector_results = []
            
            # Helper to deduplicate and map documents
            def process_match(pid, title, chunk_text, year, score):
                if pid and pid not in seen_cases:
                    seen_cases.add(pid)
                    
                    parent_doc = collection.find_one({"_id": pid})
                    if not parent_doc:
                        try:
                            parent_doc = collection.find_one({"_id": ObjectId(pid)})
                        except Exception:
                            parent_doc = {}
                            
                    if not parent_doc:
                        parent_doc = {}
                        
                    vector_results.append({
                        "_id": pid,
                        "title": parent_doc.get("title") or title or "Untitled Case",
                        "summary": parent_doc.get("summary") or chunk_text,
                        "chunk_snippet": chunk_text,
                        "year": parent_doc.get("year") or year or "N/A",
                        "location": parent_doc.get("location", "Unknown"),
                        "case_type": parent_doc.get("case_type", ["Unknown"]),
                        "score": score
                    })

            # 1. TRUE EXACT MATCH BACKUP: Direct Regex against the Chunk DB
            # We do this because short 1-word queries like "assault" often get lost in Vector Semantic Space
            # if they aren't surrounded by rich context. 
            import re
            regex_cursor = db["supreme-court-chunks"].find({
                "chunk_text": {"$regex": f"\\b{re.escape(keyword)}\\b", "$options": "i"}
            }).limit(7)
            
            for rd in regex_cursor:
                pid = rd.get("parent_case_id")
                # Assign a perfect 99% score to literal physical keyword overlaps
                process_match(pid, rd.get("title"), rd.get("chunk_text", ""), rd.get("year"), 0.99)

            # 2. SEMANTIC AI MATCH: Vector Search
            docs = perform_vector_search(keyword, k=20)
            for d in docs:
                pid = d.metadata.get("parent_case_id")
                score = d.metadata.get('score', 0)
                process_match(pid, d.metadata.get("title"), d.page_content, d.metadata.get("year"), score)
            
            # Immediately return the deduplicated combined results
            return jsonify({"cases": vector_results[:15], "chart": []})
            
        except Exception as e:
            print(f"❌ Vector search failed: {e}")
            # Fallback will just run the empty query below if vector fails

    # Filter by year
    if year:
        try:
            year = int(year)
            query["year"] = year
        except ValueError:
            query["year"] = year

    # Filter by location (case-insensitive match)
    if location:
        query["location"] = {"$regex": location, "$options": "i"}

    # Filter by case_type (case-insensitive, matches any in list)
    if case_type:
        query["case_type"] = {"$elemMatch": {"$regex": case_type, "$options": "i"}}

    # Filter by date range
    if start_date or end_date:
        date_filter = {}
        try:
            if start_date:
                date_filter["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                date_filter["$lte"] = datetime.strptime(end_date, "%Y-%m-%d")
            query["date"] = date_filter
        except ValueError:
            print("Invalid date format. Expecting YYYY-MM-DD.")

    print("Search Query:", query)
    results = list(collection.find(query, {"_id": 0}))
    print(f"Found {len(results)} result(s)")

    # Build chart data for matched cases
    year_freq = {}
    for r in results:
        y = r.get("year")
        if isinstance(y, int):
            year_freq[y] = year_freq.get(y, 0) + 1

    chart_data = [{"year": y, "count": c} for y, c in sorted(year_freq.items())]

    return jsonify({"cases": results, "chart": chart_data})


@app.route("/chart-data", methods=["GET"])
def chart_data():
    pipeline = [
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    data = list(collection.aggregate(pipeline))
    
    # Fix: Map "_id" to "year" for frontend compatibility
    chart_ready = [{"year": d["_id"], "count": d["count"]} for d in data if d["_id"] is not None]
    
    return jsonify(chart_ready)


@app.route("/test")
def test_connection():
    return jsonify({"status": "OK", "message": "Flask app is running and connected."})


if __name__ == "__main__":
    app.run(debug=True)