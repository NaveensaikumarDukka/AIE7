#!/usr/bin/env python3
"""CLI interface for the A2A client graph.

This provides an interactive command-line interface to communicate with
the A2A agent server through the LangGraph client.
"""

import asyncio
import logging
import os
import sys
from typing import Optional

import click
from dotenv import load_dotenv

from app.enhanced_a2a_client_graph import EnhancedA2AClientAgent
from app.a2a_client_graph import A2AClientAgent

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


def print_help():
    """Print help information."""
    print("\n📖 Available Commands:")
    print("  help     - Show this help message")
    print("  quit     - Exit the application")
    print("  exit     - Exit the application")
    print("  q        - Quick exit")
    print("\n💡 Tips:")
    print("  - Ask questions naturally")
    print("  - The agent can search the web, find academic papers, and more")
    print("  - Use Ctrl+C to interrupt long operations")


async def run_interactive_session(agent, query: Optional[str] = None):
    """Run an interactive session with the agent."""
    if query:
        # Single query mode
        response = await agent.process_query(query)
        print(f"\nQuery: {query}")
        print(f"Response: {response}")
        return
    
    # Interactive mode
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            if not user_input:
                continue
            
            print("🤔 Thinking...")
            response = await agent.process_query(user_input)
            print(f"🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def run_test_session(agent, test_queries):
    """Run a test session with predefined queries."""
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}/{len(test_queries)}")
        print(f"Query: {query}")
        print("-" * 50)
        
        try:
            response = await agent.process_query(query)
            print(f"Response: {response}")
            print("-" * 50)
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
            print("-" * 50)


@click.group()
def cli():
    """A2A Client CLI - Interact with A2A protocol agents."""
    pass


@cli.command()
@click.option('--agent-url', default='http://localhost:10000', help='URL of the A2A agent server')
@click.option('--enhanced', is_flag=True, help='Use enhanced client with LLM processing')
@click.option('--query', help='Single query to send (optional)')
def chat(agent_url: str, enhanced: bool, query: Optional[str]):
    """Start an interactive chat session with an A2A agent."""
    async def main():
        try:
            if not os.getenv('OPENAI_API_KEY'):
                raise MissingAPIKeyError(
                    'OPENAI_API_KEY environment variable not set.'
                )

            if enhanced:
                agent = EnhancedA2AClientAgent(agent_url)
                print("🤖 Enhanced A2A Client Agent (with LLM processing)")
            else:
                agent = A2AClientAgent(agent_url)
                print("🤖 Simple A2A Client Agent")
            
            print(f"🔗 Connecting to agent at: {agent_url}")
            print("=" * 60)
            
            # Initialize the agent
            await agent.initialize()
            print("✅ Connected successfully!")
            print("\nType 'quit' or 'exit' to end the session.")
            print("Type 'help' for available commands.")
            print("-" * 60)
            
            # Run the session
            await run_interactive_session(agent, query)
                
        except MissingAPIKeyError as e:
            logger.error(f'Error: {e}')
            sys.exit(1)
        except Exception as e:
            logger.error(f'An error occurred: {e}')
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    asyncio.run(main())


@cli.command()
@click.option('--agent-url', default='http://localhost:10000', help='URL of the A2A agent server')
@click.option('--enhanced', is_flag=True, help='Use enhanced client with LLM processing')
def test(agent_url: str, enhanced: bool):
    """Run a series of test queries against the A2A agent."""
    async def main():
        try:
            if not os.getenv('OPENAI_API_KEY'):
                raise MissingAPIKeyError(
                    'OPENAI_API_KEY environment variable not set.'
                )

            if enhanced:
                agent = EnhancedA2AClientAgent(agent_url)
                print("🧪 Testing Enhanced A2A Client Agent")
            else:
                agent = A2AClientAgent(agent_url)
                print("🧪 Testing Simple A2A Client Agent")
            
            print(f"🔗 Testing agent at: {agent_url}")
            print("=" * 60)
            
            # Initialize the agent
            await agent.initialize()
            
            # Test queries
            test_queries = [
                "What are the latest developments in artificial intelligence?",
                "Search for recent papers on large language models",
                "What do you know about machine learning?",
                "Can you help me understand neural networks?",
                "What are the current trends in AI research?"
            ]
            
            await run_test_session(agent, test_queries)
            
        except MissingAPIKeyError as e:
            logger.error(f'Error: {e}')
            sys.exit(1)
        except Exception as e:
            logger.error(f'An error occurred: {e}')
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    asyncio.run(main())


@cli.command()
@click.option('--agent-url', default='http://localhost:10000', help='URL of the A2A agent server')
def info(agent_url: str):
    """Get information about the A2A agent."""
    async def get_info():
        try:
            from a2a.client import A2ACardResolver
            import httpx
            
            print(f"🔍 Getting agent information from: {agent_url}")
            print("=" * 60)
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as httpx_client:
                resolver = A2ACardResolver(
                    httpx_client=httpx_client,
                    base_url=agent_url,
                )
                
                agent_card = await resolver.get_agent_card()
                
                print(f"🤖 Agent Name: {agent_card.name}")
                print(f"📝 Description: {agent_card.description}")
                print(f"🌐 URL: {agent_card.url}")
                print(f"📦 Version: {agent_card.version}")
                print(f"🔧 Capabilities: {agent_card.capabilities}")
                print(f"🛠️  Skills ({len(agent_card.skills)}):")
                
                for skill in agent_card.skills:
                    print(f"  • {skill.name}: {skill.description}")
                    print(f"    Tags: {', '.join(skill.tags)}")
                    print(f"    Examples: {', '.join(skill.examples)}")
                    print()
                
        except Exception as e:
            print(f"❌ Error getting agent information: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(get_info())


if __name__ == '__main__':
    cli()
