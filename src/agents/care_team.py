from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.types import Command
from .state import AgentState

llm = ChatOpenAI(model="gpt-4o-mini")

class CareDecision(BaseModel):
    """케어 팀 내부 상세 분류 모델"""
    category: Literal["physician", "peacekeeper", "general"] = Field(description="분류: 건강/의료(physician), 행동/갈등(peacekeeper), 일반 돌봄(general)")
    reasoning: str = Field(description="이 분류를 선택한 논리적 이유")

async def care_team_node(state: AgentState) -> Command:
    """
    Care Supervisor: Analyzes whether the concern is medical or behavioral.
    """
    system_prompt = """
    당신은 ZIPSA 서비스의 'Care Supervisor'입니다.
    사용자의 요청을 분석하여, **RAG 데이터베이스의 전문가 메타데이터(specialists)**와 가장 잘 매칭되는 하위 전문가에게 안내하세요.

    [RAG 전문가 매핑 기준]
    - physician: **Physician** 전문가 (질병, 영양, 병원, 사료, 접종 등).
    - peacekeeper: **Peacekeeper** 전문가 (행동 교정, 합사, 심리, 트라우마 등).
    - general: 특정 전문가 정보 없이 일반적인 돌봄 Tip이 필요한 경우.
    """
    
    router = llm.with_structured_output(CareDecision)
    decision = await router.ainvoke([SystemMessage(content=system_prompt)] + state["messages"])
    
    debug = state.get("debug_info", {})
    debug.update({
        "care_sub_specialist": decision.category,
        "care_reasoning": decision.reasoning
    })
    
    if decision.category == "physician":
        return {"care_sub_specialist": "physician", "debug_info": debug}
    elif decision.category == "peacekeeper":
        return {"care_sub_specialist": "peacekeeper", "debug_info": debug}
    else:
        msg = "집사님, 고양이의 건강(아픔, 식사)이나 행동(싸움, 불안) 중 어떤 쪽이 더 고민이신가요? 상황을 조금 더 구별해주시면 가장 적합한 전문가를 연결해 드리겠습니다."
        return {
            "care_sub_specialist": "general",
            "messages": [AIMessage(content=msg)],
            "debug_info": debug
        }

from src.retrieval.hybrid_search import HybridRetriever

async def physician_node(state: AgentState) -> Command:
    """
    Expert node: Physician (건강/의료)
    """
    retriever = HybridRetriever(collection_name="care_guides")
    last_msg = state["messages"][-1].content
    results = await retriever.search(last_msg, specialist="Physician", limit=3)
    
    debug = {
        "specialist": "Physician",
        "search_query": last_msg,
        "retrieved_docs": [{"title": r.get("title", "No Title"), "score": r.get("score", 0)} for r in results]
    }
    
    if results:
        guide = results[0]
        msg = f"🩺 **[주치의 소견] {guide.get('title')}**\n\n{guide.get('content', '')[:600]}..."
        return Command(update={"messages": [AIMessage(content=msg)], "debug_info": debug}, goto="__end__")
        
    return Command(update={"messages": [AIMessage(content="👨‍⚕️ 죄송합니다. 해당 건강 증상에 대한 정확한 가이드를 찾지 못했습니다. 증상이 심각하다면 즉시 가까운 동물병원을 방문하시길 권고드립니다.")], "debug_info": debug}, goto="__end__")

async def peacekeeper_node(state: AgentState) -> Command:
    """
    Expert node: Peacekeeper (갈등 조정/행동)
    """
    retriever = HybridRetriever(collection_name="care_guides")
    last_msg = state["messages"][-1].content
    results = await retriever.search(last_msg, specialist="Peacekeeper", limit=3)

    debug = {
        "specialist": "Peacekeeper",
        "search_query": last_msg,
        "retrieved_docs": [{"title": r.get("title", "No Title"), "score": r.get("score", 0)} for r in results]
    }
    
    if results:
        guide = results[0]
        msg = f"⚖️ **[평화유지군 조언] {guide.get('title')}**\n\n{guide.get('content', '')[:600]}..."
        return Command(update={"messages": [AIMessage(content=msg)], "debug_info": debug}, goto="__end__")

    return Command(update={"messages": [AIMessage(content="🕊️ 고양이들의 정서나 관계에 대한 정보를 찾지 못했습니다. 아이들의 평소 행동이나 환경에 대해 더 말씀해 주시겠어요?")], "debug_info": debug}, goto="__end__")
