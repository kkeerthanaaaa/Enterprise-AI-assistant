"""Embedding provider abstraction.

Swap providers purely via EMBEDDING_PROVIDER in .env — nothing else in the
codebase needs to change. This is what lets the team drop in a local model
later (e.g. replace bge-small with an on-prem model) without touching the
retrieval or chat pipeline code.
"""
from abc import ABC, abstractmethod
from functools import lru_cache

from app.core.config import settings


class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    @abstractmethod
    def embed_one(self, text: str) -> list[float]:
        ...


class LocalEmbedder(BaseEmbedder):
    """Uses sentence-transformers locally — no external API calls, good for
    on-prem / air-gapped enterprise deployments."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()


class OpenAIEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "text-embedding-3-small"):
        from openai import OpenAI

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = model_name

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self.client.embeddings.create(model=self.model_name, input=texts)
        return [d.embedding for d in resp.data]

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


@lru_cache
def get_embedder() -> BaseEmbedder:
    if settings.EMBEDDING_PROVIDER == "openai":
        return OpenAIEmbedder()
    return LocalEmbedder(settings.EMBEDDING_MODEL)
