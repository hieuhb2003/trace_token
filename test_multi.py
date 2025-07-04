import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoints
API_PORT_GPU0 = os.getenv("API_PORT_GPU0", "9000")
API_PORT_GPU1 = os.getenv("API_PORT_GPU1", "9001")
API_URL_GPU0 = f"http://localhost:{API_PORT_GPU0}"
API_URL_GPU1 = f"http://localhost:{API_PORT_GPU1}"

PROJECT_NAME_GPU0 = os.getenv("PROJECT_NAME_GPU0", "project-gpu0")
PROJECT_NAME_GPU1 = os.getenv("PROJECT_NAME_GPU1", "project-gpu1")

def test_chat_api(api_url, project_name, gpu_name):
    """Test chat API with Langfuse tracing"""
    
    # Create a unique trace ID for this request
    trace_id = f"{project_name}-{uuid.uuid4().hex[:8]}"
    
    # Test data
    chat_data = {
        "messages": [
            {"role": "user", "content": f"Hello! I'm testing {gpu_name}. How are you today?"}
        ],
        "max_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "trace_id": trace_id
    }
    
    print(f"\n=== Testing {gpu_name} API at {api_url} ===")
    print(f"Project: {project_name}")
    print(f"Trace ID: {trace_id}")
    
    try:
        # Test health check
        health_response = requests.get(f"{api_url}/health")
        print(f"Health check: {health_response.json()}")
        
        # Test chat endpoint
        response = requests.post(
            f"{api_url}/chat",
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

def test_openai_compatible(api_url, gpu_name):
    """Test OpenAI-compatible endpoint"""
    
    print(f"\n=== Testing {gpu_name} OpenAI-compatible API ===")
    
    try:
        response = requests.post(
            f"{api_url}/v1/chat/completions",
            json={
                "model": f"qwen2.5-7b-it-{gpu_name.lower()}",
                "messages": [
                    {"role": "user", "content": f"Say hello from {gpu_name} in Vietnamese"}
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

def test_load_balancing():
    """Test load balancing between GPUs"""
    
    print(f"\n=== Testing Load Balancing ===")
    
    # Test both GPUs with same request
    test_data = {
        "messages": [
            {"role": "user", "content": "What GPU are you running on?"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    for i, (api_url, gpu_name) in enumerate([(API_URL_GPU0, "GPU0"), (API_URL_GPU1, "GPU1")]):
        try:
            response = requests.post(
                f"{api_url}/chat",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {gpu_name}: {result['response'][:100]}...")
            else:
                print(f"❌ {gpu_name}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {gpu_name}: Exception {e}")

if __name__ == "__main__":
    print("🚀 Testing Multi-GPU vLLM API with Langfuse Cloud Integration")
    
    # Test both GPUs
    test_chat_api(API_URL_GPU0, PROJECT_NAME_GPU0, "GPU0")
    test_chat_api(API_URL_GPU1, PROJECT_NAME_GPU1, "GPU1")
    
    # Test OpenAI-compatible endpoints
    test_openai_compatible(API_URL_GPU0, "GPU0")
    test_openai_compatible(API_URL_GPU1, "GPU1")
    
    # Test load balancing
    test_load_balancing()
    
    print(f"\n📊 Check Langfuse dashboard at {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')} to see traces!")
    print(f"🔗 API GPU0: http://localhost:{API_PORT_GPU0}")
    print(f"🔗 API GPU1: http://localhost:{API_PORT_GPU1}")
    print(f"🔗 Direct vLLM GPU0: http://localhost:8000")
    print(f"🔗 Direct vLLM GPU1: http://localhost:8001") 