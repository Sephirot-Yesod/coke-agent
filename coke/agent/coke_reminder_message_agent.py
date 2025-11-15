# -*- coding: utf-8 -*-
"""
Coke Reminder Message Agent
Generates contextual reminder messages based on the task
"""
import sys
sys.path.append(".")

import logging
from logging import getLogger
logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)

from framework.agent.llmagent.doubao_llmagent import DouBaoLLMAgent

REMINDER_MESSAGE_SYSTEM_PROMPT = """你是Coke，一个机智、热情、毒舌的学习监督助理。

用户之前让你在特定时间提醒他/她完成某个任务。现在时间到了，你需要发送一条提醒消息。

这条提醒消息应该：
1. 简短、直接（不超过40字）
2. 像朋友提醒一样，不是闹钟或机器人
3. 根据任务内容个性化
4. 可以适当使用幽默或毒舌
5. 直接询问进度，不要废话

示例：
- 任务"学习雅思" → "喂，雅思学得怎么样了？别告诉我在刷手机"
- 任务"休息" → "休息够了吗？该继续干活了"
- 任务"写作业" → "作业写完了吗？还是在摸鱼？"
- 任务"锻炼" → "锻炼完了？还是躺着呢"
"""

class CokeReminderMessageAgent(DouBaoLLMAgent):
    """Agent that generates contextual reminder messages."""
    
    def __init__(self, context=None, max_retries=3, name=None):
        """
        Initialize Coke Reminder Message Agent.
        
        Args:
            context: Context with task_description
        """
        task_description = context.get("task_description", "你的任务")
        
        userp_template = f"""任务内容：{task_description}

请生成一条简短、个性化的提醒消息（不超过40字）。

要求：
- 像朋友提醒，不是机器人
- 直接询问进度
- 可以适当幽默或毒舌
- 不要说"时间到了"这种废话

直接输出消息内容，不要前缀或解释。"""
        
        super().__init__(
            context=context,
            systemp_template=REMINDER_MESSAGE_SYSTEM_PROMPT,
            userp_template=userp_template,
            output_schema=None,  # Free-form text
            default_input={},
            max_retries=max_retries,
            name=name or "CokeReminderMessageAgent",
            stream=False,
            model="deepseek-v3-1-terminus"
        )
    
    def _posthandle(self):
        """Extract the reminder message."""
        if self.resp:
            if isinstance(self.resp, str):
                self.context["reminder_message"] = self.resp.strip()
            else:
                self.context["reminder_message"] = str(self.resp).strip()
            logger.info(f"Reminder message generated: {self.context['reminder_message']}")

