#!/bin/bash

echo "🚀 Starting Multi-GPU vLLM API with Langfuse Cloud Integration..."

# Check if .env file exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "⚠️  .env file not found. Creating from .env.example..."
        cp .env.example .env
        echo "📝 Please edit .env file with your Langfuse credentials:"
        echo "   - LANGFUSE_PUBLIC_KEY_GPU0 & LANGFUSE_SECRET_KEY_GPU0"
        echo "   - LANGFUSE_PUBLIC_KEY_GPU1 & LANGFUSE_SECRET_KEY_GPU1"
        echo "   Then run this script again."
        exit 1
    else
        echo "❌ .env file not found and .env.example doesn't exist."
        echo "📝 Please create .env file with your Langfuse credentials:"
        echo "   LANGFUSE_PUBLIC_KEY_GPU0=your_key_gpu0"
        echo "   LANGFUSE_SECRET_KEY_GPU0=your_secret_gpu0"
        echo "   LANGFUSE_PUBLIC_KEY_GPU1=your_key_gpu1"
        echo "   LANGFUSE_SECRET_KEY_GPU1=your_secret_gpu1"
        exit 1
    fi
fi

# Load environment variables
source .env

# Set default ports if not set
API_PORT_GPU0=${API_PORT_GPU0:-9000}
API_PORT_GPU1=${API_PORT_GPU1:-9001}

# Check if NVIDIA Container Toolkit is available
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA GPU not detected. Please ensure NVIDIA drivers are installed."
    exit 1
fi

# Check GPU count
GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
echo "🔍 Detected $GPU_COUNT GPU(s)"

if [ $GPU_COUNT -lt 2 ]; then
    echo "❌ Less than 2 GPUs detected. This setup requires at least 2 GPUs."
    echo "   Use start-simple.sh for single GPU setup."
    exit 1
fi

echo "🎯 Using GPU 0 and GPU 1"

# Create necessary directories
mkdir -p models logs

# Start services
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose-multi.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 45

# Check service status
echo "📊 Checking service status..."

# Check API GPU0
if curl -s --max-time 5 http://localhost:$API_PORT_GPU0/v1/models > /dev/null; then
    echo "✅ API GPU0 is running at http://localhost:$API_PORT_GPU0"
elif curl -s --max-time 5 http://localhost:$API_PORT_GPU0/health > /dev/null; then
    echo "✅ API GPU0 is running at http://localhost:$API_PORT_GPU0"
else
    echo "❌ API GPU0 is not responding"
fi

# Check API GPU1
if curl -s --max-time 5 http://localhost:$API_PORT_GPU1/v1/models > /dev/null; then
    echo "✅ API GPU1 is running at http://localhost:$API_PORT_GPU1"
elif curl -s --max-time 5 http://localhost:$API_PORT_GPU1/health > /dev/null; then
    echo "✅ API GPU1 is running at http://localhost:$API_PORT_GPU1"
else
    echo "❌ API GPU1 is not responding"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📊 Available endpoints:"
echo "   API GPU0: http://localhost:$API_PORT_GPU0"
echo "   API GPU1: http://localhost:$API_PORT_GPU1"
echo "   Direct vLLM GPU0: http://localhost:8000"
echo "   Direct vLLM GPU1: http://localhost:8001"
echo ""
echo "🔧 Configuration:"
echo "   GPU0 Project: ${PROJECT_NAME_GPU0:-project-gpu0}"
echo "   GPU1 Project: ${PROJECT_NAME_GPU1:-project-gpu1}"
echo "   Langfuse GPU0: ${LANGFUSE_HOST_GPU0:-https://cloud.langfuse.com}"
echo "   Langfuse GPU1: ${LANGFUSE_HOST_GPU1:-https://cloud.langfuse.com}"
echo ""
echo "🧪 Run test: python test_multi.py"
echo "📋 View logs: docker-compose -f docker-compose-multi.yml logs -f"
echo "🛑 Stop services: docker-compose -f docker-compose-multi.yml down" 