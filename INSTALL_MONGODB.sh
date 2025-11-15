#!/bin/bash
# Install MongoDB on macOS

echo "📦 Installing MongoDB Community Edition..."
echo "=========================================="
echo ""

# Step 1: Add MongoDB tap
echo "Step 1: Adding MongoDB tap..."
brew tap mongodb/brew

# Step 2: Install MongoDB
echo "Step 2: Installing MongoDB..."
brew install mongodb-community

# Step 3: Start MongoDB
echo "Step 3: Starting MongoDB service..."
brew services start mongodb-community

echo ""
echo "✅ MongoDB installation complete!"
echo ""
echo "Verify it's running:"
echo "  brew services list | grep mongodb"
echo ""
echo "Or connect to it:"
echo "  mongosh"
echo ""
echo "Then restart Coke demo:"
echo "  python demo/coke_demo.py"
echo ""
