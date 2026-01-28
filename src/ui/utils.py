import asyncio
from src.agents.graph import app
from langchain_core.messages import HumanMessage

async def get_zipsa_response(user_input: str, user_profile: dict, history: list, thread_id: str = "default_session"):
    """
    Invokes the LangGraph Head Butler agent with persistent memory and debug info.
    """
    # 1. Prepare ONLY the new message. 
    new_message = HumanMessage(content=user_input)
    
    # 2. Prepare State Update
    inputs = {
        "messages": [new_message],
        "user_profile": user_profile
    }

    try:
        # Use Dynamic thread_id
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke the graph. 
        result = await app.ainvoke(inputs, config=config)
        
        # 3. Extract output and debug info
        content = "죄송합니다. 답변을 생성하지 못했습니다."
        debug_info = result.get("debug_info", {})
        
        if result.get("final_output"):
            content = result["final_output"]
        else:
            messages = result.get("messages", [])
            if messages:
                content = messages[-1].content
        
        return content, debug_info

    except Exception as e:
        return f"오류 발생: {str(e)}", {}
