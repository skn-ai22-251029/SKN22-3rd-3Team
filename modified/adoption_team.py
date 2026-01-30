from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.types import Command
from .state import AgentState
from src.core.prompt_manager import prompt_manager
from src.retrieval.hybrid_search import HybridRetriever

llm = ChatOpenAI(model="gpt-4o-mini")

class AdoptionDecision(BaseModel):
    """입양 팀 내부 상세 분류 모델"""
    category: Literal["matchmaker", "general"] = Field(description="분류: 맞춤 품종 추천(matchmaker), 일반 입양 정보(general)")
    reasoning: str = Field(description="이 분류를 선택한 논리적 이유")

async def adoption_team_node(state: AgentState) -> Command:
    system_prompt = prompt_manager.get_prompt("adoption_supervisor")
    profile = state.get("user_profile", {})
    context_str = f"\n[사용자 환경]\n- 주거: {profile.get('housing', '미설정')}\n- 활동량: {profile.get('activity', '미설정')}\n- 선호: {', '.join(profile.get('traits', [])) if profile.get('traits') else '미설정'}"
    
    router = llm.with_structured_output(AdoptionDecision)
    decision = await router.ainvoke([SystemMessage(content=system_prompt + context_str)] + state["messages"])
    
    debug = state.get("debug_info", {})
    debug.update({
        "adoption_sub_specialist": decision.category,
        "adoption_reasoning": decision.reasoning
    })
    
    if decision.category == "matchmaker":
        return Command(update={"adoption_sub_specialist": "matchmaker", "debug_info": debug}, goto="matchmaker")
    else:
        msg = "새로운 가족을 맞이하는 것은 큰 축복입니다! 입양 절차나 필수 준비물에 대해 궁금하신 점이 있다면 무엇이든 물어보세요. 혹은 집사님께 딱 맞는 고양이를 추천해 드릴 수도 있습니다."
        return Command(update={
            "adoption_sub_specialist": "general",
            "messages": [AIMessage(content=msg)],
            "debug_info": debug
        }, goto="__end__")

async def matchmaker_node(state: AgentState) -> Command:
    """
    Expert node: Matchmaker (맞춤 추천 & 현실 입양 상담 & 품종 검증)
    """
    persona = prompt_manager.get_prompt("matchmaker", field="persona")
    
    profile = state.get("user_profile", {})
    context_profile = f"거주환경: {profile.get('housing', '')}, 활동량: {profile.get('activity', '')}, 선호성향: {', '.join(profile.get('traits', []))}"
    
    retriever = HybridRetriever(version="v3", collection_name="care_guides")
    last_msg = state["messages"][-1].content
    search_query = f"{last_msg} (집사 환경: {context_profile})"
    
    # 2. RAG 검색 수행
    results = await retriever.search(search_query, specialist="Matchmaker", limit=3)
    
    # 3. 검색 결과를 텍스트 Context로 변환
    context_data = ""
    if results:
        for idx, doc in enumerate(results, 1):
            title = doc.get("name_ko", doc.get("name", doc.get("title_refined", "제목 없음")))
            content = doc.get("summary_ko", doc.get("text", doc.get("summary", "내용 없음")))
            # ★ LLM이 비교할 수 있도록 품종명을 명확히 강조
            context_data += f"[{idx}] 문서 제목(품종명): {title}\n    내용: {content[:300]}...\n"
    else:
        # 검색 결과가 없을 때
        context_data = "⚠️ 시스템 알림: 데이터베이스에서 관련 품종 정보를 전혀 찾을 수 없습니다."

    # 4. LLM 메시지 구성
    final_system_message = f"""
{persona}

---
[RAG 검색 결과]
{context_data}

[사용자 프로필]
{context_profile}
"""

    messages = [
        SystemMessage(content=final_system_message),
        HumanMessage(content=last_msg)
    ]
    
    response = await llm.ainvoke(messages)
    
    return Command(
        update={
            "messages": [response],
            "debug_info": {
                "specialist": "Matchmaker",
                "search_query": search_query,
                "retrieved_docs_count": len(results)
            }
        },
        goto="__end__"
    )

async def liaison_node(state: AgentState) -> Command:
    return Command(goto="__end__")