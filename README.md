# Chairpal Chatbot

An AI-powered smart wheelchair assistant API built with **FastAPI**, **FastText** supervised intent classification, **Semantic RAG** (MiniLM + FAISS-style cosine search), and a rule-based override engine.

The chatbot supports both **Egyptian Arabic** and **English**, provides real-time health sensor awareness, personalized responses, and conversation memory — all designed for the Chairpal smart wheelchair ecosystem.

---

## Project Structure

```
Chairpal_Chatbot/
├── chatbot/                        # Core chatbot modules
│   ├── chatbot.py                  # Main orchestrator
│   ├── intent_classifier.py        # FastText intent classifier
│   ├── memory.py                   # Conversation memory (per-user session)
│   ├── preprocessor.py             # Text cleaning & language detection
│   ├── response_generator.py       # RAG-based response engine
│   └── rule_engine.py              # YAML-driven intent override rules
├── config/
│   ├── health_thresholds.json      # Heart rate & temperature alert thresholds
│   └── intent_overrides.yaml       # Rule-based intent override config
├── data/
│   ├── merged_dataset.jsonl        # Main training & retrieval dataset
│   ├── health_intents_dataset.jsonl
│   ├── semantic_index.pkl          # Precomputed semantic embeddings index
│   └── confusion_matrix.png        # Model evaluation results
├── design/                         # UI mockups and app screenshots
├── models/
│   └── intent_classifier.ftz      # Quantized FastText model (production)
├── scripts/                        # Data pipeline & training scripts
│   ├── 01_generate_health_data.py
│   ├── 02_train_intent_classifier.py
│   ├── 03_add_article_data.py
│   ├── 04_build_semantic_index.py
│   ├── 05_add_lifestyle_data.py
│   ├── 06_deduplicate_dataset.py
│   ├── health_data.py
│   └── transform_user_data.py
├── templates/
│   └── index.html                  # Built-in web chat simulator UI
├── .env.example
├── main.py                         # FastAPI entry point (Port 5000)
├── requirements.txt
└── schemas.py                      # Pydantic request/response models
```

---

## Quick Start

### 1. Clone & Install

```powershell
git clone https://github.com/YOUR_USERNAME/Chairpal_Chatbot.git
cd Chairpal_Chatbot

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Environment

```powershell
$env:CHAIRPAL_CORS_ORIGINS = "*"
$env:PYTHONIOENCODING = "utf-8"
```

### 3. Run the API

```powershell
python main.py
```

API available at: `http://localhost:5000`
- **Chat endpoint**: `POST /chat`
- **Health check**: `GET /health`
- **Web simulator**: `GET /`

---

## API Usage

### Request Format

```json
POST /chat
{
  "message": { "text": "ازاي اربط الكرسي بالواي فاي؟" },
  "user": { "id": 1, "full_name": "Sara", "gender": "female" },
  "health": {
    "heart_rate": { "value": 105, "status": "high" },
    "temperature": { "value": 37.2, "status": "normal" },
    "mpu_monitoring": { "fall_risk_detected": false }
  }
}
```

### Response Format

```json
{
  "response": "لربط الكرسي المتحرك بالتطبيق، اتبع الخطوات التالية...",
  "intent": "connect_wheelchair",
  "confidence": 0.97,
  "language": "ar"
}
```

---

## Retrain the Model

Run the scripts **in order** when new data is added:

```powershell
python scripts\01_generate_health_data.py
python scripts\02_train_intent_classifier.py   # Produces .bin then .ftz
python scripts\03_add_article_data.py
python scripts\04_build_semantic_index.py      # Produces semantic_index.pkl
python scripts\05_add_lifestyle_data.py
python scripts\06_deduplicate_dataset.py
```

> The `.bin` model file (800MB) is generated during training and is **not needed after the `.ftz` is produced**. It is excluded by `.gitignore`.

---

## AWS Deployment

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for full step-by-step instructions on deploying to AWS EC2, including how to download the model and set up a permanent `systemd` service.

---

## Supported Intents

| Intent | Description |
|--------|-------------|
| `greeting` | Welcome & greetings |
| `bot_identity` | What is Chairpal / the app |
| `wheelchair_usage` | How to use the wheelchair |
| `connect_wheelchair` | How to connect via Wi-Fi |
| `battery` | Battery status & charging |
| `navigation` | Autonomous navigation & obstacle avoidance |
| `sensor_interpretation` | Reading health sensor data |
| `normal_health` | Normal vitals confirmation |
| `fatigue` | Fatigue-related queries |
| `pain` | Pain-related queries |
| `shortness_of_breath` | Breathing difficulty queries |
| `emotional_support` | Emotional support & encouragement |
| `daily_support` | Daily routine & medication reminders |
| `app_help` | App usage & account management |
| `wheelchair_stop_reason` | Why did the wheelchair stop |
| `thanks` | Gratitude responses |
| `fallback` | Out-of-scope or low-confidence queries |

---

## Health & Safety

The chatbot provides supportive health guidance based on live sensor readings. **It is not a replacement for medical professionals or emergency services.** If symptoms are severe or persistent, contact a doctor or call emergency services immediately.
