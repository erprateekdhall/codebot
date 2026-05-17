"""
Pydantic models for request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QueryIntent(str, Enum):
    """Query intent types"""
    BUG_ANALYSIS = "bug_analysis"
    CODE_SEARCH = "code_search"
    AUTHOR_LOOKUP = "author_lookup"
    CODE_EXPLANATION = "code_explanation"
    DEPENDENCY_CHECK = "dependency_check"
    GENERAL_QUESTION = "general_question"


# ===== Chat Endpoints =====

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Why is authentication failing for mobile users?",
                "conversation_id": "conv_123"
            }
        }


class CodeSnippet(BaseModel):
    """Code snippet in response"""
    file: str
    function: Optional[str] = None
    start_line: int
    end_line: int
    code: str
    relevance_score: Optional[float] = None


class GitInfo(BaseModel):
    """Git commit information"""
    author: str
    email: str
    date: datetime
    message: str
    sha: str
    lines_added: Optional[int] = None
    lines_deleted: Optional[int] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    sources: List[CodeSnippet] = []
    git_info: List[GitInfo] = []
    intent: Optional[QueryIntent] = None
    confidence: str = "medium"
    conversation_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "The authentication is failing because...",
                "sources": [],
                "git_info": [],
                "intent": "bug_analysis",
                "confidence": "high",
                "conversation_id": "conv_123"
            }
        }


# ===== Search Endpoints =====

class SearchRequest(BaseModel):
    """Code search request"""
    query: str = Field(..., min_length=1)
    max_results: Optional[int] = 10
    file_types: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """Single search result"""
    file_path: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    code: str
    start_line: int
    end_line: int
    score: float


# ===== Bug Analysis =====

class BugAnalysisRequest(BaseModel):
    """Bug analysis request"""
    description: str
    stack_trace: Optional[str] = None
    affected_files: Optional[List[str]] = None
    error_message: Optional[str] = None


class BugAnalysisResponse(BaseModel):
    """Bug analysis response"""
    root_cause: str
    affected_code: List[CodeSnippet]
    suggested_fix: str
    impact_analysis: str
    git_blame: List[GitInfo]
    confidence: str


# ===== Repository Management =====

class RepositoryStatus(BaseModel):
    """Repository status"""
    total_files: int
    indexed_files: int
    last_sync: Optional[datetime] = None
    current_branch: str
    latest_commit: str
    total_commits: int
    is_syncing: bool = False


class IndexingStatus(BaseModel):
    """Indexing progress"""
    status: str  # "in_progress", "completed", "failed"
    progress: float  # 0.0 to 1.0
    files_processed: int
    total_files: int
    current_file: Optional[str] = None
    errors: List[str] = []


# ===== Internal Models =====

class ParsedQuery(BaseModel):
    """Parsed query information"""
    intent: QueryIntent
    entities: Dict[str, List[str]]
    keywords: List[str]
    original_message: str
    confidence: float = 0.5


class ExceptionData(BaseModel):
    """Parsed exception information"""
    has_exception: bool = False
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    stack_trace: List[Dict[str, Any]] = []
    files_involved: List[str] = []
    functions_involved: List[str] = []
    line_numbers: Dict[str, int] = {}
    time_context: List[str] = []
    affected_users: List[str] = []


class CodeChunk(BaseModel):
    """Code chunk for indexing"""
    chunk_id: str
    type: str  # "function", "class", "module"
    name: str
    code: str
    filepath: str
    start_line: int
    end_line: int
    language: str
    methods: List[str] = []
    imports: List[str] = []


class GraphNode(BaseModel):
    """Neo4j graph node"""
    node_type: str  # "File", "Class", "Function"
    name: str
    properties: Dict[str, Any]


class GraphRelationship(BaseModel):
    """Neo4j graph relationship"""
    type: str  # "CONTAINS", "CALLS", "INHERITS", "USES"
    from_node: str
    to_node: str
    properties: Dict[str, Any] = {}
