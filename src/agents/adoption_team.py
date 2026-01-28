from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.types import Command
from .state import AgentState

llm = ChatOpenAI(model="gpt-4o-mini")

class AdoptionDecision(BaseModel):
    """입양 팀 내부 상세 분류 모델"""
    category: Literal["matchmaker", "general"] = Field(description="분류: 맞춤 품종 추천(matchmaker), 일반 입양 정보(general)")
    reasoning: str = Field(description="이 분류를 선택한 논리적 이유")

async def adoption_team_node(state: AgentState) -> Command:
    """
    Adoption Supervisor: Decides if the user needs a breed recommendation or general info.
    """
    system_prompt = """
    당신은 ZIPSA 서비스의 'Adoption Supervisor'입니다.
    사용자의 요청을 분석하여, **RAG 데이터베이스의 전문가 메타데이터(specialists)**와 가장 잘 매칭되는 하위 전문가에게 안내하세요.

    [RAG 전문가 매핑 기준]
    - matchmaker: **Matchmaker** (품종 추천) 또는 **Liaison** (보호소/법률) 전문가 정보가 필요한 경우.
    - general: 특정 전문가 정보 없이 일반적인 입양 절차나 준비물에 대한 안내.

    [지침]
    - RAG 검색이 필요하면 무조건 'matchmaker'를 선택하세요.
    - 모호하면 'general'로 분류하되, '추천', '보호소' 키워드가 있으면 전문가에게 넘기세요.
    """
    
    router = llm.with_structured_output(AdoptionDecision)
    decision = await router.ainvoke([SystemMessage(content=system_prompt)] + state["messages"])
    
    debug = state.get("debug_info", {})
    debug.update({
        "adoption_sub_specialist": decision.category,
        "adoption_reasoning": decision.reasoning
    })
    
    if decision.category == "matchmaker":
        return {"adoption_sub_specialist": "matchmaker", "debug_info": debug}
    else:
        msg = "새로운 가족을 맞이하는 것은 큰 축복입니다! 입양 절차나 필수 준비물에 대해 궁금하신 점이 있다면 무엇이든 물어보세요. 혹은 집사님께 딱 맞는 고양이를 추천해 드릴 수도 있습니다."
        return {
            "adoption_sub_specialist": "general",
            "messages": [AIMessage(content=msg)],
            "debug_info": debug
        }

from src.retrieval.hybrid_search import HybridRetriever

async def matchmaker_node(state: AgentState) -> Command:
    """
    Expert node: Matchmaker (맞춤 추천)
    Incorporates user profile into the search for better matching.
    """
    profile = state.get("user_profile", {})
    context = f"거주환경: {profile.get('housing', '')}, 활동량: {profile.get('activity', '')}, 선호성향: {', '.join(profile.get('traits', []))}"
    
    retriever = HybridRetriever(collection_name="breeds")
    last_msg = state["messages"][-1].content
    search_query = f"{last_msg} (집사 환경: {context})"
    
    results = await retriever.search(search_query, specialist="Matchmaker", limit=3)
    
    # Capture Debug Info
    debug = {
        "specialist": "Matchmaker",
        "search_query": search_query,
        "retrieved_docs": [
            {"title": r.get("name_ko", r.get("name", "Unknown")), "score": r.get("score", 0)} 
            for r in results
        ]
    }
    
    if results:
        top_breed = results[0]
        name_ko = top_breed.get("name_ko", top_breed.get("name", "고양이"))
        summary = top_breed.get("summary_ko", "상세 정보가 없습니다.")
        
        recommendation_msg = f"🧩 **[인사담당 비서]** 집사님의 라이프스타일을 분석한 결과, **{name_ko}** 주인님이 가장 잘 어울리실 것 같습니다! \n\n🎩: `{summary}`"
        shelter_msg = f"\n\n🔭 **[대외협력 비서]** 현재 해당 {name_ko} 주인님과 인연을 맺을 수 있는 인근 보호소 정보를 조회 중입니다. 조만간 기쁜 소식을 들려드릴게요!"
        
        return Command(
            update={
                "selected_breed": name_ko,
                "messages": [AIMessage(content=recommendation_msg + shelter_msg)],
                "debug_info": debug
            },
            goto="__end__"
        )
    
    return Command(
        update={
            "messages": [AIMessage(content="🧩 죄송합니다. 집사님의 환경에 딱 맞는 품종을 찾지 못했습니다. 조금 더 구체적인 선호를 말씀해 주시면 다시 찾아보겠습니다.")],
            "debug_info": debug
        },
        goto="__end__"
    )

async def liaison_node(state: AgentState) -> Command:
    """
    (Optional) Dedicated Liaison node if needed for complex search.
    Currently merged into matchmaker for consolidated UI output.
    """
    breed = state.get("selected_breed", "고양이")
    shelter_msg = f"🔭 **[대외협력 비서]** {breed} 주인님을 모실 수 있는 보호소를 확인 중입니다..."
    return Command(update={"messages": [AIMessage(content=shelter_msg)]}, goto="__end__")
