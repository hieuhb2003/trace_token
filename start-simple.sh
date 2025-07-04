#!/bin/bash

echo "🚀 Starting Simple vLLM API with Langfuse Cloud Integration..."

# Check if .env file exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "⚠️  .env file not found. Creating from .env.example..."
        cp .env.example .env
        echo "📝 Please edit .env file with your Langfuse credentials:"
        echo "   - LANGFUSE_PUBLIC_KEY"
        echo "   - LANGFUSE_SECRET_KEY"
        echo "   - GPU_ID (0, 1, 2, etc.)"
        echo "   Then run this script again."
        exit 1
    else
        echo "❌ .env file not found and .env.example doesn't exist."
        echo "📝 Please create .env file with your Langfuse credentials:"
        echo "   LANGFUSE_PUBLIC_KEY=your_key"
        echo "   LANGFUSE_SECRET_KEY=your_secret"
        echo "   GPU_ID=0"
        exit 1
    fi
fi

# Load environment variables
source .env

# Set default API_PORT if not set
API_PORT=${API_PORT:-9000}

# Check if NVIDIA Container Toolkit is available
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA GPU not detected. Please ensure NVIDIA drivers are installed."
    exit 1
fi

# Check GPU count
GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
echo "🔍 Detected $GPU_COUNT GPU(s)"

# Validate GPU_ID
if [ "$GPU_ID" -ge "$GPU_COUNT" ]; then
    echo "❌ GPU_ID=$GPU_ID is invalid. Available GPUs: 0 to $((GPU_COUNT-1))"
    exit 1
fi

echo "🎯 Using GPU $GPU_ID"

# Create necessary directories
mkdir -p models logs

# Start services
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose-simple.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."

# Check API
if curl -s --max-time 5 http://localhost:$API_PORT/v1/models > /dev/null; then
    echo "✅ API is running at http://localhost:$API_PORT"
elif curl -s --max-time 5 http://localhost:$API_PORT/health > /dev/null; then
    echo "✅ API is running at http://localhost:$API_PORT"
else
    echo "❌ API is not responding"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📊 Available endpoints:"
echo "   API: http://localhost:$API_PORT"
echo "   Direct vLLM: http://localhost:8000"
echo ""
echo "🔧 Configuration:"
echo "   GPU: $GPU_ID"
echo "   Project: $PROJECT_NAME"
echo "   Langfuse: $LANGFUSE_HOST"
echo ""
echo "🧪 Run test: python test_simple.py"
echo "📋 View logs: docker-compose -f docker-compose-simple.yml logs -f"
echo "🛑 Stop services: docker-compose -f docker-compose-simple.yml down" 