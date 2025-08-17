#!/usr/bin/env python3
"""Test script to verify enhanced client response enhancement."""

import asyncio
import logging
import os
from dotenv import load_dotenv

from app.enhanced_a2a_client_graph import EnhancedA2AClientAgent
from app.a2a_client_graph import A2AClientAgent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_enhancement():
    """Test that enhanced client provides better responses than simple client."""
    print("🧪 Testing Response Enhancement")
    print("="*50)
    
    # Test query
    query = "What is machine learning?"
    
    try:
        # Test simple client
        print("\n🤖 Testing Simple Client...")
        simple_agent = A2AClientAgent()
        await simple_agent.initialize()
        simple_response = await simple_agent.process_query(query)
        print(f"Simple Response Length: {len(simple_response)}")
        print(f"Simple Response: {simple_response[:200]}...")
        
        # Test enhanced client
        print("\n🚀 Testing Enhanced Client...")
        enhanced_agent = EnhancedA2AClientAgent()
        await enhanced_agent.initialize()
        enhanced_response = await enhanced_agent.process_query(query)
        print(f"Enhanced Response Length: {len(enhanced_response)}")
        print(f"Enhanced Response: {enhanced_response[:200]}...")
        
        # Compare responses
        print("\n📊 Comparison:")
        print(f"Simple Response Length: {len(simple_response)}")
        print(f"Enhanced Response Length: {len(enhanced_response)}")
        print(f"Length Difference: {len(enhanced_response) - len(simple_response)}")
        print(f"Responses are different: {simple_response != enhanced_response}")
        
        if len(enhanced_response) > len(simple_response):
            print("✅ Enhancement successful - enhanced response is longer")
        else:
            print("❌ Enhancement failed - enhanced response is not longer")
            
        if simple_response != enhanced_response:
            print("✅ Enhancement successful - responses are different")
        else:
            print("❌ Enhancement failed - responses are identical")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_enhancement())
