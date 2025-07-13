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
    
    def __init__(self, openai_key: str = None, langsmith_key: str = None, tavily_key: str = None):
        self.openai_key = openai_key
        self.langsmith_key = langsmith_key
        self.tavily_key = tavily_key
        
        # Initialize models only if API key is provided
        if openai_key:
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
        else:
            # Models will be initialized per request
            self.supervisor_model = None
            self.rag_agent_model = None
            self.chess_agent_model = None
        
        # Setup tools if API key is available
        if openai_key:
            self.tools = []
            if tavily_key:
                self.tools.append(TavilySearchResults(max_results=3, api_key=tavily_key))
            
            # Add chess-specific tools
            self.tools.extend([get_player_stats, analyze_pgn, get_recent_games])
            
            # Bind tools to chess agent
            self.chess_agent_with_tools = self.chess_agent_model.bind_tools(self.tools)
            self.tool_node = ToolNode(self.tools)
        else:
            # Tools will be initialized per request
            self.tools = []
            self.chess_agent_with_tools = None
            self.tool_node = None
        
        # Build the graph if API key is available
        if openai_key:
            self.graph = self._build_graph()
        else:
            # Graph will be built per request
            self.graph = None
    
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
        
        # Compile with recursion limit to prevent infinite loops
        return workflow.compile(
            checkpointer=None,
            interrupt_before=None,
            interrupt_after=None,
            debug=False
        )
    
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
            
            # Check for greetings - handle them directly
            simple_greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
            if user_query.lower().strip() in simple_greetings:
                greeting_response = "Hello! I'm your Chess Knowledge Assistant. I can help you with chess theory, openings, tactics, endgames, and strategy. What would you like to learn about chess today?"
                return {
                    **state,
                    "messages": state["messages"] + [AIMessage(content=greeting_response)],
                    "rag_context": {"context": "", "context_count": 0, "similarity_scores": []},
                    "current_agent": "rag_agent"
                }
            
            # Get context from RAG system
            context_data = document_retriever.get_context_for_query(
                query=user_query,
                max_chunks=8,
                max_chars=6000
            )
            
            # If no context found, provide a helpful general response
            if context_data["context_count"] == 0:
                general_response = f"""I don't have specific information about "{user_query}" in my chess knowledge base. However, I can help you with:

• Chess openings and opening principles
• Tactical patterns and combinations
• Endgame techniques and theory
• Chess strategy and positional play
• Chess history and famous games

Could you ask me about one of these chess topics, or rephrase your question to be more specific about what chess concept you'd like to learn about?"""
                
                return {
                    **state,
                    "messages": state["messages"] + [AIMessage(content=general_response)],
                    "rag_context": context_data,
                    "current_agent": "rag_agent"
                }
            
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
            fallback_response = "I apologize, but I'm having trouble accessing my chess knowledge base right now. Please try asking me about general chess concepts, and I'll do my best to help!"
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
            
            # Get or initialize chess_data for context preservation
            chess_data = state.get("chess_data", {})
            
            # Increment iteration count to prevent infinite loops
            iteration_count = state.get("iteration_count", 0) + 1
            
            # If we've been iterating too many times, provide a direct response
            if iteration_count > 5:
                return {
                    **state,
                    "messages": state["messages"] + [AIMessage(content="I've gathered the information but seem to be in a loop. Let me provide a direct response based on what I have.")],
                    "current_agent": "chess_agent",
                    "chess_data": chess_data,
                    "iteration_count": iteration_count
                }
            
            # Extract username from query if provided
            import re
            username_match = re.search(r'\b([a-zA-Z0-9_-]+)\b', user_query)
            if username_match and any(word in user_query.lower() for word in ['player', 'user', 'username', 'analyze', 'games', 'stats']):
                potential_username = username_match.group(1)
                # Store the username for future reference
                chess_data["last_username"] = potential_username
            
            # If user asks about "my" games/stats but doesn't provide username, check if we have one stored
            if any(word in user_query.lower() for word in ['my games', 'my stats', 'my last', 'my recent', 'analyze my']) and "last_username" in chess_data:
                stored_username = chess_data["last_username"]
                user_query = f"{user_query} for username {stored_username}"
            
            # Check if user is asking for game analysis without specifying count
            if any(word in user_query.lower() for word in ['analyze games', 'recent games', 'my games', 'game analysis']) and not any(num in user_query for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '15', '20']):
                return {
                    **state,
                    "messages": state["messages"] + [AIMessage(content="I'd be happy to analyze your games! How many of your recent games would you like me to analyze? I can analyze up to 20 games at a time.")],
                    "current_agent": "chess_agent",
                    "chess_data": chess_data,
                    "iteration_count": iteration_count
                }
            
            chess_system_prompt = f"""You are a Chess.com Analysis Agent. You specialize in:
- Analyzing Chess.com player statistics and profiles
- Analyzing chess games in PGN format  
- Retrieving recent games for players
- Providing chess insights based on live data

Context: {f"Previously analyzed username: {chess_data.get('last_username', 'None')}" if chess_data.get('last_username') else "No previous username context"}

IMPORTANT: 
- When getting recent games, always specify a reasonable limit (max 20 games)
- If you already have the data you need, do NOT call tools again
- Provide analysis based on the information you have
- Always ask users how many games they want analyzed if not specified

Use the available tools when you need to:
- Get player statistics from Chess.com
- Analyze chess games
- Retrieve recent games (with a limit parameter)

Always provide helpful, accurate chess analysis. If asked about non-chess topics, politely decline.
If the user refers to "my" games/stats and you have a previously stored username, use that username."""
            
            # Process with tools
            messages = [
                SystemMessage(content=chess_system_prompt),
                HumanMessage(content=user_query)
            ]
            
            response = self.chess_agent_with_tools.invoke(messages)
            
            # If the response involves tool calls, update the chess_data with any username found
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    if 'username' in tool_call.get('args', {}):
                        chess_data["last_username"] = tool_call['args']['username']
            
            return {
                **state,
                "messages": state["messages"] + [response],
                "current_agent": "chess_agent",
                "chess_data": chess_data,
                "iteration_count": iteration_count
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
                # Preserve chess_data and other persistent state
                initial_state["chess_data"] = conversation_state.get("chess_data", {})
                initial_state["rag_context"] = conversation_state.get("rag_context", {})
                initial_state["messages"] = conversation_state.get("messages", []) + [HumanMessage(content=message)]
            
            # Run the graph with recursion limit
            final_state = self.graph.invoke(initial_state, config={"recursion_limit": 15})
            
            # Extract response
            last_message = final_state["messages"][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            return {
                "response": response_content,
                "state": {
                    "current_agent": final_state.get("current_agent", ""),
                    "supervisor_decision": final_state.get("supervisor_decision", ""),
                    "rag_context": final_state.get("rag_context", {}),
                    "chess_data": final_state.get("chess_data", {}),
                    "iteration_count": final_state.get("iteration_count", 0),
                    "messages": final_state.get("messages", [])[-10:]  # Keep last 10 messages for context
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

    async def process_query(self, query: str, conversation_state: Dict[str, Any], api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Process a query through the multi-agent system (for compatibility with router)"""
        try:
            # Handle greetings directly
            simple_greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
            if query.lower().strip() in simple_greetings:
                return {
                    "response": "Hello! I'm your Chess Assistant. I can help you analyze games, explain chess concepts, provide strategy advice, and analyze Chess.com player data. What would you like to know about chess?",
                    "agent_used": "supervisor",
                    "rag_sources": 0,
                    "conversation_state": conversation_state
                }
            
            # Always use API keys from the request
            self.openai_key = api_keys.get("openai_key")
            self.langsmith_key = api_keys.get("langsmith_key")
            self.tavily_key = api_keys.get("tavily_key")
            
            # Validate OpenAI API key
            if not self.openai_key or self.openai_key == "dummy":
                raise ValueError("Valid OpenAI API key is required")
            
            # Reinitialize models with current API keys
            self.supervisor_model = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=self.openai_key
            )
            self.rag_agent_model = ChatOpenAI(
                model="gpt-4o-mini", 
                temperature=0.1,
                api_key=self.openai_key
            )
            self.chess_agent_model = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=self.openai_key
            )
            
            # Initialize tools
            self.tools = []
            if self.tavily_key:
                self.tools.append(TavilySearchResults(max_results=3, api_key=self.tavily_key))
            self.tools.extend([get_player_stats, analyze_pgn, get_recent_games])
            self.chess_agent_with_tools = self.chess_agent_model.bind_tools(self.tools)
            self.tool_node = ToolNode(self.tools)
            
            # Rebuild graph with new configuration
            self.graph = self._build_graph()
            
            # Process the message using the new interface
            result = await self.process_message(query, conversation_state)
            
            # Extract agent information from the state
            agent_used = result.get("state", {}).get("supervisor_decision", "unknown").lower()
            if agent_used == "final_response":
                agent_used = "supervisor"
            elif agent_used == "rag_agent":
                agent_used = "rag agent"
            elif agent_used == "chess_agent":
                agent_used = "chess agent"
            
            # Update conversation state with the new state
            updated_conversation_state = {
                **conversation_state,
                **result.get("state", {})
            }
            
            return {
                "response": result["response"],
                "agent_used": agent_used,
                "rag_sources": result.get("state", {}).get("rag_context", {}).get("sources_count", 0),
                "conversation_state": updated_conversation_state
            }
            
        except Exception as e:
            logger.error(f"Error in process_query: {e}")
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "agent_used": "error",
                "rag_sources": 0,
                "conversation_state": conversation_state
            }

# Global instance for compatibility - API keys will be provided per request
chess_multi_agent = ChessMultiAgentSystem(openai_key=None) 