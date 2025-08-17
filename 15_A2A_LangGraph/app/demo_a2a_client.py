#!/usr/bin/env python3
"""Demo script for the A2A Client Graph.

This script demonstrates how to use the A2A client graph to interact with
the A2A agent server through the A2A protocol.
"""

import asyncio
import logging
import os
import sys
from typing import List, Dict, Any

import httpx
from dotenv import load_dotenv

from app.enhanced_a2a_client_graph import EnhancedA2AClientAgent
from app.a2a_client_graph import A2AClientAgent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoQueries:
    """Predefined demo queries to showcase different capabilities."""
    
    WEB_SEARCH_QUERIES = [
        "What are the latest developments in artificial intelligence?",
        "What's happening with quantum computing research?",
        "What are the current trends in machine learning?",
    ]
    
    ACADEMIC_QUERIES = [
        "Find recent papers on large language models",
        "Search for papers about transformer architecture",
        "What are the latest research papers on computer vision?",
    ]
    
    GENERAL_QUERIES = [
        "What do you know about neural networks?",
        "Can you explain machine learning in simple terms?",
        "What are the main types of AI?",
    ]
    
    @classmethod
    def get_all_queries(cls) -> List[str]:
        """Get all demo queries."""
        return (
            cls.WEB_SEARCH_QUERIES +
            cls.ACADEMIC_QUERIES +
            cls.GENERAL_QUERIES
        )


class A2AClientDemo:
    """Demo class for showcasing A2A client functionality."""
    
    def __init__(self, agent_url: str = "http://localhost:10000"):
        self.agent_url = agent_url
        self.simple_agent = A2AClientAgent(agent_url)
        self.enhanced_agent = EnhancedA2AClientAgent(agent_url)
        
    async def initialize(self):
        """Initialize both client agents."""
        print("🔧 Initializing A2A Client Agents...")
        
        try:
            await self.simple_agent.initialize()
            print("✅ Simple A2A Client initialized")
            
            await self.enhanced_agent.initialize()
            print("✅ Enhanced A2A Client initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize agents: {e}")
            raise
    
    async def demo_simple_client(self, queries: List[str]):
        """Demonstrate the simple A2A client."""
        print("\n" + "="*60)
        print("🤖 SIMPLE A2A CLIENT DEMO")
        print("="*60)
        
        for i, query in enumerate(queries, 1):
            print(f"\n📝 Query {i}/{len(queries)}: {query}")
            print("-" * 50)
            
            try:
                response = await self.simple_agent.process_query(query)
                print(f"💬 Response: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 50)
            
            # Small delay between queries
            await asyncio.sleep(1)
    
    async def demo_enhanced_client(self, queries: List[str]):
        """Demonstrate the enhanced A2A client."""
        print("\n" + "="*60)
        print("🚀 ENHANCED A2A CLIENT DEMO")
        print("="*60)
        
        for i, query in enumerate(queries, 1):
            print(f"\n📝 Query {i}/{len(queries)}: {query}")
            print("-" * 50)
            
            try:
                response = await self.enhanced_agent.process_query(query)
                print(f"💬 Enhanced Response: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 50)
            
            # Small delay between queries
            await asyncio.sleep(1)
    
    async def demo_comparison(self, query: str):
        """Compare simple vs enhanced client responses."""
        print("\n" + "="*60)
        print("🔄 CLIENT COMPARISON DEMO")
        print("="*60)
        
        print(f"\n📝 Query: {query}")
        print("="*60)
        
        # Simple client response
        print("\n🤖 Simple Client Response:")
        print("-" * 30)
        try:
            simple_response = await self.simple_agent.process_query(query)
            print(simple_response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Enhanced client response
        print("\n🚀 Enhanced Client Response:")
        print("-" * 30)
        try:
            enhanced_response = await self.enhanced_agent.process_query(query)
            print(enhanced_response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("="*60)
    
    async def demo_interactive(self):
        """Interactive demo mode."""
        print("\n" + "="*60)
        print("🎮 INTERACTIVE DEMO MODE")
        print("="*60)
        print("Type your questions and see both clients respond!")
        print("Type 'quit' to exit, 'help' for commands.")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n💬 Your question: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print("\n📖 Available commands:")
                    print("  help     - Show this help")
                    print("  quit     - Exit interactive mode")
                    print("  simple   - Use simple client only")
                    print("  enhanced - Use enhanced client only")
                    print("  compare  - Compare both clients")
                    continue
                
                if user_input.lower() == 'simple':
                    print("🤖 Switching to Simple Client mode...")
                    continue
                
                if user_input.lower() == 'enhanced':
                    print("🚀 Switching to Enhanced Client mode...")
                    continue
                
                if user_input.lower() == 'compare':
                    await self.demo_comparison("What are the latest AI developments?")
                    continue
                
                if not user_input:
                    continue
                
                print("\n🤔 Processing...")
                
                # Get response from enhanced client (default)
                try:
                    response = await self.enhanced_agent.process_query(user_input)
                    print(f"🤖 Response: {response}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")


async def main():
    """Main demo function."""
    print("🎯 A2A Client Graph Demo")
    print("="*60)
    
    # Check if agent server is running
    agent_url = "http://localhost:10000"
    
    # Create demo instance
    demo = A2AClientDemo(agent_url)
    
    try:
        # Initialize agents
        await demo.initialize()
        
        # Get demo queries
        queries = DemoQueries.get_all_queries()
        
        # Run demos
        print("\n🎬 Starting demos...")
        
        # Simple client demo (first 3 queries)
        await demo.demo_simple_client(queries[:3])
        
        # Enhanced client demo (first 3 queries)
        await demo.demo_enhanced_client(queries[:3])
        
        # Comparison demo
        await demo.demo_comparison("What are the latest developments in AI?")
        
        # Interactive demo
        await demo.demo_interactive()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_quick_demo():
    """Run a quick demo with minimal setup."""
    print("⚡ Quick Demo - A2A Client Graph")
    print("="*40)
    
    async def quick_test():
        try:
            demo = A2AClientDemo()
            await demo.initialize()
            
            # Test with one query
            query = "What are the latest developments in AI?"
            print(f"\n📝 Testing with: {query}")
            
            response = await demo.enhanced_agent.process_query(query)
            print(f"🤖 Response: {response}")
            
        except Exception as e:
            print(f"❌ Quick demo failed: {e}")
    
    asyncio.run(quick_test())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="A2A Client Graph Demo")
    parser.add_argument("--quick", action="store_true", help="Run quick demo")
    parser.add_argument("--agent-url", default="http://localhost:10000", help="A2A agent URL")
    
    args = parser.parse_args()
    
    if args.quick:
        run_quick_demo()
    else:
        asyncio.run(main())
