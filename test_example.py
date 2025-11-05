#!/usr/bin/env python3
"""
Example script to test LangServe API endpoints
Demonstrates chat, RAG, and LangGraph workflows
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))
    print()

def test_chains():
    """List available chains"""
    print("=" * 60)
    print("Available Chains")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/chains")
    print(json.dumps(response.json(), indent=2))
    print()

def test_chat():
    """Test simple chat endpoint"""
    print("=" * 60)
    print("Testing Chat Endpoint")
    print("=" * 60)
    data = {
        "input": {"input": "What is LangChain in one sentence?"}
    }
    response = requests.post(f"{BASE_URL}/chat/invoke", json=data)
    result = response.json()
    print(f"Question: {data['input']['input']}")
    print(f"Answer: {result['output']}")
    print()

def test_graph():
    """Test LangGraph multi-step reasoning"""
    print("=" * 60)
    print("Testing LangGraph Endpoint")
    print("=" * 60)
    data = {
        "input": {"question": "What is machine learning?"}
    }
    response = requests.post(f"{BASE_URL}/graph/invoke", json=data)
    result = response.json()
    print(f"Question: {data['input']['question']}")
    print(f"\nAnalysis Phase:")
    print(result['output']['analysis'])
    print(f"\nAnswer Phase:")
    print(result['output']['answer'])
    print()

def test_rag():
    """Test RAG endpoint (requires documents in vector store)"""
    print("=" * 60)
    print("Testing RAG Endpoint")
    print("=" * 60)
    print("Note: RAG requires documents in the vector store.")
    print("Run the add_documents example first if you get empty results.")
    data = {
        "input": {"question": "What is vector search?"}
    }
    try:
        response = requests.post(f"{BASE_URL}/rag/invoke", json=data)
        result = response.json()
        print(f"Question: {data['input']['question']}")
        print(f"Answer: {result['output']}")
    except Exception as e:
        print(f"Error: {e}")
        print("This is normal if no documents have been added to the vector store yet.")
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LangServe API Test Suite")
    print("=" * 60 + "\n")

    try:
        test_health()
        test_chains()

        # Note: These tests require OPENAI_API_KEY to be set
        print("Note: The following tests require OPENAI_API_KEY in secrets/langchain.env")
        print()

        # Uncomment to run API tests (requires valid OpenAI key)
        # test_chat()
        # test_graph()
        # test_rag()

    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to LangServe.")
        print("Make sure the service is running: docker ps | grep langserve")
    except Exception as e:
        print(f"❌ Error: {e}")
