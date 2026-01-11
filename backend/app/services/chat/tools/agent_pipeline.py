from langgraph.graph import StateGraph, END
from app.services.chat.agent.schema import AgentState
from app.services.chat.agent import nodes
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# Routing Logic
# -----------------------------

def should_route_by_intent(state: AgentState) -> str:
    """Route to the correct sub-graph based on classified intent and last intent."""
    intent = state.current_intent
    
    if intent == "unclear":
        last_intent = state.last_intent
        logger.info(f"[MASTER_ROUTER] Intent is 'unclear'. Routing to last_intent: {last_intent}")
        return last_intent or "general"
        
    if intent == "product_search":
        return "product_search"
    if intent == "product_support":
        return "product_support"
    if intent == "cart_addition":
        return "cart_addition"
    if intent == "policy":
        return "policy"
    
    return "general"


def should_execute_tools(state: AgentState) -> str:
    """Route to tool executor if there are tool calls, otherwise to formatter."""
    
    if (state.tool_results and 
        len(state.tool_results) == 1 and 
        "text" in state.tool_results[0] and
        "name" not in state.tool_results[0]):
        logger.info("[ROUTER:should_execute_tools] Reasoner returned text. Routing to formatter.")
        state.output = state.tool_results[0].get("text", "I'm sorry, I'm not sure what to do next.")
        return "formatter"

    if state.tool_results and any(call.get("name") for call in state.tool_results):
        logger.info("[ROUTER:should_execute_tools] Tool calls found. Routing to tool_executor.")
        return "tool_executor"
        
    logger.info("[ROUTER:should_execute_tools] No tool calls. Routing to formatter.")
    return "formatter"


def should_continue_product_support(state: AgentState) -> str:
    """
    After tool_executor in product_support flow:
    - If we just found a product (focused_product_id was just set), go back to reasoner
    - Otherwise, go to formatter
    """
    if (state.current_intent == "product_support" and 
        state.focused_product_id and
        state.tool_results and
        len(state.tool_results) > 0):
        
        for result in state.tool_results:
            if isinstance(result, dict) and result.get("name") and result.get("mongoId"):
                logger.info("[ROUTER:should_continue_product_support] Product found. Going back to reasoner to answer question.")
                return "product_support_reasoner"
    
    logger.info("[ROUTER:should_continue_product_support] Routing to formatter.")
    return "formatter"


def route_after_tool_execution(state: AgentState) -> str:
    """Route after tool execution based on intent."""
    if state.current_intent == "product_support":
        return should_continue_product_support(state)
    return "formatter"


# -----------------------------
# Build Graph
# -----------------------------
graph = StateGraph(AgentState)

graph.add_node("classify_intent", nodes.classify_intent)
graph.add_node("product_support_reasoner", nodes.product_support_reasoner)
graph.add_node("analyze_query", nodes.analyze_query)
graph.add_node("llm_reasoner", nodes.shopping_reasoner)
graph.add_node("policy_reasoner", nodes.policy_reasoner)
graph.add_node("general_responder", nodes.general_responder)
graph.add_node("tool_executor", nodes.tool_executor)
graph.add_node("formatter", nodes.format_results)
graph.add_node("cart_reasoner", nodes.cart_reasoner)

graph.set_entry_point("classify_intent")

graph.add_conditional_edges(
    "classify_intent",
    should_route_by_intent,
    {
        "product_search": "analyze_query",
        "product_support": "product_support_reasoner",
        "cart_addition": "cart_reasoner",
        "policy": "policy_reasoner",
        "general": "general_responder"
    }
)

graph.add_edge("analyze_query", "llm_reasoner")

graph.add_conditional_edges(
    "product_support_reasoner",
    should_execute_tools,
    {
        "tool_executor": "tool_executor",
        "formatter": "formatter"
    }
)

graph.add_conditional_edges(
    "llm_reasoner",
    should_execute_tools,
    {
        "tool_executor": "tool_executor",
        "formatter": "formatter"
    }
)

graph.add_conditional_edges(
    "cart_reasoner",
    should_execute_tools,
    {
        "tool_executor": "tool_executor",
        "formatter": "formatter"
    }
)

graph.add_conditional_edges(
    "policy_reasoner",
    should_execute_tools,
    {
        "tool_executor": "tool_executor",
        "formatter": "formatter"
    }
)

graph.add_conditional_edges(
    "general_responder",
    should_execute_tools,
    {
        "tool_executor": "tool_executor",
        "formatter": "formatter"
    }
)

graph.add_conditional_edges(
    "tool_executor",
    route_after_tool_execution,
    {
        "product_support_reasoner": "product_support_reasoner",
        "formatter": "formatter"
    }
)

graph.add_edge("formatter", END)

shopping_assistant = graph.compile()