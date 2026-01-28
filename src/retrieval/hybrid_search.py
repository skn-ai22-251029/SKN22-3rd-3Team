from langsmith import traceable
from src.core.config import ZipsaConfig
from src.utils.mongodb import MongoDBManager
from src.embeddings.factory import EmbeddingFactory
from src.utils.text import tokenize_korean

class HybridRetriever:
    def __init__(self, version="v2", collection_name=None):
        self.policy = ZipsaConfig.get_policy(version)
        self.db = MongoDBManager.get_v1_db() if version == "v1" else MongoDBManager.get_v2_db()
        
        # Use collection from policy if not provided
        self.collection_name = collection_name or self.policy.collection_name
        self.collection = self.db[self.collection_name]
        self.embedder = EmbeddingFactory.get_embedder()

    @traceable(name="Hybrid Search")
    async def search(self, query: str, specialist: str = None, limit: int = 3):
        """
        Performs Hybrid Search using RRF (Reciprocal Rank Fusion) with optional Specialist filtering.
        """
        # 1. Vector Search with Pre-filter
        query_vector = await self.embedder.embed_query(query)
        
        vector_search_stage = {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": limit * 2
            }
        }
        
        if specialist:
            vector_search_stage["$vectorSearch"]["filter"] = {
                "specialists": specialist
            }

        vector_results = []
        try:
            vector_results = await self.collection.aggregate([
                vector_search_stage,
                { "$set": { "score_type": "vector" } }
            ]).to_list(None)
        except Exception as e:
            print(f"Vector Search Error: {e}")

        # 2. Keyword Search (Atlas Search)
        keyword_results = []
        try:
            tokenized_query = tokenize_korean(query)
            search_query = {
                "index": "keyword_index",
                "text": {
                    "query": tokenized_query,
                    "path": "tokenized_text" # Standard path in our schema
                }
            }
            
            if specialist:
                search_query = {
                    "index": "keyword_index",
                    "compound": {
                        "must": [{"text": {"query": tokenized_query, "path": "tokenized_text"}}],
                        "filter": [{"text": {"query": specialist, "path": "specialists"}}]
                    }
                }

            keyword_results = await self.collection.aggregate([
                { "$search": search_query },
                { "$limit": limit * 2 },
                { "$set": { "score_type": "keyword" } }
            ]).to_list(None)
        except Exception as e:
            # Failure here is common if the Search Index doesn't exist on M0
            print(f"Keyword Search (BM25) skipped/failed: {e}")

        # 3. RRF Combination (Fallback to Vector if Keyword is empty)
        scores = {}
        for rank, doc in enumerate(vector_results):
            doc_id = str(doc.get("_id"))
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + 60)

        for rank, doc in enumerate(keyword_results):
            doc_id = str(doc.get("_id"))
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + 60)
        
        # Merge and Sort
        merged = []
        seen = set()
        all_docs = vector_results + keyword_results
        
        if not all_docs:
            return []

        all_docs_sorted = sorted(all_docs, key=lambda x: scores.get(str(x.get("_id")), 0), reverse=True)
        
        for doc in all_docs_sorted:
            doc_id = str(doc.get("_id"))
            if doc_id not in seen:
                doc["final_score"] = scores[doc_id]
                merged.append(doc)
                seen.add(doc_id)
        
        return merged[:limit]

# Example Usage
# retriever = HybridRetriever(collection_name="breeds")
# results = await retriever.search("활동적인 고양이 추천해줘")
