# 🔧 Setup Guide for Coke Agent

## Issues Found and Fixed

### 1. ✅ Missing Configuration Directory
**Problem**: The `conf/` directory and configuration files were missing.

**Fixed**: Created:
- `/conf/config.json` - Contains MongoDB and model endpoint configuration
- `/conf/config.py` - Python module to load configuration

### 2. ✅ Ark Client Initialization Error
**Problem**: The Ark client was being instantiated at module level without an API key, causing import errors.

**Fixed**: Modified `framework/agent/llmagent/doubao_llmagent.py` to lazy-load the client only when needed.

### 3. ⚠️ Invalid Model Endpoints (REQUIRES USER ACTION)
**Problem**: The model endpoint IDs in `conf/config.json` return 404 errors:
- `ep-20250203034542-28fxb` (deepseek-v3-1-terminus) - Not found
- `ep-20250127020628-9nf9t` (doubao_1.5_pro) - Not found

**Why**: These endpoints are specific to your Volcengine ARK account and need to be created.

**Solution**: You need to:

1. **Go to Volcengine ARK Console**: https://console.volcengine.com/ark

2. **Create Model Endpoints**:
   - Navigate to "Endpoints" or "Models"
   - Create new endpoints for the models you want to use
   - Copy the endpoint IDs (they look like `ep-xxxxxxxxxxxxxx-xxxxx`)

3. **Update `conf/config.json`**:
   ```json
   {
     "doubao_models": {
       "doubao_1.5_pro": "YOUR_DOUBAO_ENDPOINT_ID_HERE",
       "deepseek-v3-1-terminus": "YOUR_DEEPSEEK_ENDPOINT_ID_HERE"
     }
   }
   ```

4. **Alternative**: If you don't have access to these specific models, you can:
   - Use any other model endpoint you have access to
   - Update the model name in `coke/agent/coke_response_agent.py` (line 47)

### 4. ✅ API Key Format
**Current**: The API key in `START_MONGODB_AND_COKE.sh` is `bfca2bea-242c-4353-989b-300f5095de4e`

**Note**: Make sure this is the correct API key from your Volcengine ARK account. It should match what you see in the console.

## Quick Start (After Fixing Endpoints)

```bash
# 1. Update conf/config.json with your valid endpoint IDs
# 2. Set your API key
export ARK_API_KEY="your-api-key-here"

# 3. Start MongoDB
brew services start mongodb-community

# 4. Run the application
cd /Users/yesod/Desktop/Code/cokeagent
source venv/bin/activate
python demo/coke_demo.py

# 5. Open browser
# http://localhost:5001
```

## Testing

To test if your endpoints are configured correctly:

```bash
cd /Users/yesod/Desktop/Code/cokeagent
source venv/bin/activate
export ARK_API_KEY="your-api-key"
python test_agent.py
```

If configured correctly, you should see a response from Coke.

## Current Status

✅ **Working**:
- Configuration files created
- Import errors fixed
- Flask server runs successfully
- MongoDB connection works
- Web interface is accessible

⚠️ **Needs Configuration**:
- Model endpoint IDs in `conf/config.json` need to be updated with valid endpoints from your ARK account

## Files Modified/Created

1. **Created**:
   - `conf/config.json` - Configuration file
   - `conf/config.py` - Configuration loader
   - `SETUP_GUIDE.md` - This file
   - `test_agent.py` - Test script

2. **Modified**:
   - `framework/agent/llmagent/doubao_llmagent.py` - Fixed client initialization
   - `coke/agent/coke_response_agent.py` - Changed default model to doubao_1.5_pro

## Next Steps

1. Log into your Volcengine ARK console
2. Create or find your model endpoints
3. Update `conf/config.json` with the correct endpoint IDs
4. Test with `python test_agent.py`
5. Start using Coke! 🥤

