import pandas as pd
from db.mongo_client import collection

def get_year_wise_case_volume():
    pipeline = [
        {"$group": {"_id": "$year", "total_cases": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    results = list(collection.aggregate(pipeline))
    return pd.DataFrame(results).rename(columns={"_id": "year"})
