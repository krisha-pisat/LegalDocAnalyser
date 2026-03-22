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
    year = request.args.get("year")
    location = request.args.get("location")
    case_type = request.args.get("case_type")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = {}

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