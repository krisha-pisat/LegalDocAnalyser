# analytics/acts_analysis.py
import re
import pandas as pd
from collections import Counter
from db.mongo_client import collection

def extract_acts():
    docs = collection.find({}, {"document": 1})
    act_pattern = re.compile(r"\b[A-Z][a-zA-Z\s]+ Act(?:,? \d{4})?\b")
    acts = []

    for doc in docs:
        text = doc.get("document", "")
        matches = act_pattern.findall(text)
        acts.extend(matches)

    act_counts = Counter(acts).most_common(20)
    return pd.DataFrame(act_counts, columns=["act", "count"])
