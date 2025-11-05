#!/usr/bin/env python
"""
LangServe Server with LangSmith and LangGraph Integration
Provides REST API endpoints for LangChain applications
"""
import os
from typing import List, Optional
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, END
from langsmith import Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LangServe API",
    version="1.0.0",
    description="LangChain Server with LangSmith tracing and LangGraph workflows",
)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "langchain-project")

# Qdrant Vector Database Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "langchain_docs")

# Enable LangSmith tracing if API key is provided
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    logger.info(f"LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")
else:
    logger.warning("LANGSMITH_API_KEY not set - tracing disabled")

# Initialize embeddings and vector store
try:
    embeddings = OpenAIEmbeddings() if OPENAI_API_KEY else None

    if embeddings:
        # Initialize Qdrant client
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

        # Initialize vector store
        vectorstore = QdrantVectorStore(
            client=qdrant_client,
            collection_name=QDRANT_COLLECTION,
            embedding=embeddings,
        )
        logger.info(f"Qdrant vector store initialized successfully (collection: {QDRANT_COLLECTION})")
    else:
        vectorstore = None
        logger.warning("OpenAI API key not set - vector store disabled")
except Exception as e:
    logger.error(f"Failed to initialize vector store: {e}")
    vectorstore = None

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
) if OPENAI_API_KEY else None

# Simple chat chain
if llm:
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant."),
        ("human", "{input}")
    ])

    chat_chain = chat_prompt | llm | StrOutputParser()

    # Add chat route with explicit input/output types
    try:
        add_routes(
            app,
            chat_chain.with_types(input_type=dict, output_type=str),
            path="/chat",
            enabled_endpoints=["invoke", "stream"],
        )
        logger.info("Chat chain added at /chat")
    except Exception as e:
        logger.error(f"Failed to add chat route: {e}")

# RAG chain with vector store
if llm and vectorstore:
    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use the following context to answer the question:\n\n{context}"),
        ("human", "{question}")
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {
            "context": lambda x: format_docs(vectorstore.similarity_search(x["question"], k=3)),
            "question": lambda x: x["question"]
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    try:
        add_routes(
            app,
            rag_chain.with_types(input_type=dict, output_type=str),
            path="/rag",
            enabled_endpoints=["invoke", "stream"],
        )
        logger.info("RAG chain added at /rag")
    except Exception as e:
        logger.error(f"Failed to add RAG route: {e}")

# LangGraph example: Multi-step reasoning workflow
if llm:
    from typing_extensions import TypedDict

    class GraphState(TypedDict):
        question: str
        analysis: str
        answer: str

    def analyze_question(state: GraphState) -> GraphState:
        """Analyze the question"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze this question and identify key concepts to address."),
            ("human", "{question}")
        ])
        chain = prompt | llm | StrOutputParser()
        state["analysis"] = chain.invoke({"question": state["question"]})
        return state

    def generate_answer(state: GraphState) -> GraphState:
        """Generate final answer"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Based on this analysis, provide a comprehensive answer:\n{analysis}"),
            ("human", "{question}")
        ])
        chain = prompt | llm | StrOutputParser()
        state["answer"] = chain.invoke({
            "question": state["question"],
            "analysis": state["analysis"]
        })
        return state

    # Build LangGraph workflow
    workflow = StateGraph(GraphState)
    workflow.add_node("analyze", analyze_question)
    workflow.add_node("answer", generate_answer)
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "answer")
    workflow.add_edge("answer", END)

    graph_chain = workflow.compile()

    try:
        add_routes(
            app,
            graph_chain,
            path="/graph",
            enabled_endpoints=["invoke"],
        )
        logger.info("LangGraph workflow added at /graph")
    except Exception as e:
        logger.error(f"Failed to add graph route: {e}")

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "services": {
            "langserve": True,
            "langsmith": bool(LANGSMITH_API_KEY),
            "openai": bool(OPENAI_API_KEY),
            "vectorstore": vectorstore is not None,
            "qdrant": QDRANT_HOST != "",
        }
    }
    return status

# Redirect root to docs
@app.get("/")
async def redirect_root_to_docs():
    """Redirect to API documentation"""
    return RedirectResponse("/docs")

# List available chains
@app.get("/chains")
async def list_chains():
    """List all available chain endpoints"""
    chains = []
    if llm:
        chains.append({
            "name": "chat",
            "path": "/chat",
            "description": "Simple chat with AI assistant"
        })
    if llm and vectorstore:
        chains.append({
            "name": "rag",
            "path": "/rag",
            "description": "Retrieval Augmented Generation with vector search"
        })
    if llm:
        chains.append({
            "name": "graph",
            "path": "/graph",
            "description": "Multi-step reasoning with LangGraph"
        })
    return {"chains": chains}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
