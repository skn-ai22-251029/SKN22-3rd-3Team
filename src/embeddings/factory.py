import os
from .base import BaseEmbedder

class EmbeddingFactory:
    @staticmethod
    def get_embedder(provider: str = None) -> BaseEmbedder:
        """
        Returns an instance of an embedder based on the provider string.
        Defaults to 'local' if not specified or via EMBEDDING_PROVIDER env var.
        """
        if provider is None:
            provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
            
        if provider == "openai":
            from .openai_embedder import OpenAIEmbedder
            return OpenAIEmbedder()
        elif provider == "local":
            from .local import LocalEmbedder
            return LocalEmbedder()
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
