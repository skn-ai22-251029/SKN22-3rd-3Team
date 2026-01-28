from typing import List, Optional, TypedDict, Annotated, Sequence, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Root state for the Cat Head Butler service.
    """
    # Standard conversation history
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Global User Profile (Housing, Activity, Budget, etc.)
    user_profile: Dict[str, Any]
    
    # Adoption Team State
    selected_breed: Optional[str]
    shelter_info: Optional[List[Dict[str, Any]]]
    
    # Care Team State
    is_emergency: bool
    care_category: Optional[str] # 'health', 'behavior', 'general'
    
    # Final response control
    final_output: Optional[str]
    
    # Debug & Transparency Metadata
    debug_info: Optional[Dict[str, Any]]
    
    # Internal Routing State (for Conditional Edges)
    router_decision: Optional[str]
