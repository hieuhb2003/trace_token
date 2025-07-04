#!/bin/bash

echo "🚀 Starting vLLM API with Langfuse Integration..."

# Check if .env file exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "⚠️  .env file not found. Creating from .env.example..."
        cp .env.example .env
        echo "📝 Please edit .env file with your Langfuse credentials"
        echo "   Then run this script again."
        exit 1
    else
        echo "❌ .env file not found and .env.example doesn't exist."
        echo "📝 Please create .env file with your Langfuse credentials:"
        echo "   LANGFUSE_PUBLIC_KEY=your_key"
        echo "   LANGFUSE_SECRET_KEY=your_secret"
        echo "   LANGFUSE_HOST=https://cloud.langfuse.com"
        exit 1
    fi
fi

# Check if NVIDIA Container Toolkit is available
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA GPU not detected. Please ensure NVIDIA drivers are installed."
    exit 1
fi

# Check GPU count
GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
echo "🔍 Detected $GPU_COUNT GPU(s)"

if [ $GPU_COUNT -lt 2 ]; then
    echo "⚠️  Warning: Less than 2 GPUs detected. Some services may not start properly."
fi

# Create necessary directories
mkdir -p models logs

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."

# Check API 1
if curl -s --max-time 5 http://localhost:9010/v1/models > /dev/null; then
    echo "✅ API 1 (GPU 0) is running at http://localhost:9010"
elif curl -s --max-time 5 http://localhost:9010/health > /dev/null; then
    echo "✅ API 1 (GPU 0) is running at http://localhost:9010"
else
    echo "❌ API 1 is not responding"
fi

# Check API 2
if curl -s --max-time 5 http://localhost:9011/v1/models > /dev/null; then
    echo "✅ API 2 (GPU 1) is running at http://localhost:9011"
elif curl -s --max-time 5 http://localhost:9011/health > /dev/null; then
    echo "✅ API 2 (GPU 1) is running at http://localhost:9011"
else
    echo "❌ API 2 is not responding"
fi

# Check Langfuse
if curl -s --max-time 5 http://localhost:3010 > /dev/null; then
    echo "✅ Langfuse dashboard is running at http://localhost:3010"
else
    echo "❌ Langfuse dashboard is not responding"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📊 Available endpoints:"
echo "   API 1 (GPU 0): http://localhost:9010"
echo "   API 2 (GPU 1): http://localhost:9011"
echo "   Langfuse: http://localhost:3010"
echo ""
echo "🧪 Run test: python test_client.py"
echo "📋 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down" 