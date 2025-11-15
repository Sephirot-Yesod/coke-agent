# -*- coding: utf-8 -*-
"""
Background Runner for Coke Reminders
Runs in a separate thread to check and send due reminders
"""
import sys
sys.path.append(".")

import time
import threading
import logging
from logging import getLogger
from datetime import datetime

logger = getLogger(__name__)

class BackgroundReminderRunner:
    """Background thread that checks for due reminders."""
    
    def __init__(self, reminder_scheduler, check_interval=30):
        """
        Initialize background runner.
        
        Args:
            reminder_scheduler: ReminderScheduler instance
            check_interval: How often to check for due reminders (seconds)
        """
        self.reminder_scheduler = reminder_scheduler
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.pending_reminders = []  # Store reminders to be retrieved by frontend
        
    def start(self):
        """Start the background runner thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"📅 Reminder background runner started (checking every {self.check_interval}s)")
    
    def stop(self):
        """Stop the background runner."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Reminder background runner stopped")
    
    def _run_loop(self):
        """Main loop that checks for due reminders and inactive users."""
        check_count = 0
        while self.running:
            try:
                check_count += 1
                logger.info(f"🔍 Background check #{check_count} running...")
                
                # Check for due reminders
                due_reminders = self.reminder_scheduler.get_due_reminders()
                
                if due_reminders:
                    logger.info(f"📬 Found {len(due_reminders)} due reminder(s)")
                    
                    for reminder in due_reminders:
                        # Generate message NOW (when timer expires)
                        if not reminder.get('message'):
                            logger.info(f"🤖 Generating proactive message for: {reminder['task_description']}")
                            reminder['message'] = self._generate_proactive_message(
                                reminder['user_id'],
                                reminder['task_description']
                            )
                        
                        # Add to pending list (will be retrieved by API)
                        self.pending_reminders.append(reminder)
                        logger.info(f"   Added to pending list (total pending: {len(self.pending_reminders)})")
                        
                        # Mark as sent
                        self.reminder_scheduler.mark_reminder_sent(reminder["_id"])
                        
                        logger.info(f"⏰ Reminder due for {reminder['user_id']}: {reminder['task_description']}")
                        logger.info(f"   Message: {reminder.get('message', 'N/A')}")
                else:
                    logger.debug(f"No due reminders found in check #{check_count}")
                
                # Check for inactive users (every check cycle)
                self._check_inactive_users()
                
            except Exception as e:
                logger.error(f"Error in reminder loop: {e}")
                import traceback
                traceback.print_exc()
            
            # Wait before next check
            logger.debug(f"Sleeping for {self.check_interval}s until next check...")
            time.sleep(self.check_interval)
    
    def _generate_proactive_message(self, user_id, task_description):
        """Generate a proactive reminder message using AI with recent context."""
        try:
            from coke.agent.coke_proactive_agent import CokeProactiveAgent
            
            # Get recent conversation history for context
            conversation_history = ""
            try:
                recent_messages = self.reminder_scheduler.mongo_db.find_many(
                    "coke_conversations",
                    {"user_id": user_id},
                    limit=100
                )
                
                if recent_messages:
                    # Sort by timestamp and get most recent
                    sorted_msgs = sorted(
                        recent_messages, 
                        key=lambda x: x.get("timestamp", ""), 
                        reverse=True
                    )[:5]
                    sorted_msgs.reverse()  # Oldest first
                    
                    conversation_history = "\n".join([
                        f"用户: {msg['user']}\nCoke: {msg['coke']}"
                        for msg in sorted_msgs
                    ])
                    logger.info(f"   📖 Using recent conversation context ({len(sorted_msgs)} messages)")
            except Exception as e:
                logger.warning(f"Could not fetch conversation history: {e}")
            
            # Generate message with CokeProactiveAgent
            context = {
                "message_type": "reminder",
                "task_description": task_description,
                "conversation_history": conversation_history
            }
            
            agent = CokeProactiveAgent(context)
            
            for result in agent.run():
                if result.get("status") == "finished":
                    message = context.get("reminder_message", "")
                    if message:
                        logger.info(f"   ✅ Generated: {message}")
                        return message
            
            # Fallback if AI generation fails
            fallback = f"⏰ 喂，{task_description}做得怎么样了？"
            logger.warning(f"   ⚠️  Using fallback: {fallback}")
            return fallback
            
        except Exception as e:
            logger.error(f"Failed to generate proactive message: {e}")
            return f"⏰ 做得怎么样了？{task_description}完成了吗？"
    
    def _check_inactive_users(self):
        """Check for users who haven't messaged in 4+ hours."""
        try:
            from datetime import datetime, timedelta
            
            # Get mongo_db from reminder_scheduler
            mongo_db = self.reminder_scheduler.mongo_db
            
            # Find all users
            all_activity = mongo_db.find_many("user_activity", {}, limit=1000)
            
            four_hours_ago = (datetime.now() - timedelta(hours=4)).isoformat()
            
            for activity in all_activity:
                last_time = activity.get("last_message_time", "")
                user_id = activity.get("user_id")
                
                # Check if last message was > 4 hours ago
                if last_time < four_hours_ago:
                    # Check if we already sent a check-in recently
                    last_checkin = activity.get("last_checkin_time", "")
                    one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
                    
                    # Don't spam - only check-in if we haven't in the last hour
                    if last_checkin < one_hour_ago:
                        # Create a check-in reminder
                        checkin_reminder = {
                            "user_id": user_id,
                            "task_description": "check-in",
                            "reminder_time": datetime.now().isoformat(),  # Send now
                            "created_at": datetime.now().isoformat(),
                            "status": "pending",
                            "message": "",  # Will be generated by frontend
                            "is_checkin": True  # Flag to trigger AI generation
                        }
                        
                        self.pending_reminders.append(checkin_reminder)
                        
                        # Update last check-in time
                        mongo_db.update_one(
                            "user_activity",
                            {"user_id": user_id},
                            {"$set": {"last_checkin_time": datetime.now().isoformat()}}
                        )
                        
                        logger.info(f"👋 Check-in triggered for inactive user: {user_id}")
                        
        except Exception as e:
            logger.error(f"Error checking inactive users: {e}")
    
    def get_pending_reminders_for_user(self, user_id):
        """Get pending reminders for a specific user (returns each reminder multiple times until expired)."""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        # Get reminders for this user
        user_reminders = []
        for r in self.pending_reminders:
            if r.get("user_id") == user_id:
                # Set first_retrieved timestamp if not set
                if not r.get('first_retrieved_at'):
                    r['first_retrieved_at'] = now
                    logger.info(f"📬 First retrieval of reminder: {r.get('task_description')}")
                
                user_reminders.append(r)
        
        if user_reminders:
            logger.info(f"📬 Returning {len(user_reminders)} pending reminder(s) for {user_id}")
            for reminder in user_reminders:
                age = (now - reminder.get('first_retrieved_at', now)).total_seconds()
                logger.debug(f"   → {reminder.get('task_description')} (age: {age:.0f}s)")
        
        # Clean up old reminders (60 seconds after FIRST retrieval)
        cleaned = []
        for r in self.pending_reminders:
            first_retrieved_at = r.get('first_retrieved_at')
            if first_retrieved_at:
                age = (now - first_retrieved_at).total_seconds()
                if age > 60:  # Keep for 60 seconds after first retrieval
                    logger.info(f"🗑️  Removing expired reminder: {r.get('task_description')} for {r.get('user_id')} (age: {age:.0f}s)")
                    continue
            cleaned.append(r)
        
        self.pending_reminders = cleaned
        
        return user_reminders

