# -*- coding: utf-8 -*-
"""
Coke Proactive Agent
Handles all proactive messaging: reminders and check-ins.
Shares the same personality and context as CokeResponseAgent.
"""
import sys
sys.path.append(".")

import logging
from logging import getLogger
logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)

from framework.agent.llmagent.doubao_llmagent import DouBaoLLMAgent
from coke.prompt.personality_prompt import COKE_PERSONALITY_PROMPT

class CokeProactiveAgent(DouBaoLLMAgent):
    """
    Agent for proactive messaging (reminders, check-ins).
    Uses the same personality as CokeResponseAgent but with different task context.
    """
    
    def __init__(self, context=None, max_retries=3, name=None):
        """
        Initialize Coke Proactive Agent.
        
        Args:
            context: Context dictionary containing:
                - message_type: "reminder" or "checkin"
                - task_description: (for reminders) what task to remind about
                - conversation_history: recent conversation context
                - last_task: (for check-ins) last mentioned task
        """
        message_type = context.get("message_type", "reminder")
        
        # Build task-specific prompt based on message type
        if message_type == "reminder":
            task_context = self._build_reminder_context(context)
        elif message_type == "checkin":
            task_context = self._build_checkin_context(context)
        else:
            task_context = "发送一条简短的问候消息。"
        
        # System prompt: personality + specific task context
        system_prompt = COKE_PERSONALITY_PROMPT + f"\n\n{task_context}"
        
        # User prompt: conversation history
        conversation_history = context.get("conversation_history", "")
        userp_template = f"""最近的对话历史：
{conversation_history or "（暂无历史对话）"}

🔴 回复格式要求：
- 必须将回复拆分成短语块
- 每个短语块不超过10个字符（包括标点）
- 用 <换行> 分隔每个短语块
- 像发微信一样，一句话分多条发送

示例格式：
"hey<换行>学得咋样<换行>还在忙吗"（每段≤10字）

直接输出消息内容，不要任何前缀或解释。"""
        
        super().__init__(
            context=context,
            systemp_template=system_prompt,
            userp_template=userp_template,
            output_schema=None,  # Free-form text output
            default_input={},
            max_retries=max_retries,
            name=name or "CokeProactiveAgent",
            stream=False,
            model="deepseek-v3-1-terminus"
        )
    
    def _build_reminder_context(self, context):
        """Build task context for reminder messages."""
        task_description = context.get("task_description", "任务")
        
        return f"""## 当前任务：发送提醒消息

用户之前让你在特定时间提醒他/她完成某个任务。现在时间到了，你需要发送一条提醒消息。

任务内容：{task_description}

这条提醒消息应该：
1. 拆分成短语块（每块≤10字符）
2. 用<换行>分隔
3. 像朋友提醒一样，不是闹钟或机器人
4. 根据任务内容个性化
5. 可以适当使用幽默或毒舌

示例：
- 任务"学习雅思" → "喂<换行>雅思咋样了<换行>别刷手机啊"（每段≤10字）
- 任务"休息" → "休息够了吗<换行>该干活了"（每段≤10字）
- 任务"写作业" → "作业呢<换行>还在摸鱼<换行>？"（每段≤10字）
- 任务"锻炼" → "锻炼完了<换行>还是躺着"（每段≤10字）
"""
    
    def _build_checkin_context(self, context):
        """Build task context for check-in messages."""
        last_task = context.get("last_task", "")
        
        return f"""## 当前任务：发送关心消息（check-in）

用户已经有一段时间（超过4小时）没有和你联系了。你需要主动发送一条消息来check-in（问候/关心）。

用户最后提到的任务：{last_task or "（无）"}

这条消息应该：
1. 拆分成短语块（每块≤10字符）
2. 用<换行>分隔
3. 像朋友关心一样，不是客服
4. 可以根据之前的聊天内容来提及：
   - 如果之前讨论了学习任务，可以问进度
   - 如果之前用户说要做某事，可以问做得怎么样
   - 如果没有具体内容，就简单问候
5. 保持轻松、幽默的语气
6. 不要说"很久没联系了"这种话，直接切入主题

示例：
- "hey<换行>学习咋样<换行>？"（每段≤10字）
- "还活着吗<换行>😄"（每段≤10字）
- "雅思模拟题<换行>做完了吗"（每段≤10字）
- "在干嘛呢"（≤10字）
"""
    
    def _posthandle(self):
        """Extract the proactive message."""
        if self.resp:
            if isinstance(self.resp, str):
                message = self.resp.strip()
            else:
                message = str(self.resp).strip()
            
            # Store in context with appropriate key
            message_type = self.context.get("message_type", "reminder")
            if message_type == "reminder":
                self.context["reminder_message"] = message
                logger.info(f"Reminder message generated: {message}")
            elif message_type == "checkin":
                self.context["checkin_message"] = message
                logger.info(f"Check-in message generated: {message}")
            else:
                self.context["proactive_message"] = message
                logger.info(f"Proactive message generated: {message}")

