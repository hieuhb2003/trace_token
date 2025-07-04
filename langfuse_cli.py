#!/usr/bin/env python3
"""
Langfuse CLI Tool - Xem traces và token usage từ terminal
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
    
    def get_total_token_usage(self, days=30):
        """Lấy tổng token usage từ tất cả traces"""
        try:
            # Tính thời gian từ X ngày trước
            since = datetime.now() - timedelta(days=days)
            
            url = f"{self.base_url}/traces"
            params = {
                "limit": 1000,  # Lấy nhiều traces
                "from": since.isoformat(),
                "orderBy": "timestamp",
                "orderDirection": "desc"
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                traces = response.json()
                return self.calculate_total_usage(traces)
            else:
                print(f"❌ Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return None
    
    def calculate_total_usage(self, traces):
        """Tính tổng token usage từ traces"""
        if not traces or not traces.get('data'):
            return {
                'total_prompt_tokens': 0,
                'total_completion_tokens': 0,
                'total_tokens': 0,
                'total_requests': 0,
                'projects': {}
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
            'projects': projects
        }
    
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
    
    def display_total_usage(self, usage_data):
        """Hiển thị tổng token usage"""
        if not usage_data:
            print("❌ Không thể lấy dữ liệu token usage")
            return
        
        print("\n" + "=" * 60)
        print("📊 TỔNG TOKEN USAGE TRONG DATABASE")
        print("=" * 60)
        
        print(f"🔢 Tổng số requests: {usage_data['total_requests']:,}")
        print(f"📥 Tổng prompt tokens: {usage_data['total_prompt_tokens']:,}")
        print(f"📤 Tổng completion tokens: {usage_data['total_completion_tokens']:,}")
        print(f"📊 Tổng tokens: {usage_data['total_tokens']:,}")
        
        if usage_data['total_requests'] > 0:
            avg_prompt = usage_data['total_prompt_tokens'] / usage_data['total_requests']
            avg_completion = usage_data['total_completion_tokens'] / usage_data['total_requests']
            avg_total = usage_data['total_tokens'] / usage_data['total_requests']
            
            print(f"\n📈 Trung bình mỗi request:")
            print(f"   Prompt tokens: {avg_prompt:.1f}")
            print(f"   Completion tokens: {avg_completion:.1f}")
            print(f"   Total tokens: {avg_total:.1f}")
        
        # Hiển thị theo project
        if usage_data['projects']:
            print(f"\n🏷️  Token Usage theo Project:")
            project_data = []
            for project, data in usage_data['projects'].items():
                project_data.append([
                    project,
                    f"{data['requests']:,}",
                    f"{data['prompt_tokens']:,}",
                    f"{data['completion_tokens']:,}",
                    f"{data['prompt_tokens'] + data['completion_tokens']:,}"
                ])
            
            headers = ['Project', 'Requests', 'Prompt Tokens', 'Completion Tokens', 'Total Tokens']
            print(tabulate(project_data, headers=headers, tablefmt='grid'))

def main():
    parser = argparse.ArgumentParser(description='Langfuse CLI Tool')
    parser.add_argument('--host', default='http://localhost:3000', help='Langfuse host')
    parser.add_argument('--limit', type=int, default=20, help='Number of traces to show')
    parser.add_argument('--days', type=int, default=1, help='Days back to search')
    parser.add_argument('--trace-id', help='Show details of specific trace ID')
    parser.add_argument('--total-usage', action='store_true', help='Show total token usage from database')
    
    args = parser.parse_args()
    
    cli = LangfuseCLI(args.host)
    
    if args.total_usage:
        # Show total token usage
        print(f"🔍 Calculating total token usage from {args.host}...")
        usage_data = cli.get_total_token_usage(days=args.days)
        cli.display_total_usage(usage_data)
    elif args.trace_id:
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
            print(f"\n💡 Use --total-usage to see total token usage from database")
            print(f"   Example: python langfuse_cli.py --total-usage --days 30")

if __name__ == "__main__":
    main() 