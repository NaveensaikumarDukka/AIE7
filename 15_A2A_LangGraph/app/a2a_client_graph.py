"""LangGraph Graph that acts as a client to interact with A2A agent server.

This graph demonstrates how to use the A2A protocol to communicate with
the agent server and process responses.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Annotated, TypedDict, List, Optional
from datetime import datetime

import httpx
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from a2a.client import A2AClient, A2ACardResolver
from a2a.types import AgentCard, TaskState, SendMessageRequest, MessageSendParams
from uuid import uuid4

logger = logging.getLogger(__name__)


class A2ARequestState(TypedDict):
    """State for A2A client graph."""
    messages: Annotated[List, add_messages]
    a2a_response: Optional[str]
    task_id: Optional[str]
    context_id: Optional[str]
    is_complete: bool
    error: Optional[str]


class A2ARequestFormat(BaseModel):
    """Format for A2A requests."""
    query: str
    context_id: Optional[str] = None


class A2AClientNode:
    """Node that handles A2A protocol communication."""
    
    def __init__(self, agent_url: str = "http://localhost:10000"):
        self.agent_url = agent_url
        self.client: Optional[A2AClient] = None
        self.agent_card: Optional[AgentCard] = None
        self.httpx_client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self):
        """Initialize the client and get agent capabilities."""
        try:
            # Create httpx client with longer timeout
            self.httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
            
            # Initialize A2ACardResolver to fetch agent card
            resolver = A2ACardResolver(
                httpx_client=self.httpx_client,
                base_url=self.agent_url,
            )
            
            # Fetch the agent card
            self.agent_card = await resolver.get_agent_card()
            
            # Initialize A2AClient with the agent card
            self.client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=self.agent_card
            )
            
            logger.info(f"Connected to agent: {self.agent_card.name}")
            logger.info(f"Available skills: {[skill.name for skill in self.agent_card.skills]}")
        except Exception as e:
            logger.error(f"Failed to initialize A2A client: {e}")
            raise
    
    async def execute_request(self, state: A2ARequestState) -> Dict[str, Any]:
        """Execute a request through the A2A protocol."""
        try:
            if not self.client:
                return {"error": "Client not initialized"}
            
            # Get the latest user message
            user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
            if not user_messages:
                return {"error": "No user message found"}
            
            latest_user_message = user_messages[-1].content
            
            # Create message payload
            send_message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {'kind': 'text', 'text': latest_user_message}
                    ],
                    'message_id': uuid4().hex,
                },
            }
            
            # Create request
            request = SendMessageRequest(
                id=str(uuid4()), 
                params=MessageSendParams(**send_message_payload)
            )
            
            logger.info(f"Sending message: {latest_user_message}")
            
            # Send message and get response
            response = await self.client.send_message(request)
            
            # Extract response from artifacts
            response_parts = []
            if response.root.result.artifacts:
                for artifact in response.root.result.artifacts:
                    if hasattr(artifact, 'parts'):
                        for part in artifact.parts:
                            if hasattr(part, 'root') and hasattr(part.root, 'text'):
                                response_parts.append(part.root.text)
            
            # Combine all response parts
            full_response = "\n".join(response_parts) if response_parts else "No response received"
            
            logger.info(f"Received response: {full_response[:100]}...")
            
            return {
                "a2a_response": full_response,
                "task_id": response.root.result.id,
                "context_id": response.root.result.context_id,
                "is_complete": True,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error in A2A request execution: {e}")
            return {
                "a2a_response": None,
                "task_id": None,
                "context_id": None,
                "is_complete": False,
                "error": str(e)
            }


def create_response_node(state: A2ARequestState) -> Dict[str, Any]:
    """Create a response message based on A2A response."""
    if state.get("error"):
        return {
            "messages": [
                AIMessage(content=f"I encountered an error while communicating with the agent: {state['error']}")
            ]
        }
    
    if state.get("a2a_response"):
        return {
            "messages": [
                AIMessage(content=state["a2a_response"])
            ]
        }
    
    return {
        "messages": [
            AIMessage(content="I'm processing your request with the agent...")
        ]
    }


def should_continue(state: A2ARequestState) -> str:
    """Determine if the graph should continue or end."""
    if state.get("error"):
        return END
    
    if state.get("is_complete", False):
        return END
    
    return "continue"


def build_a2a_client_graph(agent_url: str = "http://localhost:10000", a2a_node: Optional[A2AClientNode] = None) -> StateGraph:
    """Build the A2A client graph."""
    
    # Use provided node or create new one
    if a2a_node is None:
        a2a_node = A2AClientNode(agent_url)
    
    # Create the graph
    graph = StateGraph(A2ARequestState)
    
    # Add nodes
    graph.add_node("a2a_request", a2a_node.execute_request)
    graph.add_node("create_response", create_response_node)
    
    # Set entry point
    graph.set_entry_point("a2a_request")
    
    # Add edges
    graph.add_edge("a2a_request", "create_response")
    graph.add_conditional_edges(
        "create_response",
        should_continue,
        {"continue": "a2a_request", END: END}
    )
    
    return graph.compile()


class A2AClientAgent:
    """High-level agent that uses the A2A client graph."""
    
    def __init__(self, agent_url: str = "http://localhost:10000"):
        self.agent_url = agent_url
        self.a2a_node = A2AClientNode(agent_url)
        self.graph = build_a2a_client_graph(agent_url, self.a2a_node)
        
    async def initialize(self):
        """Initialize the agent."""
        await self.a2a_node.initialize()
    
    async def process_query(self, query: str, context_id: Optional[str] = None) -> str:
        """Process a query through the A2A agent."""
        try:
            # Initialize if not already done
            if not self.a2a_node.agent_card:
                await self.initialize()
            
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "a2a_response": None,
                "task_id": None,
                "context_id": context_id,
                "is_complete": False,
                "error": None
            }
            
            logger.info(f"Starting graph execution with query: {query}")
            
            # Run the graph
            final_state = None
            step_count = 0
            async for state in self.graph.astream(initial_state):
                step_count += 1
                logger.info(f"Graph step {step_count}: {state}")
                final_state = state
            
            logger.info(f"Graph execution completed in {step_count} steps")
            logger.info(f"Final state: {final_state}")
            
            if final_state and "create_response" in final_state:
                messages = final_state["create_response"].get("messages", [])
                if messages and hasattr(messages[0], 'content'):
                    return messages[0].content
            elif final_state and final_state.get("error"):
                return f"Error: {final_state['error']}"
            else:
                return "No response received from the agent."
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error processing your request: {str(e)}"


# Example usage and testing
async def test_a2a_client():
    """Test the A2A client with a sample query."""
    agent = A2AClientAgent()
    
    try:
        await agent.initialize()
        
        # Test queries
        test_queries = [
            "What are the latest developments in AI?",
            "Search for recent papers on large language models",
            "What do you know about machine learning?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            print("-" * 50)
            response = await agent.process_query(query)
            print(f"Response: {response}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_a2a_client())
