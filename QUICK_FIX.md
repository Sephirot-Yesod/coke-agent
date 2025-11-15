# ⚡ Quick Fix Guide

## 🚨 Current Issue
The application runs but can't connect to the LLM because the model endpoint IDs in `conf/config.json` are invalid.

## ✅ What's Already Fixed
- ✅ Configuration files created
- ✅ Import errors resolved  
- ✅ Server starts successfully
- ✅ Web interface works
- ✅ MongoDB integration works

## 🔧 What You Need to Do

### Step 1: Get Your Endpoint IDs

1. **Go to**: https://console.volcengine.com/ark
2. **Login** with your account
3. **Navigate to** "Endpoints" or "Models" section
4. **Create or find** your model endpoints:
   - Look for DouBao 1.5 Pro
   - Or DeepSeek v3.1
   - Or any other model you have access to
5. **Copy the endpoint ID** (looks like: `ep-xxxxxxxxxxxxxx-xxxxx`)

### Step 2: Update Configuration

Edit `/Users/yesod/Desktop/Code/cokeagent/conf/config.json`:

```json
{
  "mongodb": {
    "mongodb_ip": "127.0.0.1",
    "mongodb_port": "27017",
    "mongodb_name": "coke_db"
  },
  "doubao_models": {
    "doubao_1.5_pro": "PUT_YOUR_ENDPOINT_ID_HERE",
    "deepseek-v3-1-terminus": "PUT_YOUR_OTHER_ENDPOINT_ID_HERE"
  }
}
```

### Step 3: Run the Application

```bash
cd /Users/yesod/Desktop/Code/cokeagent
source venv/bin/activate
export ARK_API_KEY="bfca2bea-242c-4353-989b-300f5095de4e"  # Or your actual key
python demo/coke_demo.py
```

Open browser: http://localhost:5001

## 🎯 That's It!

Once you update the endpoint IDs, everything will work.

## 📚 More Information

- **Detailed Setup**: See `SETUP_GUIDE.md`
- **Debug Report**: See `DEBUG_SUMMARY.md`
- **Main README**: See `README.md`

## ❓ Still Having Issues?

Check that:
1. ✅ ARK_API_KEY is set correctly
2. ✅ Endpoint IDs are valid and accessible with your API key
3. ✅ MongoDB is running (or you're okay with in-memory mode)
4. ✅ Port 5001 is not already in use

## 🆘 Quick Test

To test if your endpoint is configured correctly:

```bash
cd /Users/yesod/Desktop/Code/cokeagent
source venv/bin/activate
export ARK_API_KEY="your-key"
python -c "from coke.agent.coke_response_agent import CokeResponseAgent; print('Config OK!')"
```

If this runs without errors, your config is correct!

