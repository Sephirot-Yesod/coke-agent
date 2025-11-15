# -*- coding: utf-8 -*-
"""
Coke Response Agent - Generates responses to user messages.
Shares the same personality and context as CokeProactiveAgent.
"""

import sys
sys.path.append(".")

import logging
from logging import getLogger
logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)

from framework.agent.base_agent import AgentStatus
from framework.agent.llmagent.doubao_llmagent import DouBaoLLMAgent
from coke.prompt.personality_prompt import COKE_PERSONALITY_PROMPT
from coke.prompt.task_prompt import COKE_TASK_PROMPT

class CokeResponseAgent(DouBaoLLMAgent):
    """Agent that generates Coke's text responses."""
    
    def __init__(self, context=None, max_retries=3, name=None):
        """
        Initialize Coke Response Agent.
        
        Args:
            context: Context dictionary containing user_message, conversation_history, etc.
            max_retries: Maximum retry attempts
            name: Agent name
        """
        # Build user prompt from context
        user_message = context.get("user_message", "")
        conversation_history = context.get("conversation_history", "")
        
        userp_template = COKE_TASK_PROMPT.format(
            user_message=user_message,
            conversation_history=conversation_history or "（暂无历史对话）"
        )
        
        default_input = {
            "user_message": "",
            "conversation_history": ""
        }
        
        # Use DeepSeek v3.1 model (better reasoning capabilities)
        model_to_use = "deepseek-v3-1-terminus"
        
        # Define output schema to extract task and reminder info
        output_schema = {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "Coke的回复内容"
                },
                "has_task": {
                    "type": "boolean",
                    "description": "用户是否提到了具体任务"
                },
                "task_description": {
                    "type": "string",
                    "description": "任务描述，如果没有任务则为空"
                },
                "task_duration_minutes": {
                    "type": "integer",
                    "description": "任务预计持续时间（分钟），如果没有提到则为0"
                },
                "needs_reminder": {
                    "type": "boolean",
                    "description": "是否需要在任务时间结束后提醒用户"
                }
            },
            "required": ["response", "has_task", "needs_reminder"]
        }
        
        super().__init__(
            context=context,
            systemp_template=COKE_PERSONALITY_PROMPT,  # Use shared personality
            userp_template=userp_template,
            output_schema=output_schema,  # Now using structured output
            default_input=default_input,
            max_retries=max_retries,
            name=name or "CokeResponseAgent",
            stream=False,
            model=model_to_use
        )
    
    def _posthandle(self):
        """Post-process the response and handle reminder scheduling."""
        # Extract text response from structured output
        if self.resp:
            if isinstance(self.resp, dict):
                self.context["coke_response"] = self.resp.get("response", "")
                self.context["has_task"] = self.resp.get("has_task", False)
                self.context["task_description"] = self.resp.get("task_description", "")
                self.context["task_duration_minutes"] = self.resp.get("task_duration_minutes", 0)
                self.context["needs_reminder"] = self.resp.get("needs_reminder", False)
            else:
                # Fallback for non-dict responses
                self.context["coke_response"] = str(self.resp)
                self.context["has_task"] = False
                self.context["needs_reminder"] = False
            
            logger.info(f"Coke response: {self.context['coke_response']}")
            
            # Log reminder info if applicable
            if self.context.get("needs_reminder"):
                logger.info(f"📅 Reminder scheduled: {self.context['task_description']} in {self.context['task_duration_minutes']} minutes")



