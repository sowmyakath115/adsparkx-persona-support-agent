from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from openai import OpenAI
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.preprocessing import normalize

from support_agent.config import Settings


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class LocalHashingEmbeddingProvider(EmbeddingProvider):
    """Deterministic local vectorizer used for demos without API keys.

    This keeps the project runnable for reviewers. It is not a replacement for production semantic
    embeddings, but it gives a real vector representation and works with Chroma query embeddings.
    """

    def __init__(self, n_features: int = 1536) -> None:
        self.vectorizer = HashingVectorizer(
            n_features=n_features,
            alternate_sign=False,
            norm=None,
            ngram_range=(1, 2),
            stop_words="english",
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        matrix = self.vectorizer.transform(texts)
        matrix = normalize(matrix, norm="l2", axis=1)
        dense = matrix.astype(np.float32).toarray()
        return dense.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )
    return LocalHashingEmbeddingProvider()
