from typing import List
from sentence_transformers import SentenceTransformer
from .base import BaseEmbedder
import asyncio

class LocalEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "dragonkue/multilingual-e5-small-ko"):
        # E5-small-ko dimension is 384
        super().__init__(dimension=384)
        self.model = SentenceTransformer(model_name)
        # Set to CPU or MPS? M2 Pro supports MPS
        try:
            self.model.to("mps")
        except:
             # Fallback to CPU if MPS is not available
            pass

    async def embed_query(self, text: str) -> List[float]:
        # E5 models often need a prefix like 'query: ' for better performance
        processed_text = f"query: {text}"
        # sentence-transformers encode is synchronous, wrapping in thread for async safety
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, lambda: self.model.encode(processed_text))
        return self.validate_and_format(self.normalize(embedding.tolist()))

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        processed_texts = [f"passage: {t}" for t in texts]
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, lambda: self.model.encode(processed_texts))
        
        results = []
        for emb in embeddings:
            results.append(self.validate_and_format(self.normalize(emb.tolist())))
        return results
