"""Enhanced LangGraph that uses an LLM to process and enhance A2A responses.

This graph demonstrates a more sophisticated approach where an LLM processes
the A2A agent responses and can provide additional context, formatting, or
follow-up questions.
"""

import asyncio
import logging
from typing import Dict, Any, Annotated, TypedDict, List, Optional
import os

import httpx
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from a2a.client import A2AClient, A2ACardResolver
from a2a.types import AgentCard, TaskState, SendMessageRequest, MessageSendParams
from uuid import uuid4

logger = logging.getLogger(__name__)


class EnhancedA2AState(TypedDict):
    """State for enhanced A2A client graph."""
    messages: Annotated[List, add_messages]
    a2a_response: Optional[str]
    processed_response: Optional[str]
    task_id: Optional[str]
    context_id: Optional[str]
    is_complete: bool
    error: Optional[str]
    needs_clarification: bool
    clarification_question: Optional[str]


class ResponseAnalysis(BaseModel):
    """Analysis of the A2A response."""
    is_satisfactory: bool = Field(description="Whether the response satisfactorily answers the user's question")
    needs_clarification: bool = Field(description="Whether the user needs to provide more information")
    should_enhance: bool = Field(description="Whether the response should be enhanced with additional context")
    enhancement_suggestions: List[str] = Field(description="Suggestions for enhancing the response", default_factory=list)
    clarification_question: Optional[str] = Field(description="Question to ask for clarification if needed")


class A2ACommunicationNode:
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
    
    async def execute_request(self, state: EnhancedA2AState) -> Dict[str, Any]:
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
                "error": None,
                "needs_clarification": False
            }
            
        except Exception as e:
            logger.error(f"Error in A2A request execution: {e}")
            return {
                "a2a_response": None,
                "task_id": None,
                "context_id": None,
                "is_complete": False,
                "error": str(e),
                "needs_clarification": False
            }


class ResponseAnalysisNode:
    """Node that analyzes the A2A response using an LLM."""
    
    def __init__(self):
        self.model = ChatOpenAI(
            model=os.getenv('TOOL_LLM_NAME', 'gpt-4o-mini'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            openai_api_base=os.getenv('TOOL_LLM_URL', 'https://api.openai.com/v1'),
            temperature=0,
        )
    
    async def analyze_response(self, state: EnhancedA2AState) -> Dict[str, Any]:
        """Analyze the A2A response and determine next steps."""
        if not state.get("a2a_response"):
            return {"processed_response": "No response to analyze"}
        
        # Get the original user query
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        original_query = user_messages[-1].content if user_messages else ""
        
        logger.info(f"Analyzing response for query: {original_query}")
        logger.info(f"Response to analyze: {state['a2a_response'][:100]}...")
        
        # Create analysis prompt
        analysis_prompt = f"""
        Analyze the following response from an AI agent to determine if it satisfactorily answers the user's question.

        User Query: {original_query}
        Agent Response: {state["a2a_response"]}

        Please analyze this response and determine:
        1. Is the response satisfactory and complete?
        2. Does the user need to provide more information?
        3. Could the response be enhanced with additional context or formatting?
        4. What specific suggestions would improve the response?

        Respond with a structured analysis.
        """
        
        try:
            # Use structured output for analysis
            model_with_analysis = self.model.with_structured_output(
                ResponseAnalysis,
                method="json_schema",
                include_raw=False
            )
            
            analysis = model_with_analysis.invoke(analysis_prompt)
            
            # Only set processed_response if we don't need clarification
            processed_response = None if analysis.needs_clarification else state["a2a_response"]
            
            logger.info(f"Analysis result - needs_clarification: {analysis.needs_clarification}")
            logger.info(f"Analysis result - should_enhance: {analysis.should_enhance}")
            
            return {
                "processed_response": processed_response,
                "needs_clarification": analysis.needs_clarification,
                "clarification_question": analysis.clarification_question
            }
            
        except Exception as e:
            logger.error(f"Error analyzing response: {e}")
            return {
                "processed_response": state["a2a_response"],
                "needs_clarification": False,
                "clarification_question": None
            }


class ResponseEnhancementNode:
    """Node that enhances the A2A response with additional context."""
    
    def __init__(self):
        self.model = ChatOpenAI(
            model=os.getenv('TOOL_LLM_NAME', 'gpt-4o-mini'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            openai_api_base=os.getenv('TOOL_LLM_URL', 'https://api.openai.com/v1'),
            temperature=0.1,
        )
    
    async def enhance_response(self, state: EnhancedA2AState) -> Dict[str, Any]:
        """Enhance the A2A response with additional context and formatting."""
        if not state.get("a2a_response"):
            return {"processed_response": "No response to enhance"}
        
        # Get the original user query
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        original_query = user_messages[-1].content if user_messages else ""
        
        logger.info(f"Enhancing response for query: {original_query}")
        logger.info(f"Original response length: {len(state['a2a_response'])}")
        
        enhancement_prompt = f"""
        You are a helpful assistant that enhances responses from other AI agents.
        
        Original User Query: {original_query}
        Agent Response: {state["a2a_response"]}
        
        Please enhance this response by:
        1. Adding relevant context or background information if helpful
        2. Improving formatting and readability with better structure
        3. Adding any relevant follow-up suggestions or questions
        4. Ensuring the response is comprehensive and user-friendly
        5. Adding bullet points, headers, or other formatting to improve readability
        6. Including additional insights or explanations where appropriate
        
        IMPORTANT: Make sure your enhanced response is noticeably different and more comprehensive than the original. 
        Add value through better formatting, additional context, or clearer explanations.
        
        Provide an enhanced version that maintains the original information while making it more useful and accessible.
        """
        
        try:
            enhanced_response = await self.model.ainvoke(enhancement_prompt)
            enhanced_content = enhanced_response.content
            logger.info(f"Enhanced response length: {len(enhanced_content)}")
            logger.info(f"Enhancement successful: {len(enhanced_content) > len(state['a2a_response'])}")
            return {"processed_response": enhanced_content}
            
        except Exception as e:
            logger.error(f"Error enhancing response: {e}")
            return {"processed_response": state["a2a_response"]}


def create_final_response_node(state: EnhancedA2AState) -> Dict[str, Any]:
    """Create the final response message."""
    if state.get("error"):
        return {
            "messages": [
                AIMessage(content=f"I encountered an error while communicating with the agent: {state['error']}")
            ]
        }
    
    if state.get("needs_clarification") and state.get("clarification_question"):
        return {
            "messages": [
                AIMessage(content=f"{state['processed_response']}\n\n{state['clarification_question']}")
            ]
        }
    
    if state.get("processed_response"):
        return {
            "messages": [
                AIMessage(content=state["processed_response"])
            ]
        }
    
    return {
        "messages": [
            AIMessage(content="I'm processing your request with the agent...")
        ]
    }


def route_after_analysis(state: EnhancedA2AState) -> str:
    """Route after response analysis."""
    if state.get("error"):
        return END
    
    if state.get("needs_clarification"):
        logger.info("Routing to create_response due to clarification needed")
        return "create_response"
    
    # If we have a response and no clarification is needed, enhance it
    if state.get("processed_response") and not state.get("needs_clarification"):
        logger.info("Routing to enhance_response for response enhancement")
        return "enhance_response"
    
    logger.info("Routing to create_response as default")
    return "create_response"


def route_after_enhancement(state: EnhancedA2AState) -> str:
    """Route after response enhancement."""
    return "create_response"


def build_enhanced_a2a_client_graph(agent_url: str = "http://localhost:10000", a2a_node: Optional[A2ACommunicationNode] = None) -> StateGraph:
    """Build the enhanced A2A client graph."""
    
    # Use provided node or create new one
    if a2a_node is None:
        a2a_node = A2ACommunicationNode(agent_url)
    
    # Create other nodes
    analysis_node = ResponseAnalysisNode()
    enhancement_node = ResponseEnhancementNode()
    
    # Create the graph
    graph = StateGraph(EnhancedA2AState)
    
    # Add nodes
    graph.add_node("a2a_request", a2a_node.execute_request)
    graph.add_node("analyze_response", analysis_node.analyze_response)
    graph.add_node("enhance_response", enhancement_node.enhance_response)
    graph.add_node("create_response", create_final_response_node)
    
    # Set entry point
    graph.set_entry_point("a2a_request")
    
    # Add edges
    graph.add_edge("a2a_request", "analyze_response")
    graph.add_conditional_edges(
        "analyze_response",
        route_after_analysis,
        {"enhance_response": "enhance_response", "create_response": "create_response", END: END}
    )
    graph.add_edge("enhance_response", "create_response")
    graph.add_edge("create_response", END)
    
    return graph.compile()


class EnhancedA2AClientAgent:
    """Enhanced agent that uses the A2A client graph with LLM processing."""
    
    def __init__(self, agent_url: str = "http://localhost:10000"):
        self.agent_url = agent_url
        self.a2a_node = A2ACommunicationNode(agent_url)
        self.graph = build_enhanced_a2a_client_graph(agent_url, self.a2a_node)
        
    async def initialize(self):
        """Initialize the agent."""
        await self.a2a_node.initialize()
    
    async def process_query(self, query: str, context_id: Optional[str] = None) -> str:
        """Process a query through the enhanced A2A agent."""
        try:
            # Initialize if not already done
            if not self.a2a_node.agent_card:
                await self.initialize()
            
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "a2a_response": None,
                "processed_response": None,
                "task_id": None,
                "context_id": context_id,
                "is_complete": False,
                "error": None,
                "needs_clarification": False,
                "clarification_question": None
            }
            
            # Run the graph
            final_state = None
            async for state in self.graph.astream(initial_state):
                final_state = state
            
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
async def test_enhanced_a2a_client():
    """Test the enhanced A2A client with sample queries."""
    agent = EnhancedA2AClientAgent()
    
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
            print(f"Enhanced Response: {response}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_enhanced_a2a_client())
