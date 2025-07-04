import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoint
API_PORT = os.getenv("API_PORT", "9000")
API_URL = f"http://localhost:{API_PORT}"
PROJECT_NAME = os.getenv("PROJECT_NAME", "my-project")

def test_chat_api():
    """Test chat API with Langfuse tracing"""
    
    # Create a unique trace ID for this request
    trace_id = f"{PROJECT_NAME}-{uuid.uuid4().hex[:8]}"
    
    # Test data
    chat_data = {
        "messages": [
            {"role": "user", "content": "Hello! How are you today?"}
        ],
        "max_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "trace_id": trace_id
    }
    
    print(f"\n=== Testing API at {API_URL} ===")
    print(f"Project: {PROJECT_NAME}")
    print(f"Trace ID: {trace_id}")
    
    try:
        # Test health check
        health_response = requests.get(f"{API_URL}/health")
        print(f"Health check: {health_response.json()}")
        
        # Test chat endpoint
        response = requests.post(
            f"{API_URL}/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Response: {result['response']}")
            print(f"Usage: {result['usage']}")
            print(f"Trace ID: {result['trace_id']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_generate_api():
    """Test simple text generation API"""
    
    print(f"\n=== Testing Generate API ===")
    
    try:
        response = requests.post(
            f"{API_URL}/generate",
            params={
                "prompt": "Write a short poem about AI",
                "max_tokens": 50,
                "temperature": 0.8
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Response: {result['response']}")
            print(f"Usage: {result['usage']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_openai_compatible():
    """Test OpenAI-compatible endpoint"""
    
    print(f"\n=== Testing OpenAI-compatible API ===")
    
    try:
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            json={
                "model": "qwen2.5-7b-it",
                "messages": [
                    {"role": "user", "content": "Say hello in Vietnamese"}
                ],
                "max_tokens": 50,
                "temperature": 0.7
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Response: {result['choices'][0]['message']['content']}")
            print(f"Usage: {result['usage']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Testing Simple vLLM API with Langfuse Cloud Integration")
    
    # Test all endpoints
    test_chat_api()
    test_generate_api()
    test_openai_compatible()
    
    print(f"\n📊 Check Langfuse dashboard at {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')} to see traces!")
    print(f"🔗 API: http://localhost:{API_PORT}")
    print(f"🔗 Direct vLLM: http://localhost:8000") 