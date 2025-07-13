"""Multi-agent chess assistant system with supervisor"""
import logging
from typing import Dict, Any, List, TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

from rag.retrieve import document_retriever
from rag.prompts import format_chess_system_prompt, format_chess_user_prompt
from tools.chess_tools import get_player_stats, analyze_pgn, get_recent_games

logger = logging.getLogger(__name__)

class MultiAgentState(TypedDict):
    """State for multi-agent chess system"""
    messages: Annotated[list, add_messages]
    current_agent: str
    rag_context: Dict[str, Any]
    chess_data: Dict[str, Any]
    supervisor_decision: str
    iteration_count: int

class ChessMultiAgentSystem:
    """Multi-agent system for comprehensive chess assistance"""
    
    def __init__(self, openai_key: str, langsmith_key: str = None, tavily_key: str = None):
        self.openai_key = openai_key
        self.langsmith_key = langsmith_key
        self.tavily_key = tavily_key
        
        # Initialize models
        self.supervisor_model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=openai_key
        )
        
        self.rag_agent_model = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0.1,
            api_key=openai_key
        )
        
        self.chess_agent_model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=openai_key
        )
        
        # Setup tools
        self.tools = []
        if tavily_key:
            self.tools.append(TavilySearchResults(max_results=3, api_key=tavily_key))
        
        # Add chess-specific tools
        self.tools.extend([get_player_stats, analyze_pgn, get_recent_games])
        
        # Bind tools to chess agent
        self.chess_agent_with_tools = self.chess_agent_model.bind_tools(self.tools)
        self.tool_node = ToolNode(self.tools)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the multi-agent graph"""
        workflow = StateGraph(MultiAgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self._supervisor_agent)
        workflow.add_node("rag_agent", self._rag_agent)
        workflow.add_node("chess_agent", self._chess_agent)
        workflow.add_node("tool_execution", self.tool_node)
        workflow.add_node("final_response", self._final_response_agent)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add edges
        workflow.add_conditional_edges(
            "supervisor",
            self._supervisor_routing,
            {
                "rag_agent": "rag_agent",
                "chess_agent": "chess_agent", 
                "final_response": "final_response",
                "end": END
            }
        )
        
        workflow.add_edge("rag_agent", "final_response")
        
        workflow.add_conditional_edges(
            "chess_agent",
            self._chess_agent_routing,
            {
                "tool_execution": "tool_execution",
                "final_response": "final_response"
            }
        )
        
        workflow.add_edge("tool_execution", "chess_agent")
        workflow.add_edge("final_response", END)
        
        return workflow.compile()
    
    def _supervisor_agent(self, state: MultiAgentState) -> MultiAgentState:
        """Supervisor agent that routes to appropriate specialist"""
        try:
            last_message = state["messages"][-1]
            user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            supervisor_prompt = f"""You are a Chess Assistant Supervisor. Your job is to route user queries to the most appropriate specialist agent.

Available agents:
1. RAG_AGENT - For queries that need chess knowledge from uploaded documents/database
2. CHESS_AGENT - For Chess.com player analysis, game analysis, and live chess data
3. FINAL_RESPONSE - For simple greetings or when no specialist is needed
4. END - For non-chess related queries

User Query: {user_query}

Analysis:
- If asking about chess theory, openings, endgames, or concepts that might be in documents: RAG_AGENT
- If asking about Chess.com players, game analysis, or recent games: CHESS_AGENT  
- If asking about non-chess topics: END
- If simple greeting or general chess question: FINAL_RESPONSE

Respond with only: RAG_AGENT, CHESS_AGENT, FINAL_RESPONSE, or END"""

            response = self.supervisor_model.invoke([
                SystemMessage(content=supervisor_prompt),
                HumanMessage(content=user_query)
            ])
            
            decision = response.content.strip().upper()
            
            # Validate decision
            valid_decisions = ["RAG_AGENT", "CHESS_AGENT", "FINAL_RESPONSE", "END"]
            if decision not in valid_decisions:
                decision = "FINAL_RESPONSE"  # Default fallback
            
            logger.info(f"Supervisor decision: {decision} for query: {user_query[:50]}...")
            
            return {
                **state,
                "supervisor_decision": decision,
                "current_agent": "supervisor",
                "iteration_count": state.get("iteration_count", 0) + 1
            }
            
        except Exception as e:
            logger.error(f"Error in supervisor agent: {e}")
            return {
                **state,
                "supervisor_decision": "FINAL_RESPONSE",
                "current_agent": "supervisor"
            }
    
    def _rag_agent(self, state: MultiAgentState) -> MultiAgentState:
        """RAG agent for chess knowledge retrieval"""
        try:
            last_message = state["messages"][-1]
            user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Get context from RAG system
            context_data = document_retriever.get_context_for_query(
                query=user_query,
                max_chunks=8,
                max_chars=6000
            )
            
            # Format prompts
            system_prompt = format_chess_system_prompt()
            user_prompt = format_chess_user_prompt(
                context=context_data["context"],
                context_count=context_data["context_count"],
                similarity_scores=context_data["similarity_scores"],
                user_query=user_query
            )
            
            # Generate response
            response = self.rag_agent_model.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            logger.info(f"RAG agent processed query with {context_data['context_count']} context chunks")
            
            return {
                **state,
                "messages": state["messages"] + [AIMessage(content=response.content)],
                "rag_context": context_data,
                "current_agent": "rag_agent"
            }
            
        except Exception as e:
            logger.error(f"Error in RAG agent: {e}")
            fallback_response = "I apologize, but I'm having trouble accessing my chess knowledge base right now. Please try again later."
            return {
                **state,
                "messages": state["messages"] + [AIMessage(content=fallback_response)],
                "current_agent": "rag_agent"
            }
    
    def _chess_agent(self, state: MultiAgentState) -> MultiAgentState:
        """Chess.com agent for live data and analysis"""
        try:
            last_message = state["messages"][-1]
            user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            chess_system_prompt = """You are a Chess.com Analysis Agent. You specialize in:
- Analyzing Chess.com player statistics and profiles
- Analyzing chess games in PGN format  
- Retrieving recent games for players
- Providing chess insights based on live data

Use the available tools when you need to:
- Get player statistics from Chess.com
- Analyze chess games
- Retrieve recent games

Always provide helpful, accurate chess analysis. If asked about non-chess topics, politely decline."""
            
            # Process with tools
            messages = [
                SystemMessage(content=chess_system_prompt),
                HumanMessage(content=user_query)
            ]
            
            response = self.chess_agent_with_tools.invoke(messages)
            
            return {
                **state,
                "messages": state["messages"] + [response],
                "current_agent": "chess_agent"
            }
            
        except Exception as e:
            logger.error(f"Error in chess agent: {e}")
            fallback_response = "I apologize, but I'm having trouble accessing Chess.com data right now. Please try again later."
            return {
                **state,
                "messages": state["messages"] + [AIMessage(content=fallback_response)],
                "current_agent": "chess_agent"
            }
    
    def _final_response_agent(self, state: MultiAgentState) -> MultiAgentState:
        """Final response agent for simple queries and coordination"""
        try:
            last_message = state["messages"][-1]
            
            # If we already have a response from a specialist agent, just pass it through
            if isinstance(last_message, AIMessage) and state.get("current_agent") in ["rag_agent", "chess_agent"]:
                return state
            
            # Handle simple queries directly
            user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            final_system_prompt = format_chess_system_prompt()
            
            response = self.rag_agent_model.invoke([
                SystemMessage(content=final_system_prompt),
                HumanMessage(content=user_query)
            ])
            
            return {
                **state,
                "messages": state["messages"] + [AIMessage(content=response.content)],
                "current_agent": "final_response"
            }
            
        except Exception as e:
            logger.error(f"Error in final response agent: {e}")
            fallback_response = "Hello! I'm your Chess Assistant. I can help you with chess-related questions, analyze games, and provide chess insights. What would you like to know about chess?"
            return {
                **state,
                "messages": state["messages"] + [AIMessage(content=fallback_response)],
                "current_agent": "final_response"
            }
    
    def _supervisor_routing(self, state: MultiAgentState) -> str:
        """Route based on supervisor decision"""
        decision = state.get("supervisor_decision", "final_response").lower()
        
        if decision == "rag_agent":
            return "rag_agent"
        elif decision == "chess_agent":
            return "chess_agent"
        elif decision == "end":
            return "end"
        else:
            return "final_response"
    
    def _chess_agent_routing(self, state: MultiAgentState) -> str:
        """Route chess agent to tools or final response"""
        last_message = state["messages"][-1]
        
        # Check if the agent wants to use tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tool_execution"
        else:
            return "final_response"
    
    async def process_message(self, message: str, conversation_state: Dict = None) -> Dict[str, Any]:
        """Process a user message through the multi-agent system"""
        try:
            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "current_agent": "",
                "rag_context": {},
                "chess_data": {},
                "supervisor_decision": "",
                "iteration_count": 0
            }
            
            # Merge with existing conversation state if provided
            if conversation_state:
                initial_state.update(conversation_state)
            
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Extract response
            last_message = final_state["messages"][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            return {
                "response": response_content,
                "state": {
                    "current_agent": final_state.get("current_agent", ""),
                    "supervisor_decision": final_state.get("supervisor_decision", ""),
                    "rag_context": final_state.get("rag_context", {}),
                    "iteration_count": final_state.get("iteration_count", 0)
                },
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "state": conversation_state or {},
                "success": False,
                "error": str(e)
            } 