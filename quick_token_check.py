#!/usr/bin/env python3
"""
Quick Token Check - Xem nhanh tổng token usage
Sử dụng để check nhanh token in/out trong database
"""

import requests
from datetime import datetime, timedelta

def quick_token_check():
    """Xem nhanh tổng token usage"""
    
    try:
        # Query traces từ 30 ngày qua
        since = datetime.now() - timedelta(days=30)
        
        url = "http://localhost:3000/api/public/traces"
        params = {
            "limit": 1000,
            "from": since.isoformat(),
            "orderBy": "timestamp",
            "orderDirection": "desc"
        }
        
        print("🔍 Querying token usage...")
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            traces = response.json()
            
            total_prompt = 0
            total_completion = 0
            total_requests = 0
            
            for trace in traces.get('data', []):
                if trace.get('output') and isinstance(trace['output'], dict):
                    if 'usage' in trace['output']:
                        usage = trace['output']['usage']
                        total_prompt += usage.get('prompt_tokens', 0)
                        total_completion += usage.get('completion_tokens', 0)
                        total_requests += 1
            
            print("\n📊 TOKEN USAGE SUMMARY (30 days)")
            print("=" * 40)
            print(f"📥 Total IN (prompt): {total_prompt:,}")
            print(f"📤 Total OUT (completion): {total_completion:,}")
            print(f"📊 Total tokens: {total_prompt + total_completion:,}")
            print(f"🔢 Total requests: {total_requests:,}")
            
            if total_requests > 0:
                avg_in = total_prompt / total_requests
                avg_out = total_completion / total_requests
                print(f"📈 Avg IN per request: {avg_in:.1f}")
                print(f"📈 Avg OUT per request: {avg_out:.1f}")
            
            print("=" * 40)
            
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure Langfuse is running on http://localhost:3000")

if __name__ == "__main__":
    quick_token_check() 