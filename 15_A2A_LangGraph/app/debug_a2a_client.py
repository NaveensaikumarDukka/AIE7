#!/usr/bin/env python3
"""Debug script to test A2A client step by step."""

import asyncio
import logging
import os
from dotenv import load_dotenv

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import SendMessageRequest, MessageSendParams
from uuid import uuid4

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def debug_a2a_client():
    """Debug the A2A client step by step."""
    print("🔍 Debugging A2A Client")
    print("="*50)
    
    base_url = 'http://localhost:10000'
    
    try:
        # Step 1: Create httpx client
        print("1. Creating httpx client...")
        httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
        
        # Step 2: Initialize A2ACardResolver
        print("2. Initializing A2ACardResolver...")
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )
        
        # Step 3: Fetch agent card
        print("3. Fetching agent card...")
        agent_card = await resolver.get_agent_card()
        print(f"   Agent name: {agent_card.name}")
        print(f"   Agent description: {agent_card.description}")
        
        # Step 4: Initialize A2AClient
        print("4. Initializing A2AClient...")
        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=agent_card
        )
        print("   A2AClient initialized successfully")
        
        # Step 5: Create message payload
        print("5. Creating message payload...")
        send_message_payload = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': 'What is machine learning?'}
                ],
                'message_id': uuid4().hex,
            },
        }
        print(f"   Message payload: {send_message_payload}")
        
        # Step 6: Create request
        print("6. Creating SendMessageRequest...")
        request = SendMessageRequest(
            id=str(uuid4()), 
            params=MessageSendParams(**send_message_payload)
        )
        print(f"   Request ID: {request.id}")
        
        # Step 7: Send message
        print("7. Sending message...")
        response = await client.send_message(request)
        print(f"   Response received: {type(response)}")
        
        # Step 8: Inspect response structure
        print("8. Inspecting response structure...")
        print(f"   Response has root: {hasattr(response, 'root')}")
        if hasattr(response, 'root'):
            print(f"   Root type: {type(response.root)}")
            print(f"   Root has result: {hasattr(response.root, 'result')}")
            if hasattr(response.root, 'result'):
                print(f"   Result type: {type(response.root.result)}")
                print(f"   Result has artifacts: {hasattr(response.root.result, 'artifacts')}")
                if hasattr(response.root.result, 'artifacts'):
                    print(f"   Artifacts: {response.root.result.artifacts}")
                    if response.root.result.artifacts:
                        for i, artifact in enumerate(response.root.result.artifacts):
                            print(f"   Artifact {i}: {artifact}")
                            if hasattr(artifact, 'parts'):
                                print(f"   Artifact {i} has parts: {artifact.parts}")
                                for j, part in enumerate(artifact.parts):
                                    print(f"   Part {j}: {part}")
                                    if hasattr(part, 'text'):
                                        print(f"   Part {j} text: {part.text}")
        
        # Step 9: Extract response text (old way)
        print("9. Extracting response text (old way)...")
        response_parts_old = []
        if hasattr(response, 'root') and hasattr(response.root, 'result') and hasattr(response.root.result, 'artifacts'):
            if response.root.result.artifacts:
                for artifact in response.root.result.artifacts:
                    if hasattr(artifact, 'parts'):
                        for part in artifact.parts:
                            if hasattr(part, 'text'):
                                response_parts_old.append(part.text)
        
        full_response_old = "\n".join(response_parts_old) if response_parts_old else "No response received"
        print(f"   Full response (old way): {full_response_old}")
        
        # Step 9b: Extract response text (new way)
        print("9b. Extracting response text (new way)...")
        response_parts_new = []
        if hasattr(response, 'root') and hasattr(response.root, 'result') and hasattr(response.root.result, 'artifacts'):
            if response.root.result.artifacts:
                for artifact in response.root.result.artifacts:
                    if hasattr(artifact, 'parts'):
                        for part in artifact.parts:
                            if hasattr(part, 'root') and hasattr(part.root, 'text'):
                                response_parts_new.append(part.root.text)
        
        full_response_new = "\n".join(response_parts_new) if response_parts_new else "No response received"
        print(f"   Full response (new way): {full_response_new}")
        
        # Step 10: Close httpx client
        print("10. Closing httpx client...")
        await httpx_client.aclose()
        
        print("\n✅ Debug completed successfully!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_a2a_client())
