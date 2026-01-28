from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .head_butler import head_butler_node
from .adoption_team import adoption_team_node, matchmaker_node, liaison_node
from .care_team import care_team_node, physician_node, peacekeeper_node

def create_zipsa_graph():
    # 1. Memory Checkpointer
    memory = MemorySaver()
    
    # 2. Initialize the graph with AgentState
    workflow = StateGraph(AgentState)
    
    # 3. Add all expert and supervisor nodes
    workflow.add_node("head_butler", head_butler_node)
    
    # Adoption Team
    workflow.add_node("adoption_team", adoption_team_node)
    workflow.add_node("matchmaker", matchmaker_node)
    workflow.add_node("liaison", liaison_node)
    
    # Care Team
    workflow.add_node("care_team", care_team_node)
    workflow.add_node("physician", physician_node)
    workflow.add_node("peacekeeper", peacekeeper_node)
    
    # 4. Define Edge Logic
    def route_butler(state: AgentState):
        decision = state.get("router_decision", "general")
        if decision == "adoption":
            return "adoption_team"
        elif decision == "care":
            return "care_team"
        else:
            return END

    def route_adoption(state: AgentState):
        decision = state.get("adoption_sub_specialist", "general")
        if decision == "matchmaker":
            return "matchmaker"
        elif decision == "liaison": # If we add Liaison back
            return "liaison"
        else:
            return END

    def route_care(state: AgentState):
        decision = state.get("care_sub_specialist", "general")
        if decision == "physician":
            return "physician"
        elif decision == "peacekeeper":
            return "peacekeeper"
        else:
            return END

    # 5. Build Graph
    workflow.add_edge(START, "head_butler")
    
    # Head Butler Routing
    workflow.add_conditional_edges(
        "head_butler",
        route_butler,
        {"adoption_team": "adoption_team", "care_team": "care_team", END: END}
    )
    
    # Adoption Team Routing
    workflow.add_conditional_edges(
        "adoption_team",
        route_adoption,
        {"matchmaker": "matchmaker", "liaison": "liaison", END: END}
    )
    
    # Care Team Routing
    workflow.add_conditional_edges(
        "care_team",
        route_care,
        {"physician": "physician", "peacekeeper": "peacekeeper", END: END}
    )
    
    # Expert Nodes -> END (Aggregation or Final Response)
    workflow.add_edge("matchmaker", END)
    workflow.add_edge("liaison", END)
    workflow.add_edge("physician", END)
    workflow.add_edge("peacekeeper", END)
    
    return workflow.compile(checkpointer=memory)

app = create_zipsa_graph()
