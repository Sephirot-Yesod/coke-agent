#!/bin/bash
# Helper script to run Coke Agent (kills any existing instance first)

cd "$(dirname "$0")"

echo "🥤 Starting Coke Agent..."
echo ""

# Kill any existing instances
echo "🔍 Checking for existing instances..."
if lsof -i :5001 > /dev/null 2>&1; then
    echo "   Found existing instance, stopping it..."
    lsof -ti :5001 | xargs kill -9 2>/dev/null
    sleep 1
    echo "   ✅ Stopped"
else
    echo "   No existing instance found"
fi

# Check MongoDB
echo ""
echo "🔍 Checking MongoDB..."
if lsof -i :27017 > /dev/null 2>&1; then
    echo "   ✅ MongoDB is running"
else
    echo "   ⚠️  MongoDB not running (will use in-memory mode)"
    echo "   To start MongoDB: brew services start mongodb-community"
fi

# Check API key
echo ""
echo "🔍 Checking API key..."
if [ -z "$ARK_API_KEY" ]; then
    echo "   ⚠️  ARK_API_KEY not set"
    echo "   Setting from START_MONGODB_AND_COKE.sh..."
    export ARK_API_KEY="bfca2bea-242c-4353-989b-300f5095de4e"
    echo "   ✅ API key set"
else
    echo "   ✅ ARK_API_KEY is set"
fi

# Activate virtual environment
echo ""
echo "🔍 Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"

# Start the server
echo ""
echo "🚀 Starting Coke Agent on http://localhost:5001"
echo ""
echo "=" * 60
echo ""

python demo/coke_demo.py

