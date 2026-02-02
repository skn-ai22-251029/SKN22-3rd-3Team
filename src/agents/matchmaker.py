from pydantic import BaseModel, Field
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.types import Command
from .state import AgentState
from src.core.prompts.prompt_manager import prompt_manager
from src.retrieval.hybrid_search import HybridRetriever
from src.core.models.user_profile import UserProfile

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class BreedSelection(BaseModel):
    """에이전틱 선별용 구조화된 출력."""
    selected_indices: List[int] = Field(..., max_items=3, description="후보 목록에서 선택한 품종 인덱스")
    reasoning: str = Field(..., description="해당 3종을 선택한 이유")

async def matchmaker_node(state: AgentState) -> Command:
    """
    매치메이커: 고양이 품종 추천 전문가.
    에이전틱 선별 방식: 10건 검색 후 LLM이 상위 3건 선별.
    """
    query = state["messages"][-1].content
    
    # UserProfile 초기화 (dict 또는 객체 모두 처리)
    profile_data = state.get("user_profile", {})
    if isinstance(profile_data, dict):
        profile = UserProfile.from_dict(profile_data)
    else:
        profile = profile_data
        
    context = profile.to_context_string()
    persona = prompt_manager.get_prompt("matchmaker", field="persona")

    # 1. 10건 후보 검색 (넓은 범위)
    retriever = HybridRetriever(version="v3", collection_name="care_guides")
    search_query = f"{query} (집사 환경: {context})"
    raw_results = await retriever.search(
        search_query, specialist="Matchmaker",
        filters={"categories": "Breeds"}, limit=10
    )

    if not raw_results:
        return Command(update={"specialist_result": {"source": "matchmaker", "rag_docs": []}}, goto="head_butler")

    # 2. 에이전틱 랭킹: LLM이 10건 중 최적 3건 선별
    selection_prompt = f"""당신은 고양이 전문 매치메이커입니다. 
아래의 [사용자 환경]과 [질문]을 바탕으로, 10개의 [후보 리스트] 중에서 가장 적합한 3마리를 선정하세요.

[사용자 환경]
{context}

[질문]
{query}

[선정 원칙]
1. 알레르기가 있다면 '저자극성(hypoallergenic: 1)' 품종을 최우선으로 하세요. 
2. 주거 환경과 활동량이 매칭되는지 확인하세요.
3. 질문에서 강조한 성격이나 특징을 우선하세요.

[후보 리스트]
"""
    for i, r in enumerate(raw_results):
        selection_prompt += f"{i}. {r.get('name_ko')} ({r.get('name_en')}): {r.get('summary')}\n"
        selection_prompt += f"   - 특징: {', '.join(r.get('personality_traits', []))}\n"
        selection_prompt += f"   - 통계: {r.get('stats', {})}\n\n"

    selector = llm.with_structured_output(BreedSelection)
    selection = await selector.ainvoke(
        [SystemMessage(content=selection_prompt)],
        config={"tags": ["router_classification"]}
    )
    
    # 3. 상위 3건 필터링
    final_indices = selection.selected_indices[:3]
    top_results = [raw_results[i] for i in final_indices if i < len(raw_results)]

    # 선별된 품종 정보를 집사용으로 압축
    rag_context = ""
    if top_results:
        docs_block = "\n\n".join([
            f"[{r.get('name_ko', '')} ({r.get('name_en', '')})]\n{r.get('text', '')[:1500]}"
            for r in top_results
        ])
        distill_msg = await llm.ainvoke([
            SystemMessage(content=(
                "아래 추천 품종 정보에서 사용자에게 설명할 핵심 특징만 간결하게 추출하세요.\n"
                "- 품종별 2~3줄, 성격/생활환경 적합성/주의사항 위주\n"
                "- 총 400자 이내\n\n"
                f"[사용자 질문]\n{query}\n\n"
                f"[추천 품종 정보]\n{docs_block}"
            ))
        ], config={"tags": ["router_classification"]})
        rag_context = distill_msg.content

    # UI DTO 가공
    results = []
    for r in top_results:
        clean_r = {k: (str(v) if k == "_id" else v) for k, v in r.items()}
        if "tags" not in clean_r:
            traits = clean_r.get("personality_traits", [])
            clean_r["tags"] = [f"#{t}" for t in traits[:4]] if traits else []
        results.append(clean_r)

    rag_docs = [
        {
            "title": r.get("name_ko", ""),
            "subtitle": r.get("name_en", ""),
            "source": "TheCatAPI, Wikipedia",
            "url": r.get("source_url") or r.get("source_urls", [""])[0] if r.get("source_urls") else "",
        }
        for r in raw_results
    ]

    specialist_result = {
        "source": "matchmaker",
        "type": "breed_recommendation",
        "specialist_name": "매치메이커 비서",
        "persona": persona + f"\n\n[추천 근거]\n{selection.reasoning}",
        "user_context": context,
        "rag_context": rag_context,
        "rag_docs": rag_docs,
    }

    return Command(
        update={
            "specialist_result": specialist_result,
            "recommendations": results,
            "rag_docs": rag_docs,
        },
        goto="head_butler"
    )
