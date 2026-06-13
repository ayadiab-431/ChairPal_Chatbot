import os
import json
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import time

def build_semantic_index(dataset_path: str, output_path: str, model_name: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
    print(f"Loading dataset from {dataset_path}...")
    dataset = []
    if os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    dataset.append(json.loads(line))
    else:
        print(f"Dataset not found at {dataset_path}")
        return

    print(f"Loaded {len(dataset)} records.")
    
    # We will build embeddings for all questions
    # We also keep track of their indices so we can retrieve the answers
    questions = []
    metadata = []
    for i, item in enumerate(dataset):
        # Clean the question slightly for embedding
        q = item.get("question", "").strip()
        if q:
            questions.append(q)
            metadata.append({
                "original_index": i,
                "intent": item.get("intent", ""),
                "language": item.get("language", "")
            })

    print(f"Loading SentenceTransformer model: {model_name}...")
    # device='cpu' ensures it runs on CPU
    model = SentenceTransformer(model_name, device='cpu')
    
    print("Generating embeddings (this may take a few minutes on CPU)...")
    start_time = time.time()
    
    # Convert to embeddings
    # show_progress_bar=True to see progress in terminal
    embeddings = model.encode(questions, show_progress_bar=True, convert_to_numpy=True)
    
    end_time = time.time()
    print(f"Embeddings generated in {end_time - start_time:.2f} seconds.")
    
    # Save the index
    print(f"Saving index to {output_path}...")
    index_data = {
        "embeddings": embeddings,
        "metadata": metadata,
        "model_name": model_name
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "wb") as f:
        pickle.dump(index_data, f)
        
    print("Done! Semantic index built successfully.")

if __name__ == "__main__":
    DATASET_PATH = "data/merged_dataset.jsonl"
    OUTPUT_INDEX_PATH = "data/semantic_index.pkl"
    build_semantic_index(DATASET_PATH, OUTPUT_INDEX_PATH)
