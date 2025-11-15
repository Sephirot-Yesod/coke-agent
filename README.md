# 🥤 Coke Agent - AI Learning Supervisor

A simple, text-only AI agent that helps users achieve their learning and working goals through conversation, reminders, and proactive check-ins.

---

## ✨ Features

- 💬 **Natural Conversations** - Chat like texting with a friend
- 🎯 **Goal Clarification** - Helps break down vague goals into specific tasks
- ⏰ **Smart Reminders** - AI-generated contextual reminders at scheduled times
- 👋 **Proactive Check-Ins** - Automatically reaches out after 4+ hours of inactivity
- 💾 **MongoDB Persistence** - Remembers conversations across sessions
- 🤖 **DeepSeek v3.1** - Powered by advanced reasoning model

---

## 🎭 Character

**Name**: Coke  
**Personality**: 机智、热情、毒舌 (witty, warm, sharp-tongued)  
**Style**: Like 吕子乔 from 爱情公寓 (iPartment)  
**Purpose**: Help you achieve your goals, not be your secretary

---

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone <your-repo-url>
cd cokeagent

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r demo/requirements.txt

# 4. Set API key
export ARK_API_KEY="your-volcengine-ark-api-key"

# 5. (Optional) Start MongoDB for persistent storage
brew services start mongodb-community

# 6. Run Coke
python demo/coke_demo.py

# 7. Open browser
# http://localhost:5001
```

---

## 🏗️ Architecture

### Simple 3-Agent System

1. **CokeChatAgent** - Main orchestrator
2. **CokeResponseAgent** - Generates responses + extracts tasks/reminders
3. **CokeProactiveAgent** - Generates check-in and reminder messages

### Framework

- **BaseAgent** - Core lifecycle management (prehandle → execute → posthandle)
- **BaseSingleRoundLLMAgent** - LLM integration with templated prompts
- **DouBaoLLMAgent** - Volcengine ARK provider

### Storage

- **MongoDB** (optional) - Persistent conversations, reminders, activity tracking
- **In-Memory** (fallback) - Works without MongoDB

---

## 💬 Example Conversations

**Opening**:
```
You: "hi"
Coke: "hey, 你很好奇啊"
```

**Goal Setting**:
```
You: "我今天想学英语"
Coke: "学英语？这个词有点大。说说你具体想学点什么，今天想完成什么目标或任务？"
```

**Setting Reminder**:
```
You: "30分钟后提醒我"
Coke: "好的，30分钟后我会提醒你！⏰ 已设置提醒"
(30 minutes later - automatic)
Coke: "⏰ 喂，做得怎么样了？"
```

**Support**:
```
You: "天啊我学不会"
Coke: "没事，其实你今天已经尽力了。出去走走，别玩手机了，换换脑子。"
```

**Refusal**:
```
You: "帮我写篇文章"
Coke: "hey，我是你的朋友，但不是你的机器人。想写文章的话，可以去找市面上那么多的大模型公司。"
```

---

## 📁 Repository Structure

```
cokeagent/
├── coke/                    # Coke agent system
│   ├── agent/               # 3 agents
│   ├── prompt/              # Personality & task prompts
│   ├── role/                # Character definition
│   └── scheduler/           # Reminder & check-in system
├── framework/               # Shared agent framework
│   └── agent/               # Base classes
├── dao/                     # Database layer
├── conf/                    # Configuration
├── util/                    # Utilities
├── demo/                    # Web demo application
│   ├── coke_demo.py         # Flask server
│   ├── templates/           # HTML UI
│   └── requirements.txt     # Python dependencies
└── LICENSE                  # MIT License
```

---

## 🔧 Configuration

### Model

Edit `coke/agent/coke_response_agent.py` (line 44):
```python
model_to_use = "deepseek-v3-1-terminus"
```

Change to your model endpoint or:
- `"doubao-1-5-pro-32k-250115"` (Doubao)
- `"ep-YOUR-ENDPOINT-ID"` (Custom endpoint)

### MongoDB

Edit `conf/config.json`:
```json
{
  "mongodb": {
    "mongodb_ip": "127.0.0.1",
    "mongodb_port": "27017",
    "mongodb_name": "mymongo"
  }
}
```

### Reminders & Check-Ins

Edit `coke/scheduler/background_runner.py`:
- Line 56: `check_interval=30` (how often to check)
- Line 90: `timedelta(hours=4)` (inactivity threshold)
- Line 100: `timedelta(hours=1)` (check-in cooldown)

---

## 🎨 Customization

### Change Personality

Edit: `coke/prompt/system_prompt.py`

### Modify Conversation Patterns

Edit: `coke/prompt/task_prompt.py`

### Adjust Reminder Messages

Edit: `coke/agent/coke_reminder_message_agent.py`

---

## 🔑 API Requirements

**Required**:
- Volcengine ARK API key (for DeepSeek v3.1)
- Get from: https://console.volcengine.com/ark

**Optional**:
- MongoDB (for persistence)
- Without it, uses in-memory storage

---

## 📚 Documentation

- `README.md` - This file
- `COKE_COMPLETE.txt` - Quick reference
- `TEST_PROACTIVE_MESSAGING.md` - Testing guide
- `demo/README.md` - Demo setup

---

## 🤝 Contributing

This project is based on the [Luoyun Project](https://github.com/PeterZhao119/luoyun_project) framework, simplified for focused productivity assistance.

---

## 📝 License

MIT License - See LICENSE file

---

## 🎓 Learn More

**What is this?**
- A simplified AI agent framework
- Text-only learning supervisor
- Demonstrates agent composition, LLM integration, and proactive messaging

**Based on**:
- Luoyun Project's agent framework
- Simplified from complex multimodal social companion (Qiaoyun) to focused productivity assistant

---

## 🚀 Get Started

```bash
source venv/bin/activate
export ARK_API_KEY="your-key"
python demo/coke_demo.py
```

Open http://localhost:5001 and start chatting with Coke! 🥤
