# -*- coding: utf-8 -*-
"""
Coke Check-In Agent
Generates contextual check-in messages when user is inactive
"""
import sys
sys.path.append(".")

import logging
from logging import getLogger
logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)

from framework.agent.llmagent.doubao_llmagent import DouBaoLLMAgent

CHECKIN_SYSTEM_PROMPT = """你是Coke，一个机智、热情、毒舌的学习监督助理。

用户已经有一段时间（超过4小时）没有和你联系了。你需要主动发送一条消息来check-in（问候/关心）。

这条消息应该：
1. 简短、自然（不要超过30字）
2. 像朋友关心一样，不是客服
3. 可以根据之前的聊天内容来提及，比如：
   - 如果之前讨论了学习任务，可以问进度
   - 如果之前用户说要做某事，可以问做得怎么样
   - 如果没有具体内容，就简单问候
4. 保持轻松、幽默的语气
5. 不要说"很久没联系了"这种话，直接切入主题

示例：
- "hey，学习进度如何？"
- "还活着吗？😄"
- "那个雅思模拟题做完了吗？"
- "在干嘛呢？"
"""

class CokeCheckInAgent(DouBaoLLMAgent):
    """Agent that generates contextual check-in messages."""
    
    def __init__(self, context=None, max_retries=3, name=None):
        """
        Initialize Coke Check-In Agent.
        
        Args:
            context: Context with conversation_history, last_task, etc.
        """
        # Build user prompt
        conversation_history = context.get("conversation_history", "")
        last_task = context.get("last_task", "")
        
        userp_template = f"""之前的对话历史：
{conversation_history or "（无）"}

用户最后提到的任务：
{last_task or "（无）"}

请生成一条简短、自然的check-in消息（最多30字）。直接输出消息内容，不要前缀。"""
        
        super().__init__(
            context=context,
            systemp_template=CHECKIN_SYSTEM_PROMPT,
            userp_template=userp_template,
            output_schema=None,  # Free-form text
            default_input={},
            max_retries=max_retries,
            name=name or "CokeCheckInAgent",
            stream=False,
            model="deepseek-v3-1-terminus"
        )
    
    def _posthandle(self):
        """Extract the check-in message."""
        if self.resp:
            if isinstance(self.resp, str):
                self.context["checkin_message"] = self.resp.strip()
            else:
                self.context["checkin_message"] = str(self.resp).strip()
            logger.info(f"Check-in message generated: {self.context['checkin_message']}")

