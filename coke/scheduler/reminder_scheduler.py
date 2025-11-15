# -*- coding: utf-8 -*-
"""
Reminder Scheduler for Coke
Checks for due reminders and sends proactive messages
"""
import sys
sys.path.append(".")

import time
import logging
from datetime import datetime, timedelta
from logging import getLogger

logger = getLogger(__name__)

class ReminderScheduler:
    """Manages scheduled reminders for Coke."""
    
    def __init__(self, mongo_db):
        self.mongo_db = mongo_db
        logger.info("ReminderScheduler initialized")
    
    def create_reminder(self, user_id, task_description, duration_minutes):
        """Create a new reminder (message will be generated when due)."""
        reminder_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        reminder = {
            "user_id": user_id,
            "task_description": task_description,
            "reminder_time": reminder_time.isoformat(),
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "message": ""  # Will be generated when due
        }
        
        reminder_id = self.mongo_db.insert_one("coke_reminders", reminder)
        logger.info(f"📅 Created reminder {reminder_id} for {user_id} at {reminder_time}")
        logger.info(f"   Task: {task_description}")
        logger.info(f"   ⏰ Message will be generated when timer expires")
        
        return reminder_id
    
    def get_due_reminders(self):
        """Get all reminders that are due now."""
        now = datetime.now()
        
        # Query for due reminders
        due_reminders = []
        all_pending = self.mongo_db.find_many(
            "coke_reminders",
            {"status": "pending"},
            limit=100
        )
        
        # Filter by time - parse ISO strings and compare datetime objects
        for reminder in all_pending:
            reminder_time_str = reminder.get("reminder_time", "")
            if reminder_time_str:
                try:
                    from datetime import datetime as dt
                    reminder_time = dt.fromisoformat(reminder_time_str)
                    
                    if reminder_time <= now:
                        due_reminders.append(reminder)
                        logger.info(f"  → Due: {reminder.get('task_description')} (scheduled for {reminder_time_str})")
                    else:
                        time_left = (reminder_time - now).total_seconds() / 60
                        logger.debug(f"  → Not yet: {reminder.get('task_description')} ({time_left:.1f} min left)")
                except Exception as e:
                    logger.error(f"Error parsing reminder time {reminder_time_str}: {e}")
        
        logger.info(f"Found {len(due_reminders)} due reminders (checked {len(all_pending)} pending, current time: {now.isoformat()})")
        return due_reminders
    
    def mark_reminder_sent(self, reminder_id):
        """Mark a reminder as sent."""
        self.mongo_db.update_one(
            "coke_reminders",
            {"_id": reminder_id},
            {"$set": {"status": "sent", "sent_at": datetime.now().isoformat()}}
        )
        logger.info(f"✅ Marked reminder {reminder_id} as sent")
    
    def get_pending_reminders(self, user_id):
        """Get all pending reminders for a user."""
        reminders = self.mongo_db.find_many(
            "coke_reminders",
            {
                "user_id": user_id,
                "status": "pending"
            }
        )
        return reminders

