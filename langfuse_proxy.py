#!/usr/bin/env python3
"""
Langfuse Proxy - Thêm Langfuse tracing vào vLLM API có sẵn
Proxy server để intercept requests và thêm token tracking
"""

import os
import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
from langfuse import Langfuse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="vLLM Langfuse Proxy", version="1.0.0")

# Initialize Langfuse client
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "default-public-key"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY", "default-secret-key"),
    host=os.getenv("LANGFUSE_HOST", "http://langfuse:3000")
)

# Get environment variables
PROJECT_NAME = os.getenv("PROJECT_NAME", "default-project")
VLLM_API_URL = os.getenv("VLLM_API_URL", "http://localhost:8000")

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 1024
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    trace_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    usage: dict
    trace_id: str

@app.on_event("startup")
async def startup_event():
    logger.info(f"Langfuse Proxy started for project: {PROJECT_NAME}")
    logger.info(f"vLLM API URL: {VLLM_API_URL}")

@app.get("/")
async def root():
    return {
        "message": "vLLM Langfuse Proxy",
        "project": PROJECT_NAME,
        "vllm_api": VLLM_API_URL
    }

@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{VLLM_API_URL}/health")
            if response.status_code == 200:
                return {"status": "healthy", "project": PROJECT_NAME}
            else:
                return {"status": "unhealthy", "vllm_status": response.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """Proxy chat completions với Langfuse tracing"""
    
    try:
        # Parse request body
        body = await request.json()
        
        # Create trace ID
        trace_id = body.get("trace_id") or f"{PROJECT_NAME}-{uuid.uuid4().hex[:8]}"
        
        # Extract messages for logging
        messages = body.get("messages", [])
        max_tokens = body.get("max_tokens", 1024)
        temperature = body.get("temperature", 0.7)
        
        logger.info(f"Processing request with trace_id: {trace_id}")
        
        # Forward request to vLLM API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{VLLM_API_URL}/v1/chat/completions",
                json=body,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract usage information
                usage = result.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
                
                # Get response content
                response_content = ""
                if result.get("choices") and len(result["choices"]) > 0:
                    response_content = result["choices"][0].get("message", {}).get("content", "")
                
                # Send trace to Langfuse
                try:
                    langfuse.trace(
                        id=trace_id,
                        name=f"{PROJECT_NAME}-chat",
                        input={
                            "messages": messages,
                            "max_tokens": max_tokens,
                            "temperature": temperature
                        },
                        output={
                            "response": response_content,
                            "usage": {
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": completion_tokens,
                                "total_tokens": total_tokens
                            }
                        },
                        metadata={
                            "project": PROJECT_NAME,
                            "vllm_api": VLLM_API_URL
                        }
                    )
                    langfuse.flush()
                    logger.info(f"Trace sent to Langfuse: {trace_id}")
                except Exception as e:
                    logger.warning(f"Failed to send trace to Langfuse: {e}")
                
                # Add trace_id to response
                result["trace_id"] = trace_id
                return result
            else:
                logger.error(f"vLLM API error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
    except Exception as e:
        logger.error(f"Error in chat_completions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    """Custom chat endpoint với Langfuse tracing"""
    
    try:
        # Create trace ID
        trace_id = request.trace_id or f"{PROJECT_NAME}-{uuid.uuid4().hex[:8]}"
        
        # Convert to OpenAI format
        openai_request = {
            "model": "qwen2.5-7b-it",
            "messages": [msg.dict() for msg in request.messages],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p
        }
        
        # Forward to vLLM API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{VLLM_API_URL}/v1/chat/completions",
                json=openai_request,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract usage and response
                usage = result.get("usage", {})
                response_content = ""
                if result.get("choices") and len(result["choices"]) > 0:
                    response_content = result["choices"][0].get("message", {}).get("content", "")
                
                # Send trace to Langfuse
                try:
                    langfuse.trace(
                        id=trace_id,
                        name=f"{PROJECT_NAME}-chat",
                        input={
                            "messages": [msg.dict() for msg in request.messages],
                            "max_tokens": request.max_tokens,
                            "temperature": request.temperature,
                            "top_p": request.top_p
                        },
                        output={
                            "response": response_content,
                            "usage": usage
                        },
                        metadata={
                            "project": PROJECT_NAME,
                            "vllm_api": VLLM_API_URL
                        }
                    )
                    langfuse.flush()
                except Exception as e:
                    logger.warning(f"Failed to send trace to Langfuse: {e}")
                
                return ChatResponse(
                    response=response_content,
                    usage=usage,
                    trace_id=trace_id
                )
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 