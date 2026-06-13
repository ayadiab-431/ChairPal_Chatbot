import os
import json
import random

# Define the dataset path
DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "health_intents_dataset.jsonl")

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

from health_data import (
    dizziness_templates, dizziness_answer_ar, dizziness_answer_en,
    fatigue_templates, fatigue_answer_ar, fatigue_answer_en,
    pain_templates, pain_answer_ar, pain_answer_en,
    sob_templates, sob_answer_ar, sob_answer_en,
    normal_templates, normal_answer_ar, normal_answer_en,
    wheelchair_movement_templates, wheelchair_movement_answer_ar, wheelchair_movement_answer_en,
)

# Define helper to construct dataset
def generate_dataset():
    data = []
    
    intents = [
        ("fatigue", dizziness_templates, dizziness_answer_ar, dizziness_answer_en),
        ("fatigue", fatigue_templates, fatigue_answer_ar, fatigue_answer_en),
        ("pain", pain_templates, pain_answer_ar, pain_answer_en),
        ("shortness_of_breath", sob_templates, sob_answer_ar, sob_answer_en),
        ("normal_health", normal_templates, normal_answer_ar, normal_answer_en),
        ("wheelchair_usage", wheelchair_movement_templates, wheelchair_movement_answer_ar, wheelchair_movement_answer_en)
    ]
    
    for intent_name, templates, ans_ar, ans_en in intents:
        # Arabic Questions
        for q in templates["ar"]:
            data.append({
                "intent": intent_name,
                "language": "ar",
                "question": q,
                "answer": ans_ar
            })
        # English Questions
        for q in templates["en"]:
            data.append({
                "intent": intent_name,
                "language": "en",
                "question": q,
                "answer": ans_en
            })
        # Mixed Questions
        for q in templates["mixed"]:
            data.append({
                "intent": intent_name,
                "language": "mixed",
                "question": q,
                # For mixed, we can offer the Arabic answer as it's more expressive for the blend, or randomly select.
                # In Egypt, Arabic is preferred as the main response for mixed queries.
                "answer": ans_ar
            })
            
    # Let's shuffle the data slightly to make it mixed
    random.seed(42)
    random.shuffle(data)
    
    # Save as JSONL
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"Generated {len(data)} samples for the new health intents.")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_dataset()
