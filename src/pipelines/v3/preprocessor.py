import os
import re
import json
from typing import List, Dict, Any
from tqdm import tqdm
from src.utils.text import tokenize_korean
from src.core.config import ZipsaConfig
from src.pipelines.base import BasePreprocessor

class V3Preprocessor(BasePreprocessor):
    def __init__(self):
        self.policy = ZipsaConfig.get_policy("v3")
        self.classifier = None # Lazy init to avoid API key requirement at init
        self.output_path = "data/v3/processed.json"
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove weird whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def _process_batch(self, batch: List[Dict[str, Any]], start_index: int) -> List[Dict[str, Any]]:
        if self.classifier is None:
            from src.pipelines.v3.classifier import V3Classifier
            self.classifier = V3Classifier()

        # 1. LLM Classification
        metadata_results = await self.classifier.classify_batch(batch)
        
        processed_batch = []
        for i, (raw_item, meta) in enumerate(zip(batch, metadata_results)):
            uid = f"v3_{start_index + i:05d}"
            
            # Clean raw text
            clean_content = self.clean_text(raw_item.get("text", ""))
            
            # Tokenization (Title + Summary + Clean Content)
            full_text_for_tokens = f"{meta['title_refined']} {meta['metadata']['summary']} {clean_content}"
            tokenized = tokenize_korean(full_text_for_tokens)
            
            doc = {
                "uid": uid,
                "title_refined": meta["title_refined"],
                "text": clean_content,
                "summary": meta["metadata"]["summary"],
                "keywords": meta["metadata"]["keywords"],
                "intent_tags": meta["metadata"]["intent_tags"],
                "categories": meta["categories"],
                "specialists": meta["specialists"],
                "tokenized_text": tokenized,
                "source": "bemypet_catlab",
                "original_url": raw_item.get("url", "")
            }
            processed_batch.append(doc)
        return processed_batch

    async def run(self, limit: int = None) -> str:
        print("🚀 Starting V3 Pure Preprocessing (Raw -> LLM)...")
        
        raw_path = "data/raw/bemypet_catlab.json"
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"Source raw data not found at {raw_path}")

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        if limit:
            raw_items = raw_items[:limit]

        processed_items = []
        batch_size = 5 # LLM cost/rate limit management
        
        print(f"📊 Processing {len(raw_items)} source documents (Batch Size: {batch_size})...")

        for i in tqdm(range(0, len(raw_items), batch_size), desc="V3 Preprocessing"):
            batch = raw_items[i : i + batch_size]
            processed_batch = await self._process_batch(batch, i)
            processed_items.extend(processed_batch)

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(processed_items, f, ensure_ascii=False, indent=2)
            
        print(f"✨ Saved {len(processed_items)} items to {self.output_path}")
        return self.output_path
