# 🚀 vLLM + Langfuse System

Hệ thống host LLM với vLLM và trace token usage qua Langfuse local.

## 🎯 Tính năng

- **2 API riêng biệt**: Mỗi API chạy trên 1 GPU riêng
- **Qwen 2.5 7B**: Model được tối ưu với GPU memory utilization 0.7
- **Langfuse Local**: Trace token usage local, không cần internet
- **Token Tracking**: Theo dõi riêng biệt prompt tokens và completion tokens
- **CLI Tools**: Xem traces và token usage từ terminal
- **Docker Compose**: Dễ dàng deploy và quản lý

## 📋 Yêu cầu hệ thống

- Docker và Docker Compose
- NVIDIA GPU với CUDA support
- 2 GPU (mỗi GPU cho 1 API)
- NVIDIA Container Toolkit

## 🛠️ Setup

### 1. Clone repository

```bash
git clone <your-repo>
cd vllm-langfuse-system
```

### 2. Cấu hình environment

```bash
cp .env.example .env
# Chỉnh sửa .env nếu cần
```

### 3. Khởi chạy hệ thống

```bash
# Sử dụng script
./start.sh

# Hoặc manual
docker-compose up -d
```

## 🔗 API Endpoints

### API 1 (GPU 0): http://localhost:8000

### API 2 (GPU 1): http://localhost:8001

### Langfuse Dashboard: http://localhost:3000

## 📊 Token Usage Tracking

### Xem traces từ terminal

```bash
# Xem danh sách traces
python langfuse_cli.py

# Xem chi tiết trace cụ thể
python langfuse_cli.py --trace-id <trace_id>

# Xem tổng token usage từ database
python langfuse_cli.py --total-usage

# Xem token usage trong 30 ngày qua
python langfuse_cli.py --total-usage --days 30
```

### Test API

```bash
# Test nhanh
python quick_test.py

# Test chi tiết
python test_client.py
```

## 📈 Monitoring

### Xem logs

```bash
# Tất cả services
docker-compose logs -f

# Chỉ vLLM API 1
docker-compose logs -f vllm-api-1

# Chỉ vLLM API 2
docker-compose logs -f vllm-api-2
```

### Kiểm tra GPU

```bash
nvidia-smi
```

### Health check

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

## 📁 Cấu trúc project

```
vllm-langfuse-system/
├── 📁 Docker & Deployment
│   ├── docker-compose.yml          # 🐳 Docker Compose config
│   ├── Dockerfile.vllm             # 🐳 Dockerfile cho vLLM
│   ├── requirements.txt            # 📦 Python dependencies
│   └── start.sh                    # 🚀 Script khởi chạy
│
├── 📁 Environment & Config
│   ├── .env                        # ⚙️ Environment variables
│   └── .env.example                # 📝 Template
│
├── 📁 Application
│   └── app/
│       └── main.py                 # 🐍 vLLM API server
│
├── 📁 Tools & Testing
│   ├── langfuse_cli.py             # 🔍 CLI tool xem traces
│   ├── quick_test.py               # ⚡ Test nhanh
│   └── test_client.py              # 🧪 Test chi tiết
│
└── 📁 Documentation
    ├── README.md                   # 📖 Hướng dẫn chính
    └── server_guide.md             # 🖥️ Hướng dẫn server
```

## 🎯 Token Usage Features

### 1. **Separate Tracking**

- **Prompt tokens**: Tokens trong input
- **Completion tokens**: Tokens trong response
- **Total tokens**: Tổng của prompt + completion

### 2. **Database Query**

```bash
# Xem tổng token usage
python langfuse_cli.py --total-usage

# Output:
# 📊 TỔNG TOKEN USAGE TRONG DATABASE
# 🔢 Tổng số requests: 1,234
# 📥 Tổng prompt tokens: 45,678
# 📤 Tổng completion tokens: 123,456
# 📊 Tổng tokens: 169,134
```

### 3. **Project-based Tracking**

- Phân biệt token usage theo project
- Theo dõi riêng biệt project-1 và project-2

## 🚨 Troubleshooting

### GPU không được nhận

```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi
```

### API không response

```bash
docker-compose logs vllm-api-1
docker-compose logs vllm-api-2
```

### Không thấy traces

```bash
python quick_test.py
python langfuse_cli.py --total-usage
```

## 🔄 Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

## 📝 Notes

- Model được cache để tăng tốc độ load
- Traces được lưu trong PostgreSQL local
- Có thể scale thêm API bằng cách thêm service
- Token usage được tính chính xác prompt vs completion
