# analytics/case_type_trend.py
import pandas as pd
from db.mongo_client import collection

def get_case_type_trend(case_type="Criminal"):
    pipeline = [
        {"$match": {"case_type": case_type}},
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    results = list(collection.aggregate(pipeline))
    return pd.DataFrame(results).rename(columns={"_id": "year"})
