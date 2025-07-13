import os
from typing import TypedDict, Annotated, Dict, Any
from uuid import uuid4

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from backend.agents.tools import ChessComPlayerTool, ChessComGameAnalyzerTool, ChessComRatingTrackerTool
from backend.utils.logging import get_logger

logger = get_logger(__name__)

class ChessAgentState(TypedDict):
    """State object for the chess analysis agent"""
    messages: Annotated[list, add_messages]

# Initialize tools following notebook style
chess_tool_belt = [
    ChessComPlayerTool(),
    ChessComGameAnalyzerTool(),
    ChessComRatingTrackerTool(),
]

def create_chess_agent_graph(openai_key: str, langsmith_key: str, langsmith_project: str = None):
    """Create and compile the chess analysis LangGraph agent"""
    
    # Set up environment for this request
    os.environ["OPENAI_API_KEY"] = openai_key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = langsmith_key
    os.environ["LANGCHAIN_PROJECT"] = langsmith_project or f"Chess-Agent-{uuid4().hex[0:8]}"
    
    logger.info(f"Creating chess agent with project: {os.environ['LANGCHAIN_PROJECT']}")
    
    # Initialize model and bind tools (following notebook pattern)
    model = ChatOpenAI(model="gpt-4", temperature=0)
    model_with_tools = model.bind_tools(chess_tool_belt)
    
    def call_model(state):
        """Agent node that calls the model with current state"""
        messages = state["messages"]
        logger.debug(f"Calling model with {len(messages)} messages")
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state):
        """Conditional edge function to determine next step"""
        last_message = state["messages"][-1]
        
        # Check if we have tool calls to execute
        if last_message.tool_calls:
            logger.debug("Tool calls detected, routing to action node")
            return "action"
        
        # No tool calls, end the workflow
        logger.debug("No tool calls, ending workflow")
        return END
    
    # Create tool node for executing tools
    tool_node = ToolNode(chess_tool_belt)
    
    # Build the graph following notebook structure
    uncompiled_graph = StateGraph(ChessAgentState)
    
    # Add nodes
    uncompiled_graph.add_node("agent", call_model)
    uncompiled_graph.add_node("action", tool_node)
    
    # Set entry point
    uncompiled_graph.set_entry_point("agent")
    
    # Add conditional edges
    uncompiled_graph.add_conditional_edges(
        "agent",
        should_continue
    )
    
    # Add edge from action back to agent (for potential follow-up)
    uncompiled_graph.add_edge("action", "agent")
    
    # Compile the graph
    chess_agent_graph = uncompiled_graph.compile()
    
    logger.info("Chess agent graph compiled successfully")
    return chess_agent_graph

def analyze_player(username: str, openai_key: str, langsmith_key: str) -> Dict[str, Any]:
    """Analyze a Chess.com player using the LangGraph agent"""
    logger.info(f"Starting player analysis for: {username}")
    
    try:
        # Create the agent graph
        agent_graph = create_chess_agent_graph(openai_key, langsmith_key)
        
        # Create input message
        input_message = HumanMessage(
            content=f"Please analyze the Chess.com player '{username}'. Get their profile, current ratings, and provide insights about their playing style and performance."
        )
        
        # Run the agent
        inputs = {"messages": [input_message]}
        result = agent_graph.invoke(inputs)
        
        # Extract final response
        final_message = result["messages"][-1]
        
        logger.info(f"Player analysis completed for: {username}")
        return {
            "success": True,
            "analysis": final_message.content,
            "message_count": len(result["messages"])
        }
        
    except Exception as e:
        error_msg = f"Error analyzing player {username}: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def analyze_pgn_game(pgn_content: str, openai_key: str, langsmith_key: str) -> Dict[str, Any]:
    """Analyze a PGN game using the LangGraph agent"""
    logger.info("Starting PGN game analysis")
    
    try:
        # Create the agent graph
        agent_graph = create_chess_agent_graph(openai_key, langsmith_key)
        
        # Create input message with PGN content
        input_message = HumanMessage(
            content=f"Please analyze this chess game in PGN format and provide insights about the opening, tactics, and key moments:\n\n{pgn_content}"
        )
        
        # Run the agent
        inputs = {"messages": [input_message]}
        result = agent_graph.invoke(inputs)
        
        # Extract final response
        final_message = result["messages"][-1]
        
        logger.info("PGN game analysis completed")
        return {
            "success": True,
            "analysis": final_message.content,
            "message_count": len(result["messages"])
        }
        
    except Exception as e:
        error_msg = f"Error analyzing PGN game: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def analyze_recent_games(username: str, num_games: int, openai_key: str, langsmith_key: str) -> Dict[str, Any]:
    """Analyze recent games for a Chess.com player"""
    logger.info(f"Starting recent games analysis for {username} ({num_games} games)")
    
    try:
        # Create the agent graph
        agent_graph = create_chess_agent_graph(openai_key, langsmith_key)
        
        # Create input message for recent games analysis
        input_message = HumanMessage(
            content=f"Please analyze the last {num_games} games for Chess.com player '{username}'. Look at their recent performance, opening choices, rating trends, and provide insights about their current playing strength and patterns."
        )
        
        # Run the agent
        inputs = {"messages": [input_message]}
        result = agent_graph.invoke(inputs)
        
        # Extract final response
        final_message = result["messages"][-1]
        
        logger.info(f"Recent games analysis completed for: {username}")
        return {
            "success": True,
            "analysis": final_message.content,
            "message_count": len(result["messages"])
        }
        
    except Exception as e:
        error_msg = f"Error analyzing recent games for {username}: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        } 