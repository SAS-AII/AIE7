"""
Multi-agent system for chess analysis using LangGraph
"""

import os
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from rag.retrieve import get_document_retriever
from rag.prompts import CHESS_SUPERVISOR_PROMPT, CHESS_RAG_PROMPT, CHESS_PLAYER_ANALYSIS_PROMPT
from tools.chess_tools import get_player_stats, analyze_pgn, get_recent_games

class ChessAgentState(TypedDict):
    """State for the chess multi-agent system"""
    messages: List[Any]
    current_agent: str
    rag_sources: int
    conversation_state: Dict[str, Any]
    api_keys: Dict[str, str]

class ChessMultiAgentSystem:
    """Multi-agent system for chess analysis with supervisor routing"""
    
    def __init__(self):
        self.graph = None
        self.compiled_graph = None
        
    async def _create_supervisor_agent(self, state: ChessAgentState) -> Dict[str, Any]:
        """Supervisor agent that routes queries to appropriate specialist"""
        try:
            api_keys = state.get("api_keys", {})
            openai_key = api_keys.get("openai_key")
            
            if not openai_key:
                return {
                    "messages": [AIMessage(content="Error: OpenAI API key is required")],
                    "current_agent": "supervisor"
                }
            
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=openai_key
            )
            
            # Get the last user message
            last_message = state["messages"][-1]
            user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Use supervisor prompt to determine routing
            supervisor_response = await llm.ainvoke([
                SystemMessage(content=CHESS_SUPERVISOR_PROMPT),
                HumanMessage(content=user_query)
            ])
            
            # Parse supervisor decision
            decision = supervisor_response.content.strip().lower()
            
            if "rag_agent" in decision:
                next_agent = "rag_agent"
            elif "chess_agent" in decision:
                next_agent = "chess_agent"
            else:
                # Default to RAG for general chess questions
                next_agent = "rag_agent"
            
            return {
                "messages": state["messages"],
                "current_agent": next_agent,
                "rag_sources": state.get("rag_sources", 0),
                "conversation_state": state.get("conversation_state", {}),
                "api_keys": api_keys
            }
            
        except Exception as e:
            return {
                "messages": [AIMessage(content=f"Error in supervisor: {str(e)}")],
                "current_agent": "supervisor"
            }
    
    async def _create_rag_agent(self, state: ChessAgentState) -> Dict[str, Any]:
        """RAG agent for chess knowledge retrieval"""
        try:
            api_keys = state.get("api_keys", {})
            openai_key = api_keys.get("openai_key")
            qdrant_url = api_keys.get("qdrant_url", "http://localhost:6333")
            qdrant_api_key = api_keys.get("qdrant_api_key")
            
            if not openai_key:
                return {
                    "messages": state["messages"] + [AIMessage(content="Error: OpenAI API key is required")],
                    "current_agent": "rag_agent",
                    "rag_sources": 0
                }
            
            # Get the last user message
            last_message = state["messages"][-1]
            user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Get document retriever
            retriever = get_document_retriever(api_key=openai_key)
            
            # Retrieve relevant documents
            documents = await retriever.retrieve_documents(
                query=user_query,
                api_key=openai_key,
                qdrant_url=qdrant_url,
                qdrant_api_key=qdrant_api_key,
                k=5
            )
            
            if not documents:
                response = "I don't have enough information in my knowledge base to answer this chess question. Please try asking about chess openings, tactics, endgames, or strategy."
                rag_sources = 0
            else:
                # Generate contextual answer
                response = await retriever.get_contextual_answer(
                    query=user_query,
                    documents=documents,
                    api_key=openai_key
                )
                rag_sources = len(documents)
            
            return {
                "messages": state["messages"] + [AIMessage(content=response)],
                "current_agent": "rag_agent",
                "rag_sources": rag_sources,
                "conversation_state": state.get("conversation_state", {}),
                "api_keys": api_keys
            }
            
        except Exception as e:
            return {
                "messages": state["messages"] + [AIMessage(content=f"Error in RAG agent: {str(e)}")],
                "current_agent": "rag_agent",
                "rag_sources": 0
            }
    
    async def _create_chess_agent(self, state: ChessAgentState) -> Dict[str, Any]:
        """Chess.com agent with tool access"""
        try:
            api_keys = state.get("api_keys", {})
            openai_key = api_keys.get("openai_key")
            
            if not openai_key:
                return {
                    "messages": state["messages"] + [AIMessage(content="Error: OpenAI API key is required")],
                    "current_agent": "chess_agent"
                }
            
            # Tools for chess.com analysis
            tools = [get_player_stats, analyze_pgn, get_recent_games]
            
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=openai_key
            )
            
            # Bind tools to the model
            llm_with_tools = llm.bind_tools(tools)
            
            # Get the last user message
            last_message = state["messages"][-1]
            user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Create system message for chess agent
            system_message = SystemMessage(content=CHESS_PLAYER_ANALYSIS_PROMPT)
            
            # Invoke the model with tools
            response = await llm_with_tools.ainvoke([
                system_message,
                HumanMessage(content=user_query)
            ])
            
            # Check if tools were called
            if response.tool_calls:
                # Execute tools
                tool_node = ToolNode(tools)
                tool_results = tool_node.invoke({"messages": [response]})
                
                # Get final response with tool results
                final_response = await llm.ainvoke([
                    system_message,
                    HumanMessage(content=user_query),
                    response,
                    *tool_results["messages"]
                ])
                
                return {
                    "messages": state["messages"] + [AIMessage(content=final_response.content)],
                    "current_agent": "chess_agent",
                    "rag_sources": state.get("rag_sources", 0),
                    "conversation_state": state.get("conversation_state", {}),
                    "api_keys": api_keys
                }
            else:
                return {
                    "messages": state["messages"] + [AIMessage(content=response.content)],
                    "current_agent": "chess_agent",
                    "rag_sources": state.get("rag_sources", 0),
                    "conversation_state": state.get("conversation_state", {}),
                    "api_keys": api_keys
                }
                
        except Exception as e:
            return {
                "messages": state["messages"] + [AIMessage(content=f"Error in Chess agent: {str(e)}")],
                "current_agent": "chess_agent",
                "rag_sources": 0
            }
    
    def _should_continue(self, state: ChessAgentState) -> str:
        """Determine if we should continue or end"""
        current_agent = state.get("current_agent", "supervisor")
        
        # If we're coming from supervisor, route to the determined agent
        if current_agent in ["rag_agent", "chess_agent"]:
            return current_agent
        else:
            # Default to rag_agent if no specific agent determined
            return "rag_agent"
    
    def create_graph(self) -> StateGraph:
        """Create the multi-agent graph"""
        # Create the graph
        graph = StateGraph(ChessAgentState)
        
        # Add nodes
        graph.add_node("supervisor", self._create_supervisor_agent)
        graph.add_node("rag_agent", self._create_rag_agent)
        graph.add_node("chess_agent", self._create_chess_agent)
        
        # Set entry point
        graph.set_entry_point("supervisor")
        
        # Add conditional edges from supervisor
        graph.add_conditional_edges(
            "supervisor",
            self._should_continue,
            {
                "rag_agent": "rag_agent",
                "chess_agent": "chess_agent"
            }
        )
        
        # Add edges from agents to END
        graph.add_edge("rag_agent", END)
        graph.add_edge("chess_agent", END)
        
        self.graph = graph
        return graph
    
    def compile_graph(self) -> Any:
        """Compile the graph for execution"""
        if not self.graph:
            self.create_graph()
        
        self.compiled_graph = self.graph.compile()
        return self.compiled_graph
    
    async def process_query(
        self,
        query: str,
        conversation_state: Dict[str, Any],
        api_keys: Dict[str, str]
    ) -> Dict[str, Any]:
        """Process a query through the multi-agent system"""
        try:
            if not self.compiled_graph:
                self.compile_graph()
            
            # Create initial state
            initial_state = ChessAgentState(
                messages=[HumanMessage(content=query)],
                current_agent="supervisor",
                rag_sources=0,
                conversation_state=conversation_state,
                api_keys=api_keys
            )
            
            # Run the graph
            result = await self.compiled_graph.ainvoke(initial_state)
            
            # Extract the final message
            final_message = result["messages"][-1]
            response_content = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            return {
                "response": response_content,
                "agent_used": result.get("current_agent", "unknown"),
                "rag_sources": result.get("rag_sources", 0),
                "conversation_state": result.get("conversation_state", {})
            }
            
        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "agent_used": "error",
                "rag_sources": 0,
                "conversation_state": conversation_state
            }

# Global instance
chess_multi_agent = ChessMultiAgentSystem() 