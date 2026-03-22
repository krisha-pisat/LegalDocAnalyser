import os
import json

# Windows-style path (make sure to escape backslashes or use raw string)
LOCAL_DIR = "C:\\LegalDocsAnalyser\\dataset\\IN-Ext"

DOC_PATH = os.path.join(LOCAL_DIR, "judgement")
SUMMARY_PATH_A1 = os.path.join(LOCAL_DIR, "summary", "full", "A1")
SUMMARY_PATH_A2 = os.path.join(LOCAL_DIR, "summary", "full", "A2")

data = []

for fname in os.listdir(DOC_PATH):
    if not fname.endswith(".txt"):
        continue  # skip non-txt files

    try:
        with open(os.path.join(DOC_PATH, fname), 'r', encoding='utf-8') as f:
            doc_text = f.read()

        with open(os.path.join(SUMMARY_PATH_A1, fname), 'r', encoding='utf-8') as f1:
            summary_a1 = f1.read()

        with open(os.path.join(SUMMARY_PATH_A2, fname), 'r', encoding='utf-8') as f2:
            summary_a2 = f2.read()

        data.append({
            "id": fname.replace(".txt", ""),
            "document": doc_text,
            "summary_a1": summary_a1,
            "summary_a2": summary_a2,
        })

    except Exception as e:
        print(f"❌ Error processing file {fname}: {e}")

# Save preprocessed JSON
with open("in_ext_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"✅ Processed {len(data)} documents.")
