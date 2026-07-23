"""LLM provider abstraction. Swap via LLM_PROVIDER in .env: 'openai' talks to
OpenAI's hosted GPT-5; 'local' talks to any OpenAI-compatible local server
(vLLM, Ollama, TGI) at LOCAL_LLM_BASE_URL. The rest of the app only ever
calls `get_llm_client().chat(messages)`.
"""
from functools import lru_cache
from openai import OpenAI

from app.core.config import settings


class LLMClient:
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def chat(self, messages: list[dict], temperature: float = 0.2, max_tokens: int = 800) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""

    def stream_chat(self, messages: list[dict], temperature: float = 0.2):
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


@lru_cache
def get_llm_client() -> LLMClient:
    if settings.LLM_PROVIDER == "local":
        client = OpenAI(base_url=settings.LOCAL_LLM_BASE_URL, api_key="not-needed")
        return LLMClient(client, model="local-model")
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return LLMClient(client, model=settings.OPENAI_CHAT_MODEL)
