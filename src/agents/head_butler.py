from typing import Literal, Dict, Any, Optional
import unicodedata
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.types import Command
from .state import AgentState

llm = ChatOpenAI(model="gpt-4o-mini")

class RouterDecision(BaseModel):
    """전문가 팀 분류 결정 모델"""
    category: Literal["adoption", "care", "general"] = Field(description="요청 분류: 입양 관련(adoption), 건강/행동 케어(care), 일반 인사 및 기타(general)")
    reasoning: str = Field(description="이 분류를 선택한 구체적인 논리적 이유 (한국어)")

async def head_butler_node(state: AgentState) -> Command:
    """
    Root supervisor: Pure LLM Router with Few-Shot Prompting.
    """
    system_prompt = """
    당신은 고양이 상담 서비스의 **Intelligent Router**입니다.
    사용자의 요청을 분석하여, **RAG 데이터베이스의 전문가 메타데이터(specialists)**와 가장 잘 매칭되는 팀으로 연결하십시오.

    [RAG 전문가 매핑 기준]
    1. **adoption** (입양 팀): 아래 전문가들의 전문 분야일 경우 선택
       - **Matchmaker**: 품종 추천, 성향 분석, 입양 상담
       - **Liaison**: 보호소 위치, 유기묘 구조, 입양 절차 및 법률
       
    2. **care** (케어 팀): 아래 전문가들의 전문 분야일 경우 선택
       - **Physician**: 질병 증상(구토/설사), 영양 관리, 사료 추천, 예방 접종
       - **Peacekeeper**: 다묘 가정 합사, 공격성/하악질, 배변 실수 등 행동 교정

    3. **general** (일반): 위 전문가들의 도움이 필요 없는 단순 인사나 일상 대화.

    [Few-Shot Examples]
    - "나한테 맞는 품종 추천해줘" (Matchmaker 소관) -> **adoption**
    - "우리 고양이가 자꾸 동생을 때려" (Peacekeeper 소관) -> **care**
    - "동물등록은 어떻게 해?" (Liaison 소관) -> **adoption**
    - "고양이가 노란 토를 했어" (Physician 소관) -> **care**

    [지침]
    - 사용자의 질문이 어떤 **전문가(specialist)**에게 속하는지 먼저 판단하고, 그 상위 팀으로 라우팅하세요.
    - 직접 답변하지 말고 오직 분류 결정만 내리세요.
    """
    
    router = llm.with_structured_output(RouterDecision)
    decision = await router.ainvoke([SystemMessage(content=system_prompt)] + state["messages"])
    
    debug = {
        "node": "Head Butler",
        "method": "LLM Router (Few-Shot)",
        "decision": decision.category,
        "reasoning": decision.reasoning
    }
    
    if decision.category == "adoption":
        return {
            "router_decision": "adoption",
            "debug_info": debug
        }
    elif decision.category == "care":
        return {
            "router_decision": "care",
            "debug_info": debug
        }
    else:
        # Butler answers general queries
        response = await llm.ainvoke([
            SystemMessage(content="당신은 정중한 수석 집사입니다. 인사나 일반적인 대화에 짧고 우아하게 답하세요. 전문 상담이 필요하면 언제든 말씀해 달라고 덧붙이세요."),
            *state["messages"]
        ])
        return {
            "router_decision": "general",
            "messages": [response],
            "debug_info": debug
        }
