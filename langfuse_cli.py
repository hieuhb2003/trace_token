#!/usr/bin/env python3
"""
Langfuse CLI Tool - Xem traces từ terminal
Sử dụng khi không có GUI để truy cập Langfuse dashboard
"""

import requests
import json
import argparse
from datetime import datetime, timedelta
from tabulate import tabulate
import os

class LangfuseCLI:
    def __init__(self, host="http://localhost:3000"):
        self.host = host
        self.base_url = f"{host}/api/public"
        
    def get_traces(self, limit=20, days=1):
        """Lấy danh sách traces"""
        try:
            # Tính thời gian từ X ngày trước
            since = datetime.now() - timedelta(days=days)
            
            url = f"{self.base_url}/traces"
            params = {
                "limit": limit,
                "from": since.isoformat(),
                "orderBy": "timestamp",
                "orderDirection": "desc"
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return None
    
    def get_trace_details(self, trace_id):
        """Lấy chi tiết của một trace"""
        try:
            url = f"{self.base_url}/traces/{trace_id}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return None
    
    def get_observations(self, trace_id):
        """Lấy observations của một trace"""
        try:
            url = f"{self.base_url}/traces/{trace_id}/observations"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return None
    
    def display_traces(self, traces):
        """Hiển thị danh sách traces dạng table"""
        if not traces or not traces.get('data'):
            print("📭 No traces found")
            return
        
        table_data = []
        for trace in traces['data']:
            # Tính token usage - hiển thị prompt và completion tokens riêng biệt
            token_usage = "N/A"
            if trace.get('output') and isinstance(trace['output'], dict):
                if 'usage' in trace['output']:
                    usage = trace['output']['usage']
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    completion_tokens = usage.get('completion_tokens', 0)
                    total_tokens = usage.get('total_tokens', 0)
                    token_usage = f"P:{prompt_tokens} C:{completion_tokens} T:{total_tokens}"
            
            # Format timestamp
            timestamp = trace.get('timestamp', 'N/A')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
                    table_data.append([
            trace.get('id', 'N/A')[:12] + '...',
            trace.get('name', 'N/A'),
            timestamp,
            token_usage,
            trace.get('status', 'N/A'),
            trace.get('metadata', {}).get('project', 'N/A')
        ])
        
        headers = ['Trace ID', 'Name', 'Timestamp', 'Token Usage', 'Status', 'Project']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        print(f"\n📊 Total traces: {len(table_data)}")
    
    def display_trace_detail(self, trace):
        """Hiển thị chi tiết trace"""
        if not trace:
            return
        
        print(f"\n🔍 Trace Details: {trace.get('id', 'N/A')}")
        print("=" * 60)
        
        # Basic info
        print(f"📝 Name: {trace.get('name', 'N/A')}")
        print(f"⏰ Timestamp: {trace.get('timestamp', 'N/A')}")
        print(f"📊 Status: {trace.get('status', 'N/A')}")
        print(f"🏷️  Project: {trace.get('metadata', {}).get('project', 'N/A')}")
        
        # Input
        if trace.get('input'):
            print(f"\n📥 Input:")
            if isinstance(trace['input'], dict):
                if 'messages' in trace['input']:
                    for i, msg in enumerate(trace['input']['messages']):
                        role = msg.get('role', 'unknown')
                        content = msg.get('content', '')[:100]
                        print(f"   {i+1}. [{role}]: {content}...")
                
                if 'usage' in trace['input']:
                    usage = trace['input']['usage']
                    print(f"   📊 Input Usage: {usage}")
            else:
                print(f"   {str(trace['input'])[:200]}...")
        
        # Output
        if trace.get('output'):
            print(f"\n📤 Output:")
            if isinstance(trace['output'], dict):
                if 'response' in trace['output']:
                    response = trace['output']['response'][:200]
                    print(f"   🤖 Response: {response}...")
                if 'usage' in trace['output']:
                    usage = trace['output']['usage']
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    completion_tokens = usage.get('completion_tokens', 0)
                    total_tokens = usage.get('total_tokens', 0)
                    print(f"   📊 Token Usage:")
                    print(f"      Prompt tokens: {prompt_tokens}")
                    print(f"      Completion tokens: {completion_tokens}")
                    print(f"      Total tokens: {total_tokens}")
            else:
                print(f"   {str(trace['output'])[:200]}...")
        
        # Metadata
        if trace.get('metadata'):
            print(f"\n🏷️  Metadata:")
            for key, value in trace['metadata'].items():
                print(f"   {key}: {value}")

def main():
    parser = argparse.ArgumentParser(description='Langfuse CLI Tool')
    parser.add_argument('--host', default='http://localhost:3000', help='Langfuse host')
    parser.add_argument('--limit', type=int, default=20, help='Number of traces to show')
    parser.add_argument('--days', type=int, default=1, help='Days back to search')
    parser.add_argument('--trace-id', help='Show details of specific trace ID')
    
    args = parser.parse_args()
    
    cli = LangfuseCLI(args.host)
    
    if args.trace_id:
        # Show specific trace details
        trace = cli.get_trace_details(args.trace_id)
        cli.display_trace_detail(trace)
    else:
        # Show list of traces
        print(f"🔍 Fetching traces from {args.host}...")
        traces = cli.get_traces(limit=args.limit, days=args.days)
        cli.display_traces(traces)
        
        if traces and traces.get('data'):
            print(f"\n💡 Use --trace-id <ID> to see details of a specific trace")
            print(f"   Example: python langfuse_cli.py --trace-id {traces['data'][0]['id']}")

if __name__ == "__main__":
    main() 