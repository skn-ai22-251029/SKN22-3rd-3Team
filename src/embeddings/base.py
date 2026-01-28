from abc import ABC, abstractmethod
from typing import List
import numpy as np

class BaseEmbedder(ABC):
    def __init__(self, dimension: int):
        self.dimension = dimension

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of document strings."""
        pass

    def validate_and_format(self, vector: List[float]) -> List[float]:
        """
        Ensures the vector is a float list, matches the expected dimension,
        and handles null/empty cases.
        """
        if not vector or len(vector) == 0:
            raise ValueError("Embedding vector is empty or null.")
        
        if len(vector) != self.dimension:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {len(vector)}")
        
        # Explicit float casting for MongoDB compatibility
        return [float(x) for x in vector]

    def normalize(self, vector: List[float]) -> List[float]:
        """L2 Normalization for Cosine Similarity."""
        arr = np.array(vector)
        norm = np.linalg.norm(arr)
        if norm == 0:
            return vector
        return (arr / norm).tolist()
