from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# --- V1 (Legacy) ---
class ArticleMetadataV1(BaseModel):
    uid: str = Field(description="The unique identifier (uid) of the article")
    category: str = Field(description="Single category")
    keywords: List[str] = Field(description="List of keywords")
    summary: str = Field(description="A concise summary")
    potential_questions: List[str] = Field(description="Potential user questions")

class BatchResultV1(BaseModel):
    results: List[ArticleMetadataV1]

# --- V2 (Pro) ---
class ArticleMetadataV2(BaseModel):
    uid: str = Field(description="The unique identifier (uid) of the article")
    categories: List[str] = Field(description="Multiple categories")
    specialists: List[str] = Field(description="Relevant specialist personas")
    keywords: List[str] = Field(description="3-5 핵심 키워드")
    summary: str = Field(description="1-2문장 한국어 요약")
    potential_questions: List[str] = Field(description="2-3 예상 질문")
    target_audience: str = Field(description="대상 독자 (예: 초보 집사)")
    entities: List[str] = Field(description="언급된 품종, 질병 등 주요 개체")

class BatchResultV2(BaseModel):
    results: List[ArticleMetadataV2]
