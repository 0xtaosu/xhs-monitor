import random
import json
from openai import OpenAI
from config import LLM_CONFIG, MONITOR_CONFIG

class CommentGenerator:
    def __init__(self):
        self.api_key = LLM_CONFIG["API_KEY"]
        # DeepSeek API 不需要 /v1 前缀
        self.api_base = LLM_CONFIG["API_BASE"].rstrip('/')
        self.model = LLM_CONFIG["MODEL"]
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )

    def generate_comment(self, title: str, content: str) -> str:
        """
        根据笔记标题和内容生成评论
        """
        try:
            print(f"正在调用 API: {self.api_base}/chat/completions")
            print(f"使用模型: {self.model}")
            print("请求参数:")
            request_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": LLM_CONFIG["SYSTEM_PROMPT"]
                    },
                    {
                        "role": "user",
                        "content": f"请根据以下笔记生成一条评论:\n标题: {title}\n内容: {content}"
                    }
                ],
                "max_tokens": LLM_CONFIG["MAX_TOKENS"],
                "temperature": LLM_CONFIG["TEMPERATURE"],
                "stream": False
            }
            print(json.dumps(request_params, ensure_ascii=False, indent=2))
            
            response = self.client.chat.completions.create(**request_params)
            print("API 响应内容:")
            print(response)
            
            return response.choices[0].message.content.strip()
                
        except Exception as e:
            print(f"生成评论失败: {e}")
            print(f"错误类型: {type(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            return self._get_fallback_comment()
            
    def _get_fallback_comment(self) -> str:
        """
        获取一条随机备用评论
        """
        return random.choice(MONITOR_CONFIG["FALLBACK_COMMENTS"])