"""LangGraph workflow definitions for AI Agent YBot."""

from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from src.tools import get_all_tools
from langchain_mistralai import ChatMistralAI
from src.config import config


class AgentState(TypedDict):
    """State definition for the agent graph."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


def create_agent_graph():
    """
    Create the LangGraph agent workflow.
    
    This creates a ReAct-style agent that can:
    1. Process user messages
    2. Decide whether to use tools or respond directly
    3. Execute tools and process results
    4. Provide final responses
    
    Returns:
        Compiled LangGraph workflow.
    """
    # Initialize the Mistral LLM
    llm = ChatMistralAI(
        model=config.MISTRAL_MODEL,
        api_key=config.MISTRAL_API_KEY,
        temperature=0.7,
    )
    
    # Get available tools
    tools = get_all_tools()
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Define the agent node
    def agent_node(state: AgentState) -> dict:
        """Process messages and decide on next action."""
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    
    # Define the conditional edge function
    def should_continue(state: AgentState) -> str:
        """Determine if we should continue to tools or end."""
        last_message = state["messages"][-1]
        
        # If the LLM made a tool call, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        
        # Otherwise, end the conversation
        return END
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        }
    )
    
    # Tools always return to agent
    workflow.add_edge("tools", "agent")
    
    # Compile and return the graph
    return workflow.compile()


def run_agent(user_input: str, graph=None) -> str:
    """
    Run the agent with user input.
    
    Args:
        user_input: The user's message.
        graph: Optional pre-compiled graph (creates new one if not provided).
    
    Returns:
        The agent's response.
    """
    if graph is None:
        graph = create_agent_graph()
    
    # Create initial state with user message
    initial_state = {
        "messages": [HumanMessage(content=user_input)]
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    # Extract the final response
    final_message = result["messages"][-1]
    
    if isinstance(final_message, AIMessage):
        return final_message.content
    
    return str(final_message)
