# vLLM API với Langfuse Integration

Hệ thống này cung cấp 2 API vLLM riêng biệt chạy trên 2 GPU khác nhau, tích hợp với Langfuse để trace token usage.

## 🚀 Tính năng

- **2 API riêng biệt**: Mỗi API chạy trên 1 GPU riêng
- **Qwen 2.5 7B**: Model được tối ưu với GPU memory utilization 0.7
- **Langfuse Integration**: Tự động trace token usage và request/response
- **Docker Compose**: Dễ dàng deploy và quản lý
- **Local Langfuse**: Chạy Langfuse locally để quản lý traces

## 📋 Yêu cầu hệ thống

- Docker và Docker Compose
- NVIDIA GPU với CUDA support
- 2 GPU (mỗi GPU cho 1 API)
- NVIDIA Container Toolkit

## 🛠️ Setup

### 1. Clone và cài đặt

```bash
git clone <your-repo>
cd <your-repo>
```

### 2. Cấu hình environment

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với thông tin Langfuse của bạn:

```env
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 3. Khởi chạy hệ thống

```bash
docker-compose up -d
```

Hệ thống sẽ:

- Tải model Qwen 2.5 7B lên 2 GPU riêng biệt
- Khởi chạy 2 API server trên port 8000 và 8001
- Khởi chạy Langfuse dashboard trên port 3000

## 🔗 API Endpoints

### API 1 (GPU 0): http://localhost:8000

### API 2 (GPU 1): http://localhost:8001

### Health Check

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Chat API

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "max_tokens": 100,
    "temperature": 0.7,
    "trace_id": "my-trace-id"
  }'
```

### Generate API

```bash
curl -X POST "http://localhost:8000/generate?prompt=Hello&max_tokens=50&temperature=0.7"
```

## 📊 Langfuse Dashboard

Truy cập Langfuse dashboard tại: http://localhost:3000

Tại đây bạn có thể:

- Xem tất cả traces từ cả 2 API
- Theo dõi token usage
- Phân tích performance
- Filter theo project (project-1, project-2)

## 🧪 Test

Chạy test client để kiểm tra hệ thống:

```bash
python test_client.py
```

## 📁 Cấu trúc project

```
.
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile.vllm            # Dockerfile cho vLLM container
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── app/
│   └── main.py               # vLLM API server với Langfuse
├── test_client.py            # Test script
└── README.md                 # Documentation
```

## 🔧 Cấu hình

### GPU Memory Utilization

Chỉnh sửa `GPU_MEMORY_UTILIZATION` trong docker-compose.yml hoặc .env file:

```yaml
environment:
  - GPU_MEMORY_UTILIZATION=0.7 # Sử dụng 70% GPU memory
```

### Model Configuration

Thay đổi model trong docker-compose.yml:

```yaml
environment:
  - MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
```

### Project Names

Mỗi API có project name riêng để phân biệt trong Langfuse:

```yaml
environment:
  - PROJECT_NAME=project-1 # Cho API 1
  - PROJECT_NAME=project-2 # Cho API 2
```

## 🚨 Troubleshooting

### GPU không được nhận

```bash
# Kiểm tra NVIDIA Container Toolkit
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi
```

### Model loading chậm

- Lần đầu sẽ tải model từ HuggingFace (có thể mất vài phút)
- Model sẽ được cache trong volume

### Langfuse connection error

- Kiểm tra LANGFUSE_PUBLIC_KEY và LANGFUSE_SECRET_KEY
- Đảm bảo internet connection để kết nối Langfuse cloud

## 📈 Monitoring

### Logs

```bash
# Xem logs của tất cả services
docker-compose logs -f

# Xem logs của specific service
docker-compose logs -f vllm-api-1
docker-compose logs -f vllm-api-2
```

### GPU Usage

```bash
nvidia-smi
```

### API Status

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

## 🔄 Restart Services

```bash
# Restart tất cả
docker-compose restart

# Restart specific service
docker-compose restart vllm-api-1
docker-compose restart vllm-api-2
```

## 🛑 Stop Services

```bash
docker-compose down
```

## 📝 Notes

- Mỗi API chạy độc lập trên 1 GPU riêng
- Token usage được track tự động qua Langfuse
- Model được cache để tăng tốc độ load lần sau
- Có thể scale thêm API bằng cách thêm service trong docker-compose.yml
