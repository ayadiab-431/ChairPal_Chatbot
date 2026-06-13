import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Union, List, Literal

from chatbot.chatbot import ChairpalChatbot

app = FastAPI(
    title="♿ Chairpal Chatbot API",
    description="Production API endpoint for smart wheelchair assistant, integrating FastText intent classification, conversation memory, and personalized health sensor feedback.",
    version="1.0.0"
)

def parse_cors_origins() -> List[str]:
    origins = os.getenv("CHAIRPAL_CORS_ORIGINS", "*")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


# 1. Enable CORS for cross-origin mobile/web requests from Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Initialize Chatbot Orchestrator globally
try:
    chatbot = ChairpalChatbot()
    print("Chatbot initialized successfully with FastText supervised model.")
except Exception as e:
    print(f"Error initializing chatbot: {e}")
    chatbot = None

# 3. Serve premium chat simulator web interface
@app.get("/", response_class=FileResponse)
def get_chat_simulator():
    """Serves the state-of-the-art Web Chat Simulator UI."""
    return FileResponse("templates/index.html")

# 4. Pydantic request models
from schemas import *

# 5. API Endpoints
@app.get("/health")
def health_check():
    """AWS ALB and health check endpoint."""
    if chatbot is None:
        raise HTTPException(status_code=500, detail="Chatbot system is unhealthy/not initialized.")
    return {"status": "healthy", "model": "FastText Supervised (Egyptian Arabic & English)"}

@app.post("/chat")
def chat_endpoint(request: Union[RichChatRequest, dict]):
    """
    Exposes chat capability to Flutter mobile and web clients.
    Accepts either the structured RichChatRequest model or a raw dictionary
    matching the backend data schema. Raw dictionaries are transformed into
    RichChatRequest before processing.
    """
    # Transform raw dict if necessary
    if isinstance(request, dict):
        from scripts.transform_user_data import transform_to_rich_request
        request = transform_to_rich_request(request)
    if chatbot is None:
        raise HTTPException(status_code=500, detail="Chatbot model not initialized on server.")
        
    try:
        # Determine the schema type and construct query & user_context
        if isinstance(request, RichChatRequest):
            query = request.message.text
            user_context = request.dict(exclude={"message"})
            user_id = str(request.user.id) if request.user and request.user.id is not None else "anonymous"
            
            # Map user name for backward compatibility/personalization
            if request.user and request.user.full_name:
                user_context["name"] = request.user.full_name
        else:
            # Fallback for unexpected type (should not occur)
            raise HTTPException(status_code=400, detail="Invalid request format.")
        
        # Run chatbot inference pipeline
        result = chatbot.respond(query, user_context=user_context, user_id=user_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

if __name__ == "__main__":
    # Start uvicorn server locally on port 8001
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=False)
