"""
CodeBot AI - Main FastAPI Application
Intelligent code analysis chatbot with RAG, static analysis, and git integration
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional
import asyncio

from config import settings
from models.schemas import (
    ChatRequest, ChatResponse, SearchRequest, 
    BugAnalysisRequest, RepositoryStatus
)
from engines.rag_engine import RAGEngine
from engines.static_analyzer import StaticAnalyzer
from engines.git_analyzer import GitAnalyzer
from parsers.query_parser import QueryParser
from parsers.exception_parser import ExceptionParser
from agents.orchestrator import AgentOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global engine instances
rag_engine = None
static_analyzer = None
git_analyzer = None
query_parser = None
exception_parser = None
orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    global rag_engine, static_analyzer, git_analyzer
    global query_parser, exception_parser, orchestrator
    
    logger.info("🚀 Starting CodeBot AI...")
    
    try:
        # Initialize engines
        logger.info("Initializing RAG Engine...")
        rag_engine = RAGEngine()
        await rag_engine.initialize()
        
        logger.info("Initializing Static Analyzer...")
        static_analyzer = StaticAnalyzer()
        await static_analyzer.initialize()
        
        logger.info("Initializing Git Analyzer...")
        git_analyzer = GitAnalyzer()
        await git_analyzer.initialize()
        
        # Initialize parsers
        query_parser = QueryParser()
        exception_parser = ExceptionParser()
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(
            rag_engine=rag_engine,
            static_analyzer=static_analyzer,
            git_analyzer=git_analyzer,
            query_parser=query_parser,
            exception_parser=exception_parser
        )
        
        logger.info("✅ All engines initialized successfully")
        
        yield
        
    finally:
        # Cleanup on shutdown
        logger.info("🛑 Shutting down CodeBot AI...")
        if rag_engine:
            await rag_engine.close()
        if static_analyzer:
            await static_analyzer.close()
        if git_analyzer:
            await git_analyzer.close()


# Create FastAPI app
app = FastAPI(
    title="CodeBot AI",
    description="Intelligent Code Analysis Chatbot",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CodeBot AI - Intelligent Code Analysis",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for load balancer
    """
    health_status = {
        "status": "healthy",
        "checks": {}
    }
    
    try:
        # Check RAG engine
        if rag_engine and await rag_engine.health_check():
            health_status["checks"]["rag_engine"] = "ok"
        else:
            health_status["checks"]["rag_engine"] = "unhealthy"
            health_status["status"] = "unhealthy"
        
        # Check Static Analyzer
        if static_analyzer and await static_analyzer.health_check():
            health_status["checks"]["static_analyzer"] = "ok"
        else:
            health_status["checks"]["static_analyzer"] = "unhealthy"
            health_status["status"] = "unhealthy"
        
        # Check Git Analyzer
        if git_analyzer and await git_analyzer.health_check():
            health_status["checks"]["git_analyzer"] = "ok"
        else:
            health_status["checks"]["git_analyzer"] = "unhealthy"
            health_status["status"] = "unhealthy"
        
        if health_status["status"] == "unhealthy":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health_status
            )
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - handles all user queries
    This is the primary interface users interact with
    """
    try:
        logger.info(f"Chat request: {request.message[:100]}...")
        
        # Use orchestrator to handle the query
        result = await orchestrator.process_query(
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint for real-time responses
    """
    async def generate():
        try:
            async for chunk in orchestrator.process_query_stream(
                message=request.message,
                conversation_id=request.conversation_id
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@app.post("/api/search")
async def search_code(request: SearchRequest):
    """
    Direct code search endpoint
    """
    try:
        results = await rag_engine.search(
            query=request.query,
            n_results=request.max_results or 10,
            filters=request.filters
        )
        
        return {
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/analyze/bug")
async def analyze_bug(request: BugAnalysisRequest):
    """
    Direct bug analysis endpoint
    """
    try:
        result = await orchestrator.analyze_bug(
            description=request.description,
            stack_trace=request.stack_trace,
            affected_files=request.affected_files
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Bug analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/analyze/dependencies/{function_name}")
async def get_dependencies(function_name: str):
    """
    Get dependencies for a specific function
    """
    try:
        callers = await static_analyzer.find_callers(function_name)
        callees = await static_analyzer.find_callees(function_name)
        
        return {
            "function": function_name,
            "callers": callers,
            "callees": callees
        }
        
    except Exception as e:
        logger.error(f"Dependency analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/repo/status", response_model=RepositoryStatus)
async def repository_status():
    """
    Get current repository status
    """
    try:
        status_info = await git_analyzer.get_repository_status()
        return RepositoryStatus(**status_info)
        
    except Exception as e:
        logger.error(f"Repository status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/repo/sync")
async def sync_repository():
    """
    Trigger repository sync and re-indexing
    """
    try:
        # Sync git repository
        await git_analyzer.sync_repository()
        
        # Re-index code
        asyncio.create_task(reindex_repository())
        
        return {
            "message": "Repository sync started",
            "status": "in_progress"
        }
        
    except Exception as e:
        logger.error(f"Repository sync error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/repo/index")
async def index_repository():
    """
    Trigger full repository indexing
    """
    try:
        asyncio.create_task(reindex_repository())
        
        return {
            "message": "Indexing started",
            "status": "in_progress"
        }
        
    except Exception as e:
        logger.error(f"Indexing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def reindex_repository():
    """
    Background task to reindex entire repository
    """
    try:
        logger.info("Starting repository indexing...")
        
        # 1. Chunk code files
        from engines.chunking import CodeChunker
        chunker = CodeChunker()
        
        all_chunks = await chunker.chunk_repository(settings.REPO_PATH)
        logger.info(f"Chunked {len(all_chunks)} code segments")
        
        # 2. Index in RAG engine
        await rag_engine.index_chunks(all_chunks)
        logger.info("RAG indexing complete")
        
        # 3. Build code graph
        await static_analyzer.build_graph(settings.REPO_PATH)
        logger.info("Code graph building complete")
        
        # 4. Sync git data
        await git_analyzer.sync_commits()
        logger.info("Git sync complete")
        
        logger.info("✅ Repository indexing completed successfully")
        
    except Exception as e:
        logger.error(f"Indexing failed: {str(e)}", exc_info=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
