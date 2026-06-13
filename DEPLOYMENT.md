# Chairpal Chatbot — AWS Deployment Guide

## Overview

The chatbot backend is a **FastAPI** application that runs on port `5000`.

```
GitHub Repo (source code + data)      Google Drive (large model)
├── chatbot/                           └── intent_classifier.ftz (~100MB)
├── data/merged_dataset.jsonl
├── data/semantic_index.pkl
├── config/
├── main.py
└── requirements.txt
```

> The model file `models/intent_classifier.ftz` must be downloaded once to the server.
> It does **not** need to be retrained — training is already done.

---

## AWS EC2 Setup (First Time Only)

### Recommended Instance
- **Type**: `t3.medium` or higher (2 vCPU, 4GB RAM minimum)
- **OS**: Ubuntu 22.04 LTS
- **Storage**: 20GB+
- **Security Group**: Open inbound port `5000`

### Step-by-Step

```bash
# 1. Connect to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# 2. Install system dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y

# 3. Clone the repository
git clone https://github.com/YOUR_USERNAME/Chairpal_Chatbot.git
cd Chairpal_Chatbot

# 4. Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Download the model from Google Drive
pip install gdown
gdown "GOOGLE_DRIVE_SHARE_LINK" -O models/intent_classifier.ftz

# 7. Set environment variables
export CHAIRPAL_CORS_ORIGINS="*"
export PYTHONIOENCODING="utf-8"

# 8. Run the server
python main.py
```

The API will be available at `http://YOUR_EC2_IP:5000`.

---

## Running as a Permanent Service (systemd)

To keep the server running after SSH disconnect and auto-restart on crash:

```bash
sudo nano /etc/systemd/system/chairpal.service
```

Paste the following:

```ini
[Unit]
Description=Chairpal Chatbot API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Chairpal_Chatbot
Environment="CHAIRPAL_CORS_ORIGINS=*"
Environment="PYTHONIOENCODING=utf-8"
ExecStart=/home/ubuntu/Chairpal_Chatbot/.venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable chairpal
sudo systemctl start chairpal

# Verify it is running
sudo systemctl status chairpal
```

---

## Verify the Deployment

```bash
curl -X POST http://YOUR_EC2_IP:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": {"text": "ازاي اربط الكرسي"}, "user": {"id": 1, "full_name": "Test"}}'
```

Expected response:
```json
{
  "response": "لربط الكرسي المتحرك بالتطبيق...",
  "intent": "connect_wheelchair",
  "confidence": 0.97,
  "language": "ar"
}
```

---

## Updating the Server (After Retraining)

When new data is collected and the model is retrained, only **3 commands** are needed:

```bash
# 1. Pull updated code and dataset
git pull

# 2. Replace the model with the new version
gdown "NEW_GOOGLE_DRIVE_LINK" -O models/intent_classifier.ftz

# 3. Restart the service
sudo systemctl restart chairpal
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app entry point (Port 5000) |
| `models/intent_classifier.ftz` | Trained model — download from Google Drive |
| `data/merged_dataset.jsonl` | Main Q&A dataset (in repo) |
| `data/semantic_index.pkl` | Precomputed semantic search index (in repo) |
| `config/intent_overrides.yaml` | Rule-based intent override config |
| `config/health_thresholds.json` | Health alert thresholds |
