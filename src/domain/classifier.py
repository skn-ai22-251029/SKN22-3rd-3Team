import os
import logging
from typing import List, Dict, Any, Type
from abc import ABC, abstractmethod
from openai import AsyncOpenAI
from src.core.config import VersionPolicy, ZipsaConfig
from src.domain.schemas import BatchResultV1, BatchResultV2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ArticleClassifier(ABC):
    """Abstract Base for classification policies."""
    def __init__(self, policy: VersionPolicy, model: str = "gpt-4o-mini"):
        self.policy = policy
        self.model = model
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @abstractmethod
    def _get_system_prompt(self) -> str:
        pass

    @abstractmethod
    def _get_response_format(self) -> Type:
        pass

    async def classify_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items:
            return []

        user_content = "Analyze these articles:\n\n"
        for item in items:
            uid_key = 'uid' if 'uid' in item else 'index'
            user_content += f"ID: {item.get(uid_key)}\nTitle: {item['title']}\nContent: {item.get('text', '')[:2000]}\n\n"

        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_content}
                ],
                response_format=self._get_response_format(),
                temperature=0
            )
            return [res.model_dump() for res in response.choices[0].message.parsed.results]
        except Exception as e:
            logging.error(f"[{self.policy.version}] Classification Error: {e}")
            return []

class LegacyClassifier(ArticleClassifier):
    def _get_system_prompt(self) -> str:
        return f"""
        You are a cat consultant AI. Analyze articles and assign EXACTLY ONE category from: {', '.join(self.policy.categories)}.
        Extract category, keywords (3), summary (1 sentence), and potential_questions (2).
        """
    
    def _get_response_format(self) -> Type:
        return BatchResultV1

class ProClassifier(ArticleClassifier):
    def _get_system_prompt(self) -> str:
        return f"""
        You are an expert cat consultant AI "Zipsa". Extract 2-layer metadata.
        Layer 1 (Topic): Select ALL relevant from: {', '.join(self.policy.categories)}.
        Layer 2 (Specialist): Select relevant from: {', '.join(self.policy.specialists)}.
        Extract summary, keywords (3-5), potential_questions (2-3), target_audience, and entities in Korean.
        """

    def _get_response_format(self) -> Type:
        return BatchResultV2

class ClassifierFactory:
    @staticmethod
    def create(version: str) -> ArticleClassifier:
        policy = ZipsaConfig.get_policy(version)
        if version == "v1":
            return LegacyClassifier(policy)
        elif version == "v2":
            return ProClassifier(policy)
        else:
            raise ValueError(f"No classifier implementation for version: {version}")
