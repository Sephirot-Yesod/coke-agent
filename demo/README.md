# 🥤 Coke Agent Demo

A simple web demo for the Coke learning supervisor agent.

## Quick Start

1. **Create virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r demo/requirements.txt
   ```
   
   This will install:
   - Flask (web framework)
   - OpenAI SDK (LLM client)
   - Volcengine SDK (Doubao models)
   - PyMongo (database, optional for demo)
   - NumPy (data processing)
   - DashScope (embeddings, optional for demo)

3. **Set API key**:
   ```bash
   export ARK_API_KEY="your-volcengine-ark-api-key"
   ```
   
   Get your key from: https://console.volcengine.com/ark

4. **Run the demo**:
   ```bash
   python demo/coke_demo.py
   ```

5. **Open browser**:
   ```
   http://localhost:5001
   ```

## Features

- ✅ Text-only chat interface
- ✅ Simple, clean UI
- ✅ Conversation history
- ✅ No external dependencies (all mocked)

## What's Used

- ✅ **Real DAO modules** (dao.mongo, dao.user_dao, dao.conversation_dao)
- ✅ **In-memory storage** (MongoDB optional, falls back to memory)
- ⚠️  **MongoDB** (optional - will use in-memory if not available)
- ⚠️  **Embeddings** (DashScope - optional for demo)

## Try These

- "hi" → See casual greeting
- "我今天想学英语" → Goal clarification
- "天啊我学不会了" → Emotional support
- "帮我写篇文章" → See refusal

## API Endpoints

- `POST /api/chat` - Send a message to Coke
- `POST /api/clear` - Clear conversation history
- `GET /api/history` - Get conversation history

## Troubleshooting

**Port 5001 already in use?**
- Change the port in `coke_demo.py`: `app.run(port=5002)`

**API key not working?**
- Make sure you exported `ARK_API_KEY` (not `APK_API_KEY`)
- Check: `echo $ARK_API_KEY`

**Import errors?**
- Make sure you're in the project root directory
- Activate your virtual environment
- Install dependencies: `pip install -r requirements.txt`



