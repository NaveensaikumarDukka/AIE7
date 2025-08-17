#!/usr/bin/env python3
"""Simple test to debug graph execution."""

import asyncio
import logging
from dotenv import load_dotenv

from app.a2a_client_graph import A2AClientAgent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_simple_graph():
    """Test the simple A2A client graph."""
    print("🧪 Testing Simple A2A Client Graph")
    print("="*50)
    
    try:
        # Create agent
        agent = A2AClientAgent()
        print("✅ Agent created")
        
        # Initialize
        await agent.initialize()
        print("✅ Agent initialized")
        
        # Test query
        query = "What is machine learning?"
        print(f"📝 Query: {query}")
        
        # Process query
        print("🔄 Processing query...")
        response = await agent.process_query(query)
        print(f"🤖 Response: {response}")
        
        if "No response received" in response:
            print("❌ Still getting 'No response received'")
        else:
            print("✅ Got a proper response!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_simple_graph())
