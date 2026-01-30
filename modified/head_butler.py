from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.types import Command
from .state import AgentState
from src.core.prompt_manager import prompt_manager

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini")

# 라우팅 결정 모델
class RouteDecision(BaseModel):
    decision: Literal["adoption", "care", "general"] = Field(
        description="전문가 팀(adoption, care) 또는 일반 대화(general)로 분류"
    )
    reasoning: str = Field(description="이 분류를 선택한 이유")

async def head_butler_node(state: AgentState) -> Command:
    # 1. YAML에서 라우팅 프롬프트 로드
    router_prompt = prompt_manager.get_prompt("head_butler")
    
    # 구조적 출력(Structured Output)을 위한 LLM 설정
    router = llm.with_structured_output(RouteDecision)
    
    # 2. 라우팅 수행
    # (주의: 시스템 프롬프트 + 사용자 대화 내역 전체를 전달)
    messages = [SystemMessage(content=router_prompt)] + state["messages"]
    result = await router.ainvoke(messages)
    
    # 디버그 정보 기록
    debug_info = state.get("debug_info", {})
    debug_info.update({
        "node": "Head Butler",
        "method": "LLM Router (Few-Shot)",
        "decision": result.decision,
        "reasoning": result.reasoning
    })
    
    # 3. 분기 처리
    if result.decision == "general":
        # =========================================================
        # [수정 핵심] General 답변 생성 시 YAML 프롬프트 적용
        # =========================================================
        
        # (1) YAML에서 'general' 페르소나 로드 ("고양이 전문이라 강아지는 몰라요" 내용 포함)
        general_persona = prompt_manager.get_prompt("general")
        
        # (2) 페르소나 적용하여 답변 생성
        gen_messages = [
            SystemMessage(content=general_persona),
            state["messages"][-1]  # 사용자의 마지막 질문
        ]
        response = await llm.ainvoke(gen_messages)
        
        return Command(
            update={
                "messages": [response],
                "router_decision": "general",
                "debug_info": debug_info
            },
            goto="__end__"
        )
        
    else:
        # 전문가 팀(adoption, care)으로 이동
        target_node = f"{result.decision}_team"
        return Command(
            update={
                "router_decision": result.decision,
                "debug_info": debug_info
            }, 
            goto=target_node
        )