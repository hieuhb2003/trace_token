import os
import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vllm import LLM, SamplingParams
from langfuse import Langfuse
from langfuse.model import CreateTrace
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="vLLM API with Langfuse", version="1.0.0")

# Initialize Langfuse client
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "default-public-key"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY", "default-secret-key"),
    host=os.getenv("LANGFUSE_HOST", "http://langfuse:3000")
)

# Get environment variables
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
GPU_MEMORY_UTILIZATION = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.7"))
PROJECT_NAME = os.getenv("PROJECT_NAME", "default-project")

# Initialize LLM
logger.info(f"Loading model: {MODEL_NAME}")
llm = LLM(
    model=MODEL_NAME,
    gpu_memory_utilization=GPU_MEMORY_UTILIZATION,
    trust_remote_code=True
)

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
    logger.info(f"vLLM API server started with model: {MODEL_NAME}")
    logger.info(f"GPU memory utilization: {GPU_MEMORY_UTILIZATION}")
    logger.info(f"Project name: {PROJECT_NAME}")

@app.get("/")
async def root():
    return {
        "message": "vLLM API with Langfuse Integration",
        "model": MODEL_NAME,
        "project": PROJECT_NAME
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": MODEL_NAME}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Create trace if trace_id is provided
        trace_id = request.trace_id or f"{PROJECT_NAME}-{os.urandom(8).hex()}"
        
        # Format messages for Qwen
        formatted_prompt = ""
        for message in request.messages:
            if message.role == "user":
                formatted_prompt += f"<|im_start|>user\n{message.content}<|im_end|>\n"
            elif message.role == "assistant":
                formatted_prompt += f"<|im_start|>assistant\n{message.content}<|im_end|>\n"
        
        formatted_prompt += "<|im_start|>assistant\n"

        # Create sampling parameters
        sampling_params = SamplingParams(
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )

        # Generate response
        outputs = llm.generate([formatted_prompt], sampling_params)
        response_text = outputs[0].outputs[0].text.strip()

        # Get usage information - separate prompt and completion tokens
        # vLLM returns all token IDs including prompt and completion
        # We need to count prompt tokens from the original prompt
        prompt_tokens = len(llm.get_tokenizer().encode(formatted_prompt))
        completion_tokens = len(outputs[0].outputs[0].token_ids) - prompt_tokens
        
        usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }

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
                    "response": response_text,
                    "usage": usage
                },
                metadata={
                    "model": MODEL_NAME,
                    "project": PROJECT_NAME,
                    "gpu_memory_utilization": GPU_MEMORY_UTILIZATION
                }
            )
            langfuse.flush()
        except Exception as e:
            logger.warning(f"Failed to send trace to Langfuse: {e}")

        return ChatResponse(
            response=response_text,
            usage=usage,
            trace_id=trace_id
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_text(prompt: str, max_tokens: int = 1024, temperature: float = 0.7):
    try:
        # Create sampling parameters
        sampling_params = SamplingParams(
            max_tokens=max_tokens,
            temperature=temperature
        )

        # Generate response
        outputs = llm.generate([prompt], sampling_params)
        response_text = outputs[0].outputs[0].text.strip()

        # Get usage information - separate prompt and completion tokens
        prompt_tokens = len(llm.get_tokenizer().encode(prompt))
        completion_tokens = len(outputs[0].outputs[0].token_ids) - prompt_tokens
        
        usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }

        return {
            "response": response_text,
            "usage": usage
        }

    except Exception as e:
        logger.error(f"Error in generate endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 