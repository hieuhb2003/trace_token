# 🖥️ Hướng dẫn sử dụng vLLM + Langfuse trên Server

## 🎯 Tình huống

- Bạn đang ở trên server Linux
- Chỉ có terminal, không có GUI
- Muốn xem traces từ Langfuse local

## 🚀 Setup

### 1. Khởi chạy hệ thống

```bash
# Start tất cả services
docker-compose up -d

# Kiểm tra status
docker-compose ps
```

### 2. Kiểm tra services đang chạy

```bash
# Xem logs
docker-compose logs -f

# Kiểm tra ports
netstat -tlnp | grep -E ':(8000|8001|3000)'
```

## 📊 Cách xem traces từ terminal

### Option 1: Sử dụng CLI tool (Khuyến nghị)

```bash
# Cài đặt dependencies
pip install tabulate

# Xem danh sách traces
python langfuse_cli.py

# Xem chi tiết một trace cụ thể
python langfuse_cli.py --trace-id <trace_id>

# Xem traces trong 7 ngày qua
python langfuse_cli.py --days 7

# Xem 50 traces gần nhất
python langfuse_cli.py --limit 50
```

### Option 2: Sử dụng curl

```bash
# Lấy danh sách traces
curl "http://localhost:3000/api/public/traces?limit=10" | jq

# Lấy chi tiết trace
curl "http://localhost:3000/api/public/traces/<trace_id>" | jq

# Lấy observations
curl "http://localhost:3000/api/public/traces/<trace_id>/observations" | jq
```

### Option 3: Port forwarding (nếu có SSH access)

```bash
# Từ máy local, SSH với port forwarding
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 -L 8001:localhost:8001 user@server_ip

# Sau đó truy cập từ browser local:
# http://localhost:3000 (Langfuse dashboard)
# http://localhost:8000 (API 1)
# http://localhost:8001 (API 2)
```

## 🧪 Test API

### Test nhanh

```bash
# Test API 1
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50,
    "trace_id": "test-1"
  }'

# Test API 2
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50,
    "trace_id": "test-2"
  }'
```

### Test với Python

```bash
python quick_test.py
```

## 📈 Monitoring từ terminal

### 1. Xem logs real-time

```bash
# Tất cả services
docker-compose logs -f

# Chỉ vLLM API 1
docker-compose logs -f vllm-api-1

# Chỉ vLLM API 2
docker-compose logs -f vllm-api-2

# Chỉ Langfuse
docker-compose logs -f langfuse
```

### 2. Kiểm tra GPU usage

```bash
# Xem GPU usage
nvidia-smi

# Monitor GPU real-time
watch -n 1 nvidia-smi
```

### 3. Kiểm tra API health

```bash
# Health check API 1
curl http://localhost:8000/health

# Health check API 2
curl http://localhost:8001/health
```

## 🔍 Xem traces chi tiết

### Sử dụng CLI tool

```bash
# Xem danh sách traces
python langfuse_cli.py

# Output sẽ hiển thị:
# +------------+------------------+---------------------+--------+--------+----------+
# | Trace ID   | Name             | Timestamp           | Tokens | Status | Project  |
# +------------+------------------+---------------------+--------+--------+----------+
# | project-1- | project-1-chat   | 2024-01-15 10:30:15 | 45     | OK     | project-1|
# | project-2- | project-2-chat   | 2024-01-15 10:30:20 | 67     | OK     | project-2|
# +------------+------------------+---------------------+--------+--------+----------+

# Xem chi tiết trace cụ thể
python langfuse_cli.py --trace-id project-1-abc123
```

### Sử dụng jq để format JSON

```bash
# Cài đặt jq nếu chưa có
sudo apt-get install jq

# Lấy traces và format đẹp
curl -s "http://localhost:3000/api/public/traces?limit=5" | jq '.data[] | {id, name, timestamp, status}'
```

## 🛠️ Troubleshooting

### Langfuse không khởi động

```bash
# Kiểm tra logs
docker-compose logs langfuse

# Restart service
docker-compose restart langfuse
```

### API không response

```bash
# Kiểm tra logs
docker-compose logs vllm-api-1
docker-compose logs vllm-api-2

# Kiểm tra GPU
nvidia-smi

# Restart services
docker-compose restart vllm-api-1 vllm-api-2
```

### Không thấy traces

```bash
# Kiểm tra kết nối giữa API và Langfuse
docker-compose logs vllm-api-1 | grep -i langfuse
docker-compose logs vllm-api-2 | grep -i langfuse

# Test API để tạo trace mới
python quick_test.py
```

## 📝 Script hữu ích

### Tạo file `monitor.sh`

```bash
#!/bin/bash
echo "=== vLLM + Langfuse Monitor ==="
echo "Time: $(date)"
echo ""

echo "=== GPU Status ==="
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv

echo ""
echo "=== API Status ==="
curl -s http://localhost:8000/health | jq -r '.status'
curl -s http://localhost:8001/health | jq -r '.status'

echo ""
echo "=== Recent Traces ==="
python langfuse_cli.py --limit 5
```

### Chạy monitor

```bash
chmod +x monitor.sh
./monitor.sh
```

## 🎯 Tips

1. **Sử dụng tmux/screen** để chạy multiple sessions
2. **Log rotation** để tránh disk full
3. **Regular backup** của PostgreSQL data
4. **Monitor disk space** thường xuyên
5. **Set up alerts** cho GPU memory usage

## 📊 Metrics quan trọng

- **Token usage per request**
- **API response time**
- **GPU memory utilization**
- **Number of traces per project**
- **Error rate**
