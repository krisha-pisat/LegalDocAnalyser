import os
import json

BASE_DIR = "C:/LegalDocsAnalyser/dataset/IN-Abs"  # Change to your local base path
OUTPUT_FILE = "in_abs_cleaned.json"

data = []

def process_split(split_name):
    judgement_path = os.path.join(BASE_DIR, f"{split_name}-data/judgement")
    summary_path = os.path.join(BASE_DIR, f"{split_name}-data/summary")

    for fname in os.listdir(judgement_path):
        if not fname.endswith(".txt"):
            continue

        doc_id = fname.replace(".txt", "")
        judgement_file = os.path.join(judgement_path, fname)
        summary_file = os.path.join(summary_path, fname)

        # Read judgement
        with open(judgement_file, "r", encoding="utf-8") as f:
            judgement = f.read().strip()

        # Read summary
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = f.read().strip()

        data.append({
            "id": doc_id,
            "split": split_name,
            "document": judgement,
            "summary": summary
        })

# Process train and test splits
process_split("train")
process_split("test")

# Save to JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Preprocessing complete. Total records: {len(data)}. Saved to {OUTPUT_FILE}")
