#!/usr/bin/env python3
"""
Test script to verify that the event loop fix works correctly.
This script tests the enhanced A2A client to ensure it doesn't encounter
"Event loop is closed" errors when making multiple requests.
"""

import asyncio
import logging
import os
import sys
from typing import List

from app.enhanced_a2a_client_graph import EnhancedA2AClientAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


async def test_multiple_queries(agent: EnhancedA2AClientAgent, queries: List[str]) -> None:
    """Test multiple queries to ensure event loop works correctly."""
    print(f"🧪 Testing {len(queries)} queries...")
    print("=" * 60)
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}/{len(queries)}: {query}")
        print("-" * 40)
        
        try:
            response = await agent.process_query(query)
            print(f"✅ Response: {response[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
            if "Event loop is closed" in str(e):
                print("🚨 EVENT LOOP ERROR DETECTED!")
                raise
        print("-" * 40)
    
    print("\n✅ All queries completed successfully!")


async def test_interactive_session(agent: EnhancedA2AClientAgent) -> None:
    """Test interactive session to ensure event loop works correctly."""
    print("\n🎮 Testing interactive session...")
    print("=" * 60)
    
    # Simulate multiple user inputs
    test_inputs = [
        "What is artificial intelligence?",
        "Tell me about machine learning",
        "What are neural networks?",
        "Explain deep learning"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n💬 User Input {i}: {user_input}")
        print("🤔 Processing...")
        
        try:
            response = await agent.process_query(user_input)
            print(f"🤖 Response: {response[:150]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
            if "Event loop is closed" in str(e):
                print("🚨 EVENT LOOP ERROR DETECTED!")
                raise
    
    print("\n✅ Interactive session completed successfully!")


async def main():
    """Main test function."""
    try:
        # Check for required environment variables
        if not os.getenv('OPENAI_API_KEY'):
            raise MissingAPIKeyError('OPENAI_API_KEY environment variable not set.')
        
        print("🔧 Testing Event Loop Fix for Enhanced A2A Client")
        print("=" * 60)
        
        # Initialize the agent
        agent_url = "http://localhost:10000"
        agent = EnhancedA2AClientAgent(agent_url)
        
        print(f"🔗 Connecting to agent at: {agent_url}")
        await agent.initialize()
        print("✅ Agent initialized successfully!")
        
        # Test queries
        test_queries = [
            "What are the latest developments in artificial intelligence?",
            "Search for recent papers on large language models",
            "What do you know about machine learning?",
            "Can you help me understand neural networks?",
            "What are the current trends in AI research?"
        ]
        
        # Test multiple queries
        await test_multiple_queries(agent, test_queries)
        
        # Test interactive session
        await test_interactive_session(agent)
        
        print("\n🎉 All tests passed! Event loop fix is working correctly.")
        
    except MissingAPIKeyError as e:
        logger.error(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        logger.error(f'Test failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
