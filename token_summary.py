#!/usr/bin/env python3
"""
Token Summary Script - Query tổng token usage từ Langfuse database
Sử dụng để xem nhanh tổng số token in/out trong database
"""

import requests
import json
from datetime import datetime, timedelta
import argparse

def get_token_summary(host="http://localhost:3000", days=30):
    """Lấy tổng token usage từ database"""
    
    try:
        # Tính thời gian từ X ngày trước
        since = datetime.now() - timedelta(days=days)
        
        url = f"{host}/api/public/traces"
        params = {
            "limit": 1000,  # Lấy nhiều traces
            "from": since.isoformat(),
            "orderBy": "timestamp",
            "orderDirection": "desc"
        }
        
        print(f"🔍 Querying traces from {host} (last {days} days)...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            traces = response.json()
            return calculate_summary(traces, days)
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def calculate_summary(traces, days):
    """Tính toán tổng token usage"""
    
    if not traces or not traces.get('data'):
        return {
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'total_tokens': 0,
            'total_requests': 0,
            'projects': {},
            'days': days
        }
    
    total_prompt = 0
    total_completion = 0
    total_requests = 0
    projects = {}
    
    for trace in traces['data']:
        if trace.get('output') and isinstance(trace['output'], dict):
            if 'usage' in trace['output']:
                usage = trace['output']['usage']
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                
                total_prompt += prompt_tokens
                total_completion += completion_tokens
                total_requests += 1
                
                # Tính theo project
                project = trace.get('metadata', {}).get('project', 'unknown')
                if project not in projects:
                    projects[project] = {
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'requests': 0
                    }
                projects[project]['prompt_tokens'] += prompt_tokens
                projects[project]['completion_tokens'] += completion_tokens
                projects[project]['requests'] += 1
    
    return {
        'total_prompt_tokens': total_prompt,
        'total_completion_tokens': total_completion,
        'total_tokens': total_prompt + total_completion,
        'total_requests': total_requests,
        'projects': projects,
        'days': days
    }

def display_summary(summary):
    """Hiển thị tổng token usage"""
    
    if not summary:
        print("❌ Không thể lấy dữ liệu token usage")
        return
    
    print("\n" + "=" * 60)
    print("📊 TỔNG TOKEN USAGE TRONG DATABASE")
    print("=" * 60)
    
    print(f"📅 Thời gian: {summary['days']} ngày gần nhất")
    print(f"🔢 Tổng số requests: {summary['total_requests']:,}")
    print(f"📥 Tổng prompt tokens (IN): {summary['total_prompt_tokens']:,}")
    print(f"📤 Tổng completion tokens (OUT): {summary['total_completion_tokens']:,}")
    print(f"📊 Tổng tokens: {summary['total_tokens']:,}")
    
    if summary['total_requests'] > 0:
        avg_prompt = summary['total_prompt_tokens'] / summary['total_requests']
        avg_completion = summary['total_completion_tokens'] / summary['total_requests']
        avg_total = summary['total_tokens'] / summary['total_requests']
        
        print(f"\n📈 Trung bình mỗi request:")
        print(f"   Prompt tokens (IN): {avg_prompt:.1f}")
        print(f"   Completion tokens (OUT): {avg_completion:.1f}")
        print(f"   Total tokens: {avg_total:.1f}")
    
    # Hiển thị theo project
    if summary['projects']:
        print(f"\n🏷️  Token Usage theo Project:")
        for project, data in summary['projects'].items():
            total_project = data['prompt_tokens'] + data['completion_tokens']
            print(f"   {project}:")
            print(f"     Requests: {data['requests']:,}")
            print(f"     Prompt tokens (IN): {data['prompt_tokens']:,}")
            print(f"     Completion tokens (OUT): {data['completion_tokens']:,}")
            print(f"     Total tokens: {total_project:,}")
            print()
    
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='Token Summary - Query tổng token usage')
    parser.add_argument('--host', default='http://localhost:3000', help='Langfuse host')
    parser.add_argument('--days', type=int, default=30, help='Số ngày gần nhất để query')
    
    args = parser.parse_args()
    
    summary = get_token_summary(args.host, args.days)
    display_summary(summary)

if __name__ == "__main__":
    main() 