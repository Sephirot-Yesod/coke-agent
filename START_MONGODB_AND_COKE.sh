#!/bin/bash
# Start MongoDB and Coke in one command

echo "🚀 Starting MongoDB and Coke..."
echo ""

# Check if MongoDB is running
if lsof -i :27017 > /dev/null 2>&1; then
    echo "✅ MongoDB is already running on port 27017"
else
    echo "📦 Starting MongoDB..."
    brew services start mongodb-community
    sleep 2
    
    if lsof -i :27017 > /dev/null 2>&1; then
        echo "✅ MongoDB started successfully"
    else
        echo "❌ Failed to start MongoDB"
        echo "   Try manually: brew services start mongodb-community"
        exit 1
    fi
fi

echo ""
echo "🥤 Starting Coke demo..."
echo ""

cd /Users/yesod/Desktop/Code/cokeagent
source venv/bin/activate
export ARK_API_KEY="bfca2bea-242c-4353-989b-300f5095de4e"
python demo/coke_demo.py
