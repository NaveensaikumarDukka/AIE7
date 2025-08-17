#!/usr/bin/env python3
"""Test script for the A2A Client Graph.

This script tests the A2A client graph functionality to ensure it works
correctly with the A2A agent server.
"""

import asyncio
import logging
import os
import sys
import time
from typing import List, Dict, Any

import httpx
from dotenv import load_dotenv

from app.enhanced_a2a_client_graph import EnhancedA2AClientAgent
from app.a2a_client_graph import A2AClientAgent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestResults:
    """Container for test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.responses = {}
    
    def add_success(self, test_name: str, response: str):
        """Add a successful test result."""
        self.passed += 1
        self.responses[test_name] = response
        print(f"✅ {test_name}: PASSED")
    
    def add_failure(self, test_name: str, error: str):
        """Add a failed test result."""
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: FAILED - {error}")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {self.passed/(self.passed+self.failed)*100:.1f}%")
        
        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")


class A2AClientTester:
    """Test class for A2A client functionality."""
    
    def __init__(self, agent_url: str = "http://localhost:10000"):
        self.agent_url = agent_url
        self.simple_agent = A2AClientAgent(agent_url)
        self.enhanced_agent = EnhancedA2AClientAgent(agent_url)
        self.results = TestResults()
    
    async def test_initialization(self):
        """Test agent initialization."""
        test_name = "Agent Initialization"
        
        try:
            await self.simple_agent.initialize()
            await self.enhanced_agent.initialize()
            self.results.add_success(test_name, "Both agents initialized successfully")
        except Exception as e:
            self.results.add_failure(test_name, str(e))
    
    async def test_simple_client_basic_query(self):
        """Test basic query with simple client."""
        test_name = "Simple Client - Basic Query"
        
        try:
            query = "What is artificial intelligence?"
            response = await self.simple_agent.process_query(query)
            
            if response and len(response) > 10:
                self.results.add_success(test_name, f"Response length: {len(response)} chars")
            else:
                self.results.add_failure(test_name, "Response too short or empty")
                
        except Exception as e:
            self.results.add_failure(test_name, str(e))
    
    async def test_enhanced_client_basic_query(self):
        """Test basic query with enhanced client."""
        test_name = "Enhanced Client - Basic Query"
        
        try:
            query = "What is artificial intelligence?"
            response = await self.enhanced_agent.process_query(query)
            
            if response and len(response) > 10:
                self.results.add_success(test_name, f"Response length: {len(response)} chars")
            else:
                self.results.add_failure(test_name, "Response too short or empty")
                
        except Exception as e:
            self.results.add_failure(test_name, str(e))
    
    async def test_web_search_query(self):
        """Test web search functionality."""
        test_name = "Web Search Query"
        
        try:
            query = "What are the latest developments in AI?"
            response = await self.enhanced_agent.process_query(query)
            
            if response and len(response) > 20:
                self.results.add_success(test_name, f"Web search response: {len(response)} chars")
            else:
                self.results.add_failure(test_name, "Web search response too short")
                
        except Exception as e:
            self.results.add_failure(test_name, str(e))
    
    async def test_academic_search_query(self):
        """Test academic paper search."""
        test_name = "Academic Paper Search"
        
        try:
            query = "Find recent papers on large language models"
            response = await self.enhanced_agent.process_query(query)
            
            if response and len(response) > 20:
                self.results.add_success(test_name, f"Academic search response: {len(response)} chars")
            else:
                self.results.add_failure(test_name, "Academic search response too short")
                
        except Exception as e:
            self.results.add_failure(test_name, str(e))
    
    async def test_error_handling(self):
        """Test error handling with invalid queries."""
        test_name = "Error Handling"
        
        try:
            # Test with empty query
            response = await self.enhanced_agent.process_query("")
            
            if "error" in response.lower() or "no response" in response.lower():
                self.results.add_success(test_name, "Properly handled empty query")
            else:
                self.results.add_failure(test_name, "Did not handle empty query properly")
                
        except Exception as e:
            self.results.add_failure(test_name, str(e))
    
    async def test_response_comparison(self):
        """Test that enhanced client provides better responses."""
        test_name = "Response Enhancement"
        
        try:
            query = "What is machine learning?"
            
            # Get simple response
            simple_response = await self.simple_agent.process_query(query)
            
            # Get enhanced response
            enhanced_response = await self.enhanced_agent.process_query(query)
            
            # Enhanced response should be different (and potentially longer)
            if enhanced_response != simple_response:
                self.results.add_success(test_name, "Enhanced response differs from simple response")
            else:
                self.results.add_failure(test_name, "Enhanced response identical to simple response")
                
        except Exception as e:
            self.results.add_failure(test_name, str(e))
    
    async def test_concurrent_queries(self):
        """Test handling multiple concurrent queries."""
        test_name = "Concurrent Queries"
        
        try:
            queries = [
                "What is AI?",
                "What is machine learning?",
                "What is deep learning?"
            ]
            
            # Run queries concurrently
            tasks = [
                self.enhanced_agent.process_query(query)
                for query in queries
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that all queries succeeded
            successful_responses = [r for r in responses if isinstance(r, str) and len(r) > 10]
            
            if len(successful_responses) == len(queries):
                self.results.add_success(test_name, f"All {len(queries)} concurrent queries succeeded")
            else:
                self.results.add_failure(test_name, f"Only {len(successful_responses)}/{len(queries)} queries succeeded")
                
        except Exception as e:
            self.results.add_failure(test_name, str(e))
    
    async def test_connection_stability(self):
        """Test connection stability over multiple requests."""
        test_name = "Connection Stability"
        
        try:
            # Make multiple requests to test stability
            for i in range(3):
                query = f"Test query {i+1}: What is AI?"
                response = await self.enhanced_agent.process_query(query)
                
                if not response or len(response) < 10:
                    self.results.add_failure(test_name, f"Unstable response on iteration {i+1}")
                    return
            
            self.results.add_success(test_name, "Stable responses across 3 iterations")
                
        except Exception as e:
            self.results.add_failure(test_name, str(e))
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 A2A Client Graph Test Suite")
        print("="*60)
        
        # Test initialization first
        await self.test_initialization()
        
        if self.results.failed > 0:
            print("❌ Initialization failed, skipping other tests")
            return
        
        # Run all other tests
        tests = [
            self.test_simple_client_basic_query,
            self.test_enhanced_client_basic_query,
            self.test_web_search_query,
            self.test_academic_search_query,
            self.test_error_handling,
            self.test_response_comparison,
            self.test_concurrent_queries,
            self.test_connection_stability,
        ]
        
        for test in tests:
            await test()
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Print summary
        self.results.print_summary()


async def main():
    """Main test function."""
    print("🎯 A2A Client Graph Test Suite")
    print("="*60)
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set. Please run 'python setup.py' first.")
        sys.exit(1)
    
    # Create tester
    tester = A2AClientTester()
    
    try:
        await tester.run_all_tests()
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_quick_test():
    """Run a quick test with minimal setup."""
    print("⚡ Quick Test - A2A Client Graph")
    print("="*40)
    
    async def quick_test():
        try:
            tester = A2AClientTester()
            
            # Test initialization
            await tester.test_initialization()
            
            if tester.results.failed > 0:
                print("❌ Quick test failed during initialization")
                return
            
            # Test one basic query
            await tester.test_enhanced_client_basic_query()
            
            tester.results.print_summary()
            
        except Exception as e:
            print(f"❌ Quick test failed: {e}")
    
    asyncio.run(quick_test())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="A2A Client Graph Test Suite")
    parser.add_argument("--quick", action="store_true", help="Run quick test")
    parser.add_argument("--agent-url", default="http://localhost:10000", help="A2A agent URL")
    
    args = parser.parse_args()
    
    if args.quick:
        run_quick_test()
    else:
        asyncio.run(main())
