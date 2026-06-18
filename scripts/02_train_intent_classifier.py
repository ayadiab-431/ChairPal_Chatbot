import os
import json
import random
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import fasttext
import numpy as np

# Add local path to import preprocessor
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from chatbot.preprocessor import Preprocessor

# Constants
MERGED_DATA_FILE = "data/merged_dataset.jsonl"
MODELS_DIR = "models"
DATA_DIR = "data"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

TRAIN_TXT = os.path.join(DATA_DIR, "fasttext_train.txt")
VAL_TXT = os.path.join(DATA_DIR, "fasttext_val.txt")
TEST_TXT = os.path.join(DATA_DIR, "fasttext_test.txt")
MODEL_BIN = os.path.join(MODELS_DIR, "intent_classifier.bin")
CM_IMAGE = os.path.join(DATA_DIR, "confusion_matrix.png")

def augment_text(text, lang="ar"):
    variants = []
    words = text.split()
    
    # 1. Random word deletion
    if len(words) > 3:
        idx = random.randint(0, len(words)-1)
        variants.append(' '.join(words[:idx] + words[idx+1:]))
    
    # 2. Word swap (adjacent)
    if len(words) > 2:
        idx = random.randint(0, len(words)-2)
        swapped = words.copy()
        swapped[idx], swapped[idx+1] = swapped[idx+1], swapped[idx]
        variants.append(' '.join(swapped))
    
    # 3. Arabic synonym replacement (simple)
    ar_synonyms = {"ازاي": "كيف", "عايز": "محتاج", "فين": "وين", "ايه": "ماذا", "امتى": "متى"}
    has_synonym = False
    syn_variant = []
    for w in words:
        if w in ar_synonyms:
            syn_variant.append(ar_synonyms[w])
            has_synonym = True
        else:
            syn_variant.append(w)
    if has_synonym:
        variants.append(' '.join(syn_variant))
        
    return variants

def load_data():
    samples = []
    preprocessor = Preprocessor()
    
    if os.path.exists(MERGED_DATA_FILE):
        print(f"Loading dataset: {MERGED_DATA_FILE}")
        with open(MERGED_DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    cleaned_q = preprocessor.clean(item.get("question", ""))
                    if cleaned_q:
                        samples.append((cleaned_q, item.get("intent", "unknown")))
    else:
        print(f"Error: Dataset {MERGED_DATA_FILE} not found.")
        
    return samples

def train_and_evaluate():
    samples = load_data()
    if not samples:
        print("Error: No data loaded. Cannot train model.")
        return
        
    print(f"Total loaded samples: {len(samples)}")
    
    X = [q for q, intent in samples]
    y = [intent for q, intent in samples]
    
    # 70/15/15 Split
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full, y_train_full, test_size=0.1765, stratify=y_train_full, random_state=42 # 0.1765 of 0.85 ~ 0.15
    )
    
    print(f"Base Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    
    # Data Augmentation for minority classes
    minority_intents = {"fatigue", "pain", "shortness_of_breath", "normal_health", "wheelchair_stop_reason", "connect_wheelchair", "daily_support", "wheelchair_usage", "bot_identity", "greeting"}
    X_train_aug = []
    y_train_aug = []
    
    for text, intent in zip(X_train, y_train):
        X_train_aug.append(text)
        y_train_aug.append(intent)
        if intent in minority_intents:
            variants = augment_text(text)
            for v in variants:
                if v and v not in X_train_aug:
                    X_train_aug.append(v)
                    y_train_aug.append(intent)
                    
    print(f"Train samples (after augmentation): {len(X_train_aug)}")
    
    # Write Train/Val/Test files
    with open(TRAIN_TXT, "w", encoding="utf-8") as f:
        for text, intent in zip(X_train_aug, y_train_aug):
            f.write(f"__label__{intent} {text}\n")
            
    with open(VAL_TXT, "w", encoding="utf-8") as f:
        for text, intent in zip(X_val, y_val):
            f.write(f"__label__{intent} {text}\n")
            
    with open(TEST_TXT, "w", encoding="utf-8") as f:
        for text, intent in zip(X_test, y_test):
            f.write(f"__label__{intent} {text}\n")
            
    print("Training FastText supervised model...")
    model = fasttext.train_supervised(
        input=TRAIN_TXT,
        epoch=30,
        lr=0.3,
        wordNgrams=2,
        dim=100,
        minn=2,
        maxn=4,
        loss='softmax'
    )
    
    model.save_model(MODEL_BIN)
    print(f"Model saved to: {MODEL_BIN}")
    
    try:
        model.quantize(input=TRAIN_TXT, retrain=True)
        ftz_path = os.path.join(MODELS_DIR, "intent_classifier.ftz")
        model.save_model(ftz_path)
        print(f"Quantized model saved to: {ftz_path}")
    except Exception as q_err:
        print(f"Warning: Model quantization failed: {q_err}.")
    
    # Evaluation
    _, val_precision, val_recall = model.test(VAL_TXT)
    val_f1 = 2 * (val_precision * val_recall) / (val_precision + val_recall) if (val_precision + val_recall) > 0 else 0
    
    _, test_precision, test_recall = model.test(TEST_TXT)
    test_f1 = 2 * (test_precision * test_recall) / (test_precision + test_recall) if (test_precision + test_recall) > 0 else 0
    
    print(f"\n===========================================")
    print(f"Validation F1: {val_f1:.4%}")
    print(f"Test F1:       {test_f1:.4%}")
    print(f"===========================================")
    
    # Detailed report and confusion matrix
    y_pred = []
    for text in X_test:
        labels, probabilities = model.predict(text, k=1)
        pred_intent = labels[0].replace("__label__", "")
        y_pred.append(pred_intent)
        
    print("\nDetailed Classification Report (Test Set):")
    print(classification_report(y_test, y_pred, digits=4))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    sorted_labels = sorted(list(set(y_test)))
    
    fig, ax = plt.subplots(figsize=(14, 12))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=sorted_labels)
    disp.plot(ax=ax, xticks_rotation=45, cmap='Blues')
    plt.tight_layout()
    plt.savefig(CM_IMAGE, dpi=150, bbox_inches='tight')
    print(f"Confusion matrix saved to {CM_IMAGE}")

if __name__ == "__main__":
    train_and_evaluate()
