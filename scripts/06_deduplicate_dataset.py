import json
import os
import re

# Add path to import preprocessor
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from chatbot.preprocessor import Preprocessor

DATASET_PATH = "chairpal_dataset.jsonl"
MERGED_DATASET_PATH = "data/merged_dataset.jsonl"
HEALTH_DATA_PATH = "data/health_intents_dataset.jsonl"

def deduplicate_dataset(input_files, output_file):
    preprocessor = Preprocessor()
    seen_questions = set()
    unique_entries = []
    duplicates_count = 0
    total_count = 0
    
    # Also write a combined dataset
    for path in input_files:
        if not os.path.exists(path):
            continue
            
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    total_count += 1
                    q_raw = entry.get("question", "")
                    # Clean and normalize the question
                    q_clean = preprocessor.clean(q_raw)
                    # Remove diacritics and normalize further for dedup
                    q_norm = re.sub(r'[\u064B-\u065F\u0670]', '', q_clean)
                    q_norm = re.sub(r'[أإآ]', 'ا', q_norm)
                    
                    intent = entry.get("intent", "")
                    
                    key = (q_norm.lower(), intent)
                    if key not in seen_questions:
                        seen_questions.add(key)
                        unique_entries.append(entry)
                    else:
                        duplicates_count += 1
                except json.JSONDecodeError:
                    continue
                    
    print(f"Total entries processed: {total_count}")
    print(f"Removed duplicates: {duplicates_count}")
    print(f"Unique entries saved: {len(unique_entries)}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        for entry in unique_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    inputs = [DATASET_PATH, HEALTH_DATA_PATH]
    deduplicate_dataset(inputs, MERGED_DATASET_PATH)
