# analytics/location_analysis.py
import pandas as pd
from db.mongo_client import collection

def total_cases_by_location():
    pipeline = [
        {"$match": {"location": {"$ne": "Unknown"}}},
        {"$group": {"_id": "$location", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = list(collection.aggregate(pipeline))
    return pd.DataFrame(results).rename(columns={"_id": "location"})

def top_case_types_by_location(location):
    pipeline = [
        {"$match": {"location": location}},
        {"$unwind": "$case_type"},
        {"$group": {"_id": "$case_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    results = list(collection.aggregate(pipeline))
    return pd.DataFrame(results).rename(columns={"_id": "case_type"})
