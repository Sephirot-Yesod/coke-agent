#!/bin/bash
# Helper script to set API key for the demo

echo "🔑 API Key Configuration for Qiaoyun Demo"
echo "========================================"
echo ""

# Check if API key is already set
if [ ! -z "$ARK_API_KEY" ]; then
    echo "✅ ARK_API_KEY is already set!"
    echo "   Current value: ${ARK_API_KEY:0:10}..."
    echo ""
    read -p "Do you want to change it? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping current API key."
        exit 0
    fi
fi

# Prompt for API key
echo "Please enter your Volcengine ARK API key:"
echo "(Get it from: https://console.volcengine.com/ark)"
echo ""
read -p "ARK_API_KEY: " api_key

if [ -z "$api_key" ]; then
    echo "❌ No API key entered. Exiting."
    exit 1
fi

# Export the key
export ARK_API_KEY="$api_key"

echo ""
echo "✅ API key set successfully!"
echo ""
echo "To make this permanent, add to your ~/.zshrc:"
echo "  echo 'export ARK_API_KEY=\"$api_key\"' >> ~/.zshrc"
echo ""
echo "For now, it's set for this terminal session."
echo ""
echo "Next steps:"
echo "  python demo/app.py"
echo "  Open http://localhost:5001"
