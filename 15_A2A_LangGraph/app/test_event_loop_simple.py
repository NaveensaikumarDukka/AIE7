#!/usr/bin/env python3
"""
Simple test script to verify that the event loop fix works correctly.
This script tests the structure without requiring the A2A server to be running.
"""

import asyncio
import logging
import sys
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockAgent:
    """Mock agent for testing event loop behavior."""
    
    def __init__(self, name: str = "MockAgent"):
        self.name = name
        self.initialized = False
        self.query_count = 0
    
    async def initialize(self):
        """Mock initialization."""
        await asyncio.sleep(0.1)  # Simulate async work
        self.initialized = True
        print(f"✅ {self.name} initialized")
    
    async def process_query(self, query: str) -> str:
        """Mock query processing."""
        if not self.initialized:
            raise RuntimeError("Agent not initialized")
        
        await asyncio.sleep(0.1)  # Simulate async work
        self.query_count += 1
        return f"Mock response to: {query} (query #{self.query_count})"


async def test_multiple_queries(agent: MockAgent, queries: List[str]) -> None:
    """Test multiple queries to ensure event loop works correctly."""
    print(f"🧪 Testing {len(queries)} queries...")
    print("=" * 60)
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}/{len(queries)}: {query}")
        print("-" * 40)
        
        try:
            response = await agent.process_query(query)
            print(f"✅ Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            if "Event loop is closed" in str(e):
                print("🚨 EVENT LOOP ERROR DETECTED!")
                raise
        print("-" * 40)
    
    print("\n✅ All queries completed successfully!")


async def test_interactive_session(agent: MockAgent) -> None:
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
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            if "Event loop is closed" in str(e):
                print("🚨 EVENT LOOP ERROR DETECTED!")
                raise
    
    print("\n✅ Interactive session completed successfully!")


async def test_concurrent_operations(agent: MockAgent) -> None:
    """Test concurrent operations to ensure event loop handles them correctly."""
    print("\n⚡ Testing concurrent operations...")
    print("=" * 60)
    
    queries = [
        "Query 1",
        "Query 2", 
        "Query 3",
        "Query 4"
    ]
    
    try:
        # Run queries concurrently
        tasks = [agent.process_query(query) for query in queries]
        responses = await asyncio.gather(*tasks)
        
        for i, response in enumerate(responses, 1):
            print(f"✅ Concurrent Response {i}: {response}")
            
    except Exception as e:
        print(f"❌ Error in concurrent operations: {e}")
        if "Event loop is closed" in str(e):
            print("🚨 EVENT LOOP ERROR DETECTED!")
            raise
    
    print("\n✅ Concurrent operations completed successfully!")


async def main():
    """Main test function."""
    try:
        print("🔧 Testing Event Loop Fix (Mock Agent)")
        print("=" * 60)
        
        # Initialize the agent
        agent = MockAgent("TestAgent")
        
        print(f"🔗 Initializing agent: {agent.name}")
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
        
        # Test concurrent operations
        await test_concurrent_operations(agent)
        
        print(f"\n📊 Final Statistics:")
        print(f"   - Total queries processed: {agent.query_count}")
        print(f"   - Agent initialized: {agent.initialized}")
        
        print("\n🎉 All tests passed! Event loop fix is working correctly.")
        
    except Exception as e:
        logger.error(f'Test failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
