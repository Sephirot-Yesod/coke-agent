# -*- coding: utf-8 -*-
"""Coke Chat Agent - Main orchestrator for chat interactions."""

import sys
sys.path.append(".")

import logging
from logging import getLogger
logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)

from framework.agent.base_agent import AgentStatus, BaseAgent
from coke.agent.coke_response_agent import CokeResponseAgent

class CokeChatAgent(BaseAgent):
    """Main orchestrator agent for Coke chat interactions."""
    
    def __init__(self, context=None, max_retries=3, name=None):
        """
        Initialize Coke Chat Agent.
        
        Args:
            context: Context dictionary containing user_message, conversation_history, etc.
            max_retries: Maximum retry attempts
            name: Agent name
        """
        super().__init__(context, max_retries, name or "CokeChatAgent")
    
    def _execute(self):
        """Execute the chat flow."""
        # Step 1: Generate response
        logger.info("CokeChatAgent: Generating response...")
        response_agent = CokeResponseAgent(self.context)
        results = response_agent.run()
        
        for result in results:
            if result["status"] == AgentStatus.FINISHED.value:
                # Extract response from context
                self.resp = self.context.get("coke_response", "")
                logger.info(f"CokeChatAgent: Response generated: {self.resp}")
                break
        
        # Yield the final response
        self.status = AgentStatus.MESSAGE
        yield self.resp
        self.status = AgentStatus.RUNNING



