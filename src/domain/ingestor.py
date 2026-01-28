import os
import json
import logging
from typing import List, Dict, Any, Type
from abc import ABC, abstractmethod
from tqdm import tqdm
from src.core.config import VersionPolicy, ZipsaConfig
from src.utils.mongodb import MongoDBManager
from src.embeddings.factory import EmbeddingFactory
from src.utils.text import tokenize_korean

class IngestionStrategy(ABC):
    def __init__(self, policy: VersionPolicy):
        self.policy = policy
        self.embedder = EmbeddingFactory.get_embedder()

    @abstractmethod
    async def process_breed(self, breed: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def process_guide(self, guide: Dict[str, Any]) -> Dict[str, Any]:
        pass

class LegacyIngestion(IngestionStrategy):
    async def process_breed(self, breed: Dict[str, Any]) -> Dict[str, Any]:
        content = breed.get("summary_ko", "")
        breed["embedding"] = await self.embedder.embed_query(content)
        breed["tokenized_text"] = tokenize_korean(content)
        return breed

    async def process_guide(self, guide: Dict[str, Any]) -> Dict[str, Any]:
        content = f"[{guide.get('category', 'General')}] {guide['title']} {guide.get('text', '')}"
        guide["embedding"] = await self.embedder.embed_query(content[:4000])
        guide["tokenized_text"] = tokenize_korean(content)
        return guide

class ProIngestion(IngestionStrategy):
    async def process_breed(self, breed: Dict[str, Any]) -> Dict[str, Any]:
        personality = ", ".join(breed.get("personality_traits", []))
        physical = ", ".join(breed.get("physical_traits", []))
        content = f"{breed['name_ko']} ({breed.get('name_en', '')}). {breed['summary_ko']}. 성격: {personality}. 특징: {physical}"
        
        breed["embedding"] = await self.embedder.embed_query(content)
        breed["tokenized_text"] = tokenize_korean(content)
        breed["specialists"] = ["Matchmaker (맞춤 추천)"]
        breed["categories"] = ["General Info (상식/정보)"]
        return breed

    async def process_guide(self, guide: Dict[str, Any]) -> Dict[str, Any]:
        cats = ", ".join(guide.get("categories", []))
        specs = ", ".join(guide.get("specialists", []))
        content = f"[{cats}] [{specs}] {guide['title']} {guide.get('text', '')}"
        
        guide["embedding"] = await self.embedder.embed_query(content[:4000])
        guide["tokenized_text"] = tokenize_korean(content)
        return guide

class ZipsaIngestor:
    def __init__(self, version: str):
        self.policy = ZipsaConfig.get_policy(version)
        self.db = MongoDBManager.get_v1_db() if version == "v1" else MongoDBManager.get_v2_db()
        self.strategy = LegacyIngestion(self.policy) if version == "v1" else ProIngestion(self.policy)

    async def ingest_breeds(self):
        if not os.path.exists(self.policy.breed_data_path):
            logging.warning(f"Breed data not found: {self.policy.breed_data_path}")
            return

        with open(self.policy.breed_data_path, "r") as f:
            breeds = json.load(f)
        
        col = self.db[self.policy.breed_collection]
        for b in tqdm(breeds, desc=f"[{self.policy.version}] Breeds"):
            processed = await self.strategy.process_breed(b)
            await col.update_one({"breed_id": processed["breed_id"]}, {"$set": processed}, upsert=True)

    async def ingest_guides(self):
        if not os.path.exists(self.policy.processed_data_path):
            logging.warning(f"Guide data not found: {self.policy.processed_data_path}")
            return

        with open(self.policy.processed_data_path, "r") as f:
            guides = json.load(f)
            
        col = self.db[self.policy.collection_name]
        for g in tqdm(guides, desc=f"[{self.policy.version}] Guides"):
            processed = await self.strategy.process_guide(g)
            await col.update_one({"title": processed["title"]}, {"$set": processed}, upsert=True)
