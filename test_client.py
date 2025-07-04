import requests
import json
import uuid

# API endpoints
API_1_URL = "http://localhost:8000"
API_2_URL = "http://localhost:8001"

def test_chat_api(api_url, project_name):
    """Test chat API with Langfuse tracing"""
    
    # Create a unique trace ID for this request
    trace_id = f"{project_name}-{uuid.uuid4().hex[:8]}"
    
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
    
    print(f"\n=== Testing {project_name} API at {api_url} ===")
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

def test_generate_api(api_url, project_name):
    """Test simple text generation API"""
    
    print(f"\n=== Testing {project_name} Generate API ===")
    
    try:
        response = requests.post(
            f"{api_url}/generate",
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

if __name__ == "__main__":
    print("🚀 Testing vLLM APIs with Langfuse Integration")
    
    # Test both APIs
    test_chat_api(API_1_URL, "Project-1")
    test_chat_api(API_2_URL, "Project-2")
    
    # Test generate endpoints
    test_generate_api(API_1_URL, "Project-1")
    test_generate_api(API_2_URL, "Project-2")
    
    print("\n📊 Check Langfuse dashboard at http://localhost:3000 to see traces!")
    print("🔗 API 1: http://localhost:8000")
    print("🔗 API 2: http://localhost:8001") 