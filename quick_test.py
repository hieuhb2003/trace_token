# -*- coding: utf-8 -*-
"""
Quick Test Script cho Dynamic Clustering System
Test nhanh để kiểm tra hệ thống hoạt động đúng
"""

import requests
import json
import uuid
from datetime import datetime

def test_api_with_trace(api_url, project_name, message):
    """Test API và tạo trace với ID duy nhất"""
    
    # Tạo trace ID duy nhất
    trace_id = f"{project_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    print(f"\n🔗 Testing {project_name}")
    print(f"📍 API: {api_url}")
    print(f"🆔 Trace ID: {trace_id}")
    print(f"💬 Message: {message}")
    
    # Test data
    chat_data = {
        "messages": [
            {"role": "user", "content": message}
        ],
        "max_tokens": 150,
        "temperature": 0.7,
        "trace_id": trace_id
    }
    
    try:
        # Test chat endpoint
        response = requests.post(
            f"{api_url}/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"🤖 Response: {result['response'][:100]}...")
            print(f"📊 Token Usage:")
            print(f"   Prompt tokens: {result['usage']['prompt_tokens']}")
            print(f"   Completion tokens: {result['usage']['completion_tokens']}")
            print(f"   Total tokens: {result['usage']['total_tokens']}")
            print(f"🔍 Trace ID: {result['trace_id']}")
            print(f"🌐 View trace: http://localhost:3000/traces/{trace_id}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Testing vLLM APIs with Langfuse Cloud Integration")
    print("=" * 60)
    
    # Test messages cho từng project
    test_cases = [
        ("http://localhost:8000", "project-1", "Hãy giải thích về AI một cách đơn giản"),
        ("http://localhost:8001", "project-2", "Viết một bài thơ ngắn về công nghệ"),
        ("http://localhost:8000", "project-1", "Tính toán 15 + 27 x 3"),
        ("http://localhost:8001", "project-2", "Kể một câu chuyện ngắn về tình bạn")
    ]
    
    for api_url, project, message in test_cases:
        test_api_with_trace(api_url, project, message)
    
    print("\n" + "=" * 60)
    print("🎉 Test completed!")
    print("📊 Check traces at: http://localhost:3000")
    print("🔗 API 1: http://localhost:8000")
    print("🔗 API 2: http://localhost:8001")
    print("💡 Use: python langfuse_cli.py to view traces from terminal") 