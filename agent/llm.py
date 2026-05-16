"""DeepSeek LLM 客户端封装"""
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, List

from openai import OpenAI, APIError, APITimeoutError, APIConnectionError
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    load_settings,
)


class LLMError(Exception):
    """LLM 调用异常"""
    pass


class LLMClient:
    """统一 LLM 调用封装，所有 Agent 模块共用。

    优化要点：
    - 默认 30s 超时（原 60s 太长）
    - 复用 OpenAI client 实例，避免每次重建连接
    - 支持 response_format=json_object（DeepSeek 兼容 OpenAI 协议）
    - 提供 chat_many 用于并发批量调用
    """

    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.base_url = base_url or DEEPSEEK_BASE_URL
        self.model = model or DEEPSEEK_MODEL
        self._client = None
        # 缓存配置（避免每次 chat 都读文件）
        try:
            self._settings = load_settings()
        except Exception:
            self._settings = {}

    @property
    def client(self):
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=float(self._settings.get("request_timeout", 30)),
                max_retries=1,   # 原来 2 次，慢；第一次失败后用户重新点更直观
            )
        return self._client

    def chat(self, system_prompt: str, user_message: str,
             temperature: float = 0.2, max_tokens: int = 1024,
             json_mode: bool = False) -> str:
        """发送 Chat Completion 请求，返回文本响应"""
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                # DeepSeek 兼容 OpenAI 的 json_object 模式，强制 JSON 输出
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            if content is None:
                raise LLMError("API 返回空内容，可能触发了内容过滤")
            return content
        except (APIError, APITimeoutError, APIConnectionError) as e:
            raise LLMError(f"API调用失败：{str(e)}") from e

    def chat_json(self, system_prompt: str, user_message: str,
                  temperature: float = 0.2, max_tokens: int = 1024) -> str:
        """请求并强制 JSON 输出（更快更稳）"""
        # 即使开启了 response_format，仍在 system 里多说一句兜底
        full_system = f"{system_prompt}\n\n请只输出合法 JSON，不要使用 markdown 代码块。"
        return self.chat(
            full_system, user_message,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )

    def chat_many(self, requests: Iterable[dict],
                  worker: Callable[[dict], str] = None,
                  max_workers: int = 4) -> List[str]:
        """并发批量调用。

        requests: 字典列表，每个字典包含 system_prompt / user_message / [其他参数]
        worker:   可选自定义执行函数，签名 (req) -> str；默认调 chat_json
        """
        reqs = list(requests)
        if not reqs:
            return []

        def _default_worker(req):
            return self.chat_json(
                req["system_prompt"],
                req["user_message"],
                temperature=req.get("temperature", 0.2),
                max_tokens=req.get("max_tokens", 1024),
            )

        fn = worker or _default_worker
        results = [None] * len(reqs)
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(fn, req): i for i, req in enumerate(reqs)}
            for f in futures:
                idx = futures[f]
                try:
                    results[idx] = f.result()
                except Exception as e:
                    results[idx] = ""  # 单条失败不连累整批
        return results
