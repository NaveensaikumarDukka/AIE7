# A2A Client Graph - LangGraph Implementation

This directory contains a LangGraph implementation that acts as a client to interact with A2A protocol agent servers. The implementation demonstrates how to build intelligent client agents that can communicate with A2A servers and process their responses.

## Overview

The A2A Client Graph provides two main implementations:

1. **Simple A2A Client** (`a2a_client_graph.py`) - Basic client that communicates with A2A agents
2. **Enhanced A2A Client** (`enhanced_a2a_client_graph.py`) - Advanced client with LLM processing and response enhancement

## Architecture

### Simple A2A Client Graph

```
User Query → A2A Communication Node → Response Creation Node → Final Response
```

**Components:**
- `A2AClientNode`: Handles A2A protocol communication
- `create_response_node`: Creates response messages
- `should_continue`: Routing logic for graph flow

### Enhanced A2A Client Graph

```
User Query → A2A Communication → Response Analysis → Response Enhancement → Final Response
```

**Components:**
- `A2ACommunicationNode`: Handles A2A protocol communication
- `ResponseAnalysisNode`: Analyzes responses using LLM
- `ResponseEnhancementNode`: Enhances responses with additional context
- `create_final_response_node`: Creates final response messages

## Features

### Simple Client Features
- ✅ Direct A2A protocol communication
- ✅ Task creation and management
- ✅ Response streaming
- ✅ Error handling
- ✅ Basic response formatting

### Enhanced Client Features
- ✅ All simple client features
- ✅ LLM-powered response analysis
- ✅ Intelligent response enhancement
- ✅ Clarification request handling
- ✅ Context-aware processing
- ✅ Structured response evaluation

## Installation

1. Ensure you have the required dependencies:
```bash
uv sync
```

2. Set up your environment variables:
```bash
python setup.py
```

3. Make sure your A2A agent server is running:
```bash
uv run python -m app
```

## Usage

### Command Line Interface

The easiest way to interact with the A2A client is through the CLI:

```bash
# Start interactive chat with simple client
uv run python app/a2a_client_cli.py chat

# Start interactive chat with enhanced client
uv run python app/a2a_client_cli.py chat --enhanced

# Test the client with predefined queries
uv run python app/a2a_client_cli.py test --enhanced

# Get information about the A2A agent
uv run python app/a2a_client_cli.py info

# Single query mode
uv run python app/a2a_client_cli.py chat --query "What are the latest AI developments?"
```

### Programmatic Usage

#### Simple Client

```python
import asyncio
from app.a2a_client_graph import A2AClientAgent

async def main():
    # Create client agent
    agent = A2AClientAgent("http://localhost:10000")
    
    # Initialize connection
    await agent.initialize()
    
    # Process a query
    response = await agent.process_query("What are the latest developments in AI?")
    print(response)

asyncio.run(main())
```

#### Enhanced Client

```python
import asyncio
from app.enhanced_a2a_client_graph import EnhancedA2AClientAgent

async def main():
    # Create enhanced client agent
    agent = EnhancedA2AClientAgent("http://localhost:10000")
    
    # Initialize connection
    await agent.initialize()
    
    # Process a query with enhanced processing
    response = await agent.process_query("What are the latest developments in AI?")
    print(response)

asyncio.run(main())
```

### Direct Graph Usage

```python
import asyncio
from app.enhanced_a2a_client_graph import build_enhanced_a2a_client_graph
from langchain_core.messages import HumanMessage

async def main():
    # Build the graph
    graph = build_enhanced_a2a_client_graph("http://localhost:10000")
    
    # Create initial state
    initial_state = {
        "messages": [HumanMessage(content="What are the latest AI developments?")],
        "a2a_response": None,
        "processed_response": None,
        "task_id": None,
        "context_id": None,
        "is_complete": False,
        "error": None,
        "needs_clarification": False,
        "clarification_question": None
    }
    
    # Run the graph
    async for state in graph.astream(initial_state):
        if state.get("processed_response"):
            print(f"Response: {state['processed_response']}")

asyncio.run(main())
```

## Configuration

### Environment Variables

Required environment variables (set via `setup.py` or `.env` file):

```bash
OPENAI_API_KEY=your_openai_api_key
TOOL_LLM_URL=https://api.openai.com/v1
TOOL_LLM_NAME=gpt-4o-mini
TAVILY_API_KEY=your_tavily_api_key
```

### Agent Server Configuration

The client connects to an A2A agent server. Default configuration:
- **URL**: `http://localhost:10000`
- **Protocol**: A2A (Agent-to-Agent)
- **Capabilities**: Web search, academic papers, document retrieval

## Examples

### Example 1: Web Search Query

```python
query = "What are the latest developments in artificial intelligence?"
response = await agent.process_query(query)
```

**Simple Client Response:**
```
Based on recent web search results, the latest developments in AI include...
```

**Enhanced Client Response:**
```
Based on recent web search results, the latest developments in AI include...

**Key Highlights:**
- [Enhanced formatting and bullet points]
- [Additional context and background]
- [Follow-up suggestions]

**Related Topics:**
- [Suggestions for further exploration]
```

### Example 2: Academic Paper Search

```python
query = "Find recent papers on large language models"
response = await agent.process_query(query)
```

### Example 3: Document Retrieval

```python
query = "What do the policy documents say about student loans?"
response = await agent.process_query(query)
```

## Error Handling

The client includes comprehensive error handling:

- **Connection Errors**: Automatic retry and fallback
- **A2A Protocol Errors**: Graceful degradation
- **LLM Errors**: Fallback to simple responses
- **Network Errors**: Timeout and retry logic

## Testing

Run the test suite:

```bash
# Test simple client
uv run python app/a2a_client_cli.py test

# Test enhanced client
uv run python app/a2a_client_cli.py test --enhanced

# Test individual components
uv run python app/a2a_client_graph.py
uv run python app/enhanced_a2a_client_graph.py
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the A2A agent server is running
   - Check the agent URL configuration
   - Verify network connectivity

2. **API Key Errors**
   - Run `python setup.py` to configure environment
   - Check `.env` file for correct API keys
   - Verify API key permissions

3. **Import Errors**
   - Ensure all dependencies are installed: `uv sync`
   - Check Python version (requires 3.12+)
   - Verify virtual environment activation

4. **A2A Protocol Errors**
   - Check agent server logs
   - Verify A2A protocol version compatibility
   - Ensure agent server supports required capabilities

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Architecture Details

### State Management

The graphs use typed state dictionaries:

```python
class A2ARequestState(TypedDict):
    messages: Annotated[List, add_messages]
    a2a_response: Optional[str]
    task_id: Optional[str]
    context_id: Optional[str]
    is_complete: bool
    error: Optional[str]
```

### Node Functions

Each node is a pure function that:
- Takes state as input
- Returns state updates
- Handles errors gracefully
- Maintains async compatibility

### Routing Logic

Conditional edges determine graph flow:
- Error conditions → END
- Completion conditions → END
- Processing conditions → Continue

## Contributing

To extend the A2A client graph:

1. **Add New Nodes**: Create new node functions
2. **Modify State**: Update state schemas
3. **Update Routing**: Modify conditional edges
4. **Add Tests**: Include test cases
5. **Update Documentation**: Document new features

## License

This implementation is part of the A2A LangGraph project and follows the same licensing terms.
