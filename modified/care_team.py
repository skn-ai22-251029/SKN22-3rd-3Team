from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.types import Command
from .state import AgentState
from src.core.prompt_manager import prompt_manager
from src.retrieval.hybrid_search import HybridRetriever

llm = ChatOpenAI(model="gpt-4o-mini")

class CareDecision(BaseModel):
    """케어 팀 내부 상세 분류 모델"""
    category: Literal["physician", "peacekeeper", "general"] = Field(description="분류: 건강/의료/생물학(physician), 행동/심리(peacekeeper), 일반 돌봄(general)")
    reasoning: str = Field(description="이 분류를 선택한 논리적 이유")

async def care_team_node(state: AgentState) -> Command:
    """
    Care Supervisor: Analyzes whether the concern is medical, behavioral, or biological paradox.
    """
    system_prompt = prompt_manager.get_prompt("care_supervisor")
    
    # 시스템 프롬프트 + 사용자 대화 내역을 함께 전달하여 판단력 향상
    router = llm.with_structured_output(CareDecision)
    decision = await router.ainvoke([SystemMessage(content=system_prompt)] + state["messages"])
    
    debug = state.get("debug_info", {})
    debug.update({
        "care_sub_specialist": decision.category,
        "care_reasoning": decision.reasoning
    })
    
    if decision.category == "physician":
        return Command(update={"care_sub_specialist": "physician", "debug_info": debug}, goto="physician")
    elif decision.category == "peacekeeper":
        return Command(update={"care_sub_specialist": "peacekeeper", "debug_info": debug}, goto="peacekeeper")
    else:
        # General care advice (Eating/Sickness questions should NOT come here due to prompts)
        msg = "집사님, 고양이의 전반적인 돌봄에 대해 궁금하신 점이 있으신가요? 구체적인 건강 문제나 행동 고민이 있다면 조금 더 자세히 말씀해 주세요."
        return Command(update={
            "care_sub_specialist": "general",
            "messages": [AIMessage(content=msg)],
            "debug_info": debug
        }, goto="__end__")


async def physician_node(state: AgentState) -> Command:
    """
    Expert node: Physician (건강/의료/생물학/영양)
    LLM acts as a primary logic filter for Paradoxes & Zoonotic diseases before using RAG.
    """
    persona = prompt_manager.get_prompt("physician", field="persona")
    
    retriever = HybridRetriever(version="v3", collection_name="care_guides")
    last_msg = state["messages"][-1].content
    
    # 2. RAG 검색 (Top 3)
    results = await retriever.search(last_msg, specialist="Physician", limit=3)
    
    # Debug Info
    debug = {
        "specialist": "Physician",
        "search_query": last_msg,
        "retrieved_docs": [
            {"title": r.get("title_refined", r.get("title", "No Title")), "score": r.get("final_score", 0)} 
            for r in results
        ]
    }
    
    # 3. 검색 결과를 텍스트 Context로 변환 (모든 문서 포함)
    context_data = ""
    if results:
        for idx, doc in enumerate(results, 1):
            title = doc.get("title_refined", doc.get("title", "제목 없음"))
            content = doc.get("text", doc.get("summary", "내용 없음"))
            context_data += f"[{idx}] 문서 제목: {title}\n    내용: {content[:800]}\n\n"
    else:
        context_data = "검색된 관련 의학 정보가 없습니다."

    # 4. 최종 프롬프트 조합
    final_system_message = f"""
{persona}

---
[RAG 검색 결과 (관련성 점수순)]
{context_data}
"""

    # 5. LLM 답변 생성
    messages = [
        SystemMessage(content=final_system_message),
        HumanMessage(content=last_msg)
    ]
    response = await llm.ainvoke(messages)
        
    return Command(
        update={
            "messages": [response], 
            "debug_info": debug
        }, 
        goto="__end__"
    )


async def peacekeeper_node(state: AgentState) -> Command:
    """
    Expert node: Peacekeeper (행동/갈등 교정)
    """
    persona = prompt_manager.get_prompt("peacekeeper", field="persona")
    
    retriever = HybridRetriever(version="v3", collection_name="care_guides")
    last_msg = state["messages"][-1].content
    results = await retriever.search(last_msg, specialist="Peacekeeper", limit=3)

    debug = {
        "specialist": "Peacekeeper",
        "search_query": last_msg,
        "retrieved_docs": [
            {"title": r.get("title_refined", r.get("title", "No Title")), "score": r.get("final_score", 0)} 
            for r in results
        ]
    }
    
    context_data = ""
    if results:
        for idx, doc in enumerate(results, 1):
            title = doc.get("title_refined", doc.get("title", "제목 없음"))
            content = doc.get("text", doc.get("summary", "내용 없음"))
            context_data += f"[{idx}] 행동 가이드: {title}\n    솔루션: {content[:800]}\n\n"
    else:
        context_data = "관련 행동 교정 가이드를 찾지 못했습니다."

    final_system_message = f"""
{persona}

---
[참고할 행동 심리 데이터]
{context_data}
"""

    messages = [
        SystemMessage(content=final_system_message),
        HumanMessage(content=last_msg)
    ]
    response = await llm.ainvoke(messages)

    return Command(
        update={
            "messages": [response], 
            "debug_info": debug
        }, 
        goto="__end__"
    )