# -*- coding: utf-8 -*-
"""Coke Agent Web Demo - Simple text-only learning supervisor."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set demo environment  
os.environ.setdefault('env', 'demo')

# Use actual DAO modules instead of mocks
# No need to mock pymongo - we'll use the real MongoDB classes
# They'll work in memory mode for demo

# Import Flask and other dependencies
from flask import Flask, render_template, request, jsonify
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import actual framework and agents
from framework.agent.base_agent import AgentStatus
from coke.agent.coke_chat_agent import CokeChatAgent

# Import actual DAO modules (they'll use in-memory MongoDB)
from dao.mongo import MongoDBBase
from dao.user_dao import UserDAO
from dao.conversation_dao import ConversationDAO

# Import reminder scheduler
from coke.scheduler.reminder_scheduler import ReminderScheduler
from coke.scheduler.background_runner import BackgroundReminderRunner

app = Flask(__name__)

# Global background runner
background_runner = None

# Initialize MongoDB connection
USE_MONGODB = False
mongo_db = None
conversation_collection = None
reminder_scheduler = None

try:
    mongo_db = MongoDBBase()
    # Test connection by trying a simple operation
    mongo_db.db.list_collection_names()
    conversation_collection = mongo_db.get_collection("coke_conversations")
    
    # Initialize reminder scheduler
    reminder_scheduler = ReminderScheduler(mongo_db)
    
    # Start background reminder checker (no need for global, already declared at module level)
    background_runner = BackgroundReminderRunner(reminder_scheduler, check_interval=30)
    background_runner.start()
    
    USE_MONGODB = True
    print("✅ Connected to MongoDB - Using persistent storage")
    print(f"   Database: {mongo_db.db.name}")
    print(f"   Connection: mongodb://127.0.0.1:27017/")
    print("✅ Reminder system enabled")
    print("✅ Background reminder checker started (30s intervals)")
except Exception as e:
    print(f"⚠️  MongoDB not available, using in-memory storage")
    print(f"   Error: {e}")
    print("⚠️  Reminders disabled (requires MongoDB)")
    USE_MONGODB = False
    mongo_db = None
    reminder_scheduler = None

# Fallback: In-memory conversation history
conversation_history = []

def get_conversation_history(user_id="demo_user", limit=5):
    """Get conversation history from MongoDB or memory."""
    if USE_MONGODB and mongo_db:
        try:
            # Get from MongoDB
            docs = mongo_db.find_many(
                "coke_conversations",
                {"user_id": user_id},
                limit=100
            )
            if docs:
                # Sort by timestamp and get recent
                sorted_docs = sorted(docs, key=lambda x: x.get("timestamp", ""), reverse=True)
                recent = sorted_docs[:limit]
                recent.reverse()  # Oldest first
                return recent
        except Exception as e:
            print(f"Error reading from MongoDB: {e}")
    
    # Fallback to in-memory
    if conversation_history:
        return conversation_history[-limit:]
    return []

def save_conversation_message(user_id, user_message, coke_response):
    """Save conversation to MongoDB or memory."""
    message_data = {
        "user_id": user_id,
        "user": user_message,
        "coke": coke_response,
        "timestamp": datetime.now().isoformat()
    }
    
    if USE_MONGODB and mongo_db:
        try:
            # Save to MongoDB
            mongo_db.insert_one("coke_conversations", message_data)
            
            # Update last activity timestamp for this user
            existing = mongo_db.find_one("user_activity", {"user_id": user_id})
            activity_data = {
                "user_id": user_id,
                "last_message_time": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            if existing:
                # Update existing
                activity_data["_id"] = existing["_id"]
                if "last_checkin_time" in existing:
                    activity_data["last_checkin_time"] = existing["last_checkin_time"]
                mongo_db.replace_one("user_activity", {"user_id": user_id}, activity_data)
            else:
                # Insert new
                activity_data["last_checkin_time"] = ""
                mongo_db.insert_one("user_activity", activity_data)
            
            print(f"💾 Saved to MongoDB: {user_message[:30]}...")
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            # Fallback to memory
            conversation_history.append(message_data)
    else:
        # Save to memory
        conversation_history.append(message_data)

@app.route('/')
def index():
    """Main page."""
    return render_template('coke_index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint."""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get conversation history (from MongoDB or memory)
        user_id = data.get('user_id', 'demo_user')
        recent_messages = get_conversation_history(user_id, limit=5)
        
        # Build conversation history string
        history_str = ""
        if recent_messages:
            history_str = "\n".join([
                f"用户: {msg['user']}\nCoke: {msg['coke']}" 
                for msg in recent_messages
            ])
        
        # Create context
        context = {
            "user_message": user_message,
            "conversation_history": history_str,
            "user_id": "demo_user",
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Run agent
        agent = CokeChatAgent(context)
        results = agent.run()
        
        coke_response = ""
        for result in results:
            if result["status"] == AgentStatus.MESSAGE.value or result["status"] == AgentStatus.FINISHED.value:
                # The response is stored in context by the agent's _posthandle
                coke_response = result.get("context", {}).get("coke_response", "")
                if coke_response:
                    break
        
        # Fallback: try to get from context directly
        if not coke_response:
            coke_response = context.get("coke_response", "")
        
        # Final fallback
        if not coke_response:
            coke_response = "抱歉，我暂时不知道说什么..."
            
        logger.info(f"Final coke_response: {coke_response}")
        
        # Split response by <换行> for multiple messages
        response_parts = [part.strip() for part in coke_response.split('<换行>') if part.strip()]
        if not response_parts:
            response_parts = [coke_response]
        
        # Save to MongoDB or memory
        save_conversation_message(user_id, user_message, coke_response)
        
        # Handle reminder scheduling if needed
        reminder_id = None
        if context.get("needs_reminder") and reminder_scheduler:
            task_desc = context.get("task_description", "")
            duration = context.get("task_duration_minutes", 0)
            
            if task_desc and duration > 0:
                try:
                    reminder_id = reminder_scheduler.create_reminder(
                        user_id, task_desc, duration
                    )
                    logger.info(f"✅ Reminder created: {reminder_id}")
                except Exception as e:
                    logger.error(f"Failed to create reminder: {e}")
        
        return jsonify({
            'responses': response_parts,  # Multiple responses
            'status': 'success',
            'reminder_created': reminder_id is not None,
            'reminder_id': reminder_id
        })
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({
            'error': error_msg,
            'status': 'error'
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear():
    """Clear conversation history."""
    global conversation_history
    
    data = request.json or {}
    user_id = data.get('user_id', 'demo_user')
    
    # Clear from MongoDB
    if USE_MONGODB and mongo_db:
        try:
            deleted = mongo_db.delete_many("coke_conversations", {"user_id": user_id})
            print(f"🗑️  Cleared {deleted} messages from MongoDB")
        except Exception as e:
            print(f"Error clearing MongoDB: {e}")
    
    # Clear from memory
    conversation_history = []
    
    return jsonify({'status': 'success', 'cleared': True})

@app.route('/api/history', methods=['GET'])
def history():
    """Get conversation history."""
    user_id = request.args.get('user_id', 'demo_user')
    
    # Get from MongoDB or memory
    messages = get_conversation_history(user_id, limit=50)
    
    return jsonify({
        'history': messages,
        'storage': 'mongodb' if USE_MONGODB else 'memory',
        'count': len(messages),
        'status': 'success'
    })

@app.route('/api/check_reminders', methods=['GET'])
def check_reminders():
    """Check for pending reminders for a user."""
    user_id = request.args.get('user_id', 'demo_user')
    
    if not background_runner:
        return jsonify({
            'reminders': [],
            'status': 'disabled',
            'message': 'Reminder system requires MongoDB'
        })
    
    # Log the current state before retrieval
    total_pending = len(background_runner.pending_reminders)
    logger.info(f"🔔 Frontend polling for {user_id}. Total pending: {total_pending}")
    
    # Get pending reminders from background runner
    pending = background_runner.get_pending_reminders_for_user(user_id)
    
    if pending:
        logger.info(f"📤 Returning {len(pending)} reminder(s) to frontend for {user_id}")
    else:
        logger.debug(f"📭 No pending reminders for {user_id}")
    
    # Process check-in reminders (generate AI message)
    processed_reminders = []
    for reminder in pending:
        if reminder.get("is_checkin"):
            # Generate contextual check-in message
            try:
                from coke.agent.coke_proactive_agent import CokeProactiveAgent
                
                # Get recent conversation for context
                recent = get_conversation_history(user_id, limit=3)
                history_str = "\n".join([
                    f"用户: {msg['user']}\nCoke: {msg['coke']}"
                    for msg in recent
                ]) if recent else ""
                
                # Extract last task if any
                last_task = ""
                for msg in reversed(recent):
                    if "学" in msg.get('user', '') or "做" in msg.get('user', ''):
                        last_task = msg.get('user', '')
                        break
                
                # Generate check-in message using proactive agent
                checkin_context = {
                    "message_type": "checkin",
                    "conversation_history": history_str,
                    "last_task": last_task
                }
                
                checkin_agent = CokeProactiveAgent(checkin_context)
                for result in checkin_agent.run():
                    if result["status"] == "FINISHED":
                        reminder["message"] = checkin_context.get("checkin_message", "hey，在干嘛呢？")
                        break
                
                if not reminder.get("message"):
                    reminder["message"] = "hey，在干嘛呢？"
                    
            except Exception as e:
                logger.error(f"Failed to generate check-in message: {e}")
                reminder["message"] = "hey，还好吗？"
        
        # Serialize ObjectId to string for JSON
        if '_id' in reminder:
            reminder = dict(reminder)  # Make a copy if needed
            reminder['_id'] = str(reminder['_id'])
        
        processed_reminders.append(reminder)
    
    return jsonify({
        'reminders': processed_reminders,
        'count': len(processed_reminders),
        'status': 'success'
    })

@app.route('/api/reminders/list', methods=['GET'])
def list_reminders():
    """List all reminders for a user (pending and sent)."""
    user_id = request.args.get('user_id', 'demo_user')
    
    if not reminder_scheduler or not USE_MONGODB:
        return jsonify({
            'reminders': [],
            'status': 'disabled'
        })
    
    try:
        pending = reminder_scheduler.get_pending_reminders(user_id)
        
        # Serialize ObjectIds for JSON
        serialized = []
        for reminder in pending:
            if '_id' in reminder:
                reminder = dict(reminder)
                reminder['_id'] = str(reminder['_id'])
            serialized.append(reminder)
        
        return jsonify({
            'reminders': serialized,
            'count': len(serialized),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/debug/reminders', methods=['GET'])
def debug_reminders():
    """Debug endpoint to see all reminders and background runner status."""
    if not USE_MONGODB or not mongo_db:
        return jsonify({
            'error': 'MongoDB not available',
            'status': 'disabled'
        })
    
    try:
        # Get all reminders (pending and sent)
        all_reminders = mongo_db.find_many("coke_reminders", {}, limit=100)
        
        # Convert ObjectId to string for JSON serialization
        def serialize_reminder(reminder):
            if reminder and '_id' in reminder:
                reminder['_id'] = str(reminder['_id'])
            return reminder
        
        serialized_reminders = [serialize_reminder(r) for r in all_reminders]
        
        # Get current time
        from datetime import datetime
        now = datetime.now().isoformat()
        
        # Serialize pending reminders too
        pending_reminders = background_runner.pending_reminders if background_runner else []
        serialized_pending = [serialize_reminder(dict(r)) for r in pending_reminders]
        
        # Background runner status
        runner_status = {
            'running': background_runner.running if background_runner else False,
            'check_interval': background_runner.check_interval if background_runner else 0,
            'pending_count': len(pending_reminders),
            'pending_reminders': serialized_pending
        }
        
        return jsonify({
            'current_time': now,
            'total_reminders': len(serialized_reminders),
            'all_reminders': serialized_reminders,
            'background_runner': runner_status,
            'status': 'success'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'status': 'error'
        }), 500

@app.route('/api/debug/trigger_check', methods=['POST'])
def debug_trigger_check():
    """Manually trigger a reminder check (for debugging)."""
    if not background_runner:
        return jsonify({
            'error': 'Background runner not available',
            'status': 'disabled'
        })
    
    try:
        # Manually check for due reminders
        due_reminders = reminder_scheduler.get_due_reminders()
        
        logger.info(f"Manual check triggered: found {len(due_reminders)} due reminders")
        
        for reminder in due_reminders:
            background_runner.pending_reminders.append(reminder)
            reminder_scheduler.mark_reminder_sent(reminder["_id"])
        
        # Serialize ObjectIds for JSON
        def serialize_reminder(reminder):
            if reminder and '_id' in reminder:
                reminder = dict(reminder)
                reminder['_id'] = str(reminder['_id'])
            return reminder
        
        serialized_due = [serialize_reminder(dict(r)) for r in due_reminders]
        
        return jsonify({
            'found_due': len(due_reminders),
            'due_reminders': serialized_due,
            'pending_after': len(background_runner.pending_reminders),
            'status': 'success'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🥤 Coke Agent Demo")
    print("=" * 60)
    print()
    print("Storage Mode:", "📦 MongoDB (Persistent)" if USE_MONGODB else "💾 In-Memory (Session Only)")
    if USE_MONGODB:
        print("  ✅ Conversations will persist across restarts")
        print("  ✅ Each user has separate conversation history")
    else:
        print("  ⚠️  Conversations reset when server restarts")
        print("  💡 Install MongoDB for persistent storage")
    print()
    print("Starting Flask server on http://localhost:5001")
    print()
    print("Make sure ARK_API_KEY is set:")
    print("  export ARK_API_KEY='your-key'")
    print()
    print("Open your browser to: http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)



