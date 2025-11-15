# 🔄 Server Restart Required

## Why?

The `<换行>` separator is showing in messages because the server is running with **old prompt files** from before the chunked format changes.

Python caches imported modules, so changes to prompt files require a server restart.

## How to Fix

### Option 1: Use the helper script
```bash
./run_coke.sh
```
This automatically stops old instances and starts fresh.

### Option 2: Manual restart
```bash
# Stop old instance
lsof -ti :5001 | xargs kill -9

# Start server
cd /Users/yesod/Desktop/Code/cokeagent
source venv/bin/activate
export ARK_API_KEY="bfca2bea-242c-4353-989b-300f5095de4e"
python demo/coke_demo.py
```

### Option 3: Use the original script
```bash
./START_MONGODB_AND_COKE.sh
```

## Verification

After restarting, test with a message like "我要学习30分钟"

You should see responses split into separate bubbles:
- Bubble 1: "可以啊"
- Bubble 2: "学30分钟"
- Bubble 3: "现在开始吗"
- Bubble 4: "需要提醒吗"

NOT as one long message with `<换行>` text visible.

## Why This Happens

When you run `python demo/coke_demo.py`:
1. Python imports `coke/prompt/personality_prompt.py`
2. The `COKE_PERSONALITY_PROMPT` variable is loaded into memory
3. Changes to the file don't affect the running server
4. Must restart to reload the new prompts

## Quick Test

Before testing in browser, verify the API works:
```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hi", "user_id": "test"}'
```

Should return:
```json
{
  "responses": ["hey", "咋啦", "找我干嘛"],  // Array of chunks
  "status": "success"
}
```

NOT:
```json
{
  "responses": ["hey<换行>咋啦<换行>找我干嘛"],  // One string with markers
  "status": "success"
}
```

---

**Remember**: Always restart the server after changing prompt files!

