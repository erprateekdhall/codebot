# CodeBot AI - Data Flow Design

## Overview
This document describes how data flows through the CodeBot AI system from user query to final response.

---

## High-Level Data Flow

```mermaid
graph TB
    User[👤 User] --> Frontend[🌐 React Frontend<br/>Port 3000]
    Frontend --> API[⚡ FastAPI Backend<br/>Port 8000]
    
    API --> Parser[🧠 Query Parser]
    Parser --> Orchestrator[🎯 Agent Orchestrator]
    
    Orchestrator --> RAG[📚 RAG Engine]
    Orchestrator --> Static[🔍 Static Analyzer]
    Orchestrator --> Git[📜 Git Analyzer]
    
    RAG --> ChromaDB[(🗄️ ChromaDB<br/>Vector Store)]
    Static --> Neo4j[(🕸️ Neo4j<br/>Graph DB)]
    Git --> PostgreSQL[(🐘 PostgreSQL<br/>Commit History)]
    
    Orchestrator --> Context[📝 Context Builder]
    Context --> Claude[🤖 Claude API<br/>Sonnet 4.6]
    Claude --> Response[📤 Response]
    
    Response --> Cache[(💾 Redis Cache)]
    Response --> Frontend
    Frontend --> User
    
    style User fill:#e1f5ff
    style Frontend fill:#fff3cd
    style API fill:#d1ecf1
    style Orchestrator fill:#f8d7da
    style Claude fill:#d4edda
    style Response fill:#d1ecf1
```

---

## Detailed Data Flow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as FastAPI
    participant QP as Query Parser
    participant EP as Exception Parser
    participant AO as Orchestrator
    participant RAG as RAG Engine
    participant SA as Static Analyzer
    participant GA as Git Analyzer
    participant CB as Context Builder
    participant Claude as Claude API
    participant Cache as Redis Cache
    
    U->>FE: Types query: "Why are API tokens used?"
    FE->>API: POST /api/chat {message, conversation_id}
    
    API->>QP: Parse query
    QP->>QP: Extract entities (files, functions, errors)
    QP->>QP: Detect intent (CODE_EXPLANATION)
    QP->>QP: Extract keywords
    QP->>QP: Calculate confidence
    QP-->>API: ParsedQuery{intent, entities, keywords, confidence}
    
    API->>EP: Check for exceptions
    EP->>EP: Parse stack traces
    EP-->>API: ExceptionData{has_exception: false}
    
    API->>AO: Route query based on intent
    
    alt Intent: CODE_EXPLANATION
        AO->>RAG: Search for relevant code (top 7)
        RAG->>Cache: Check cache
        alt Cache Miss
            RAG->>RAG: Generate query embedding
            RAG->>RAG: Vector similarity search
            RAG-->>Cache: Store results
        end
        RAG-->>AO: CodeChunks[7]
        
        AO->>SA: Get dependencies for entities
        SA->>SA: Find callers/callees
        SA-->>AO: DependencyGraph
        
        AO->>CB: Build explanation context
        CB->>CB: Format code chunks
        CB->>CB: Add dependency info
        CB->>CB: Apply explanation prompt template
        CB-->>AO: EnrichedContext
        
        AO->>Claude: Generate explanation
        Note over Claude: Prompt: "Explain in plain English,<br/>use analogies, avoid jargon..."
        Claude-->>AO: PlainEnglishResponse
        
        AO->>AO: Format response
        AO-->>API: {response, sources, intent, confidence}
        
    else Intent: BUG_ANALYSIS
        AO->>RAG: Search code (top 7)
        AO->>GA: Get recent commits (10)
        AO->>SA: Get dependencies
        AO->>CB: Build bug context
        AO->>Claude: Analyze bug
        AO-->>API: {response, sources, git_info}
        
    else Intent: AUTHOR_LOOKUP
        AO->>RAG: Find files (top 5)
        AO->>GA: Get file history
        AO->>GA: Get git blame
        AO->>CB: Build author context
        AO->>Claude: Lookup authors
        AO-->>API: {response, git_info}
    end
    
    API-->>FE: JSON Response
    FE->>FE: Parse and render
    FE-->>U: Display formatted answer
```

---

## Query Processing Pipeline

```mermaid
flowchart TD
    Start([User Query]) --> Parse[Parse Query]
    
    Parse --> Extract[Extract Entities:<br/>- Files<br/>- Functions<br/>- Classes<br/>- Errors]
    
    Extract --> Intent{Detect Intent}
    
    Intent -->|Bug/Error| BugFlow[Bug Analysis Flow]
    Intent -->|Search| SearchFlow[Code Search Flow]
    Intent -->|Author| AuthorFlow[Author Lookup Flow]
    Intent -->|Explain| ExplainFlow[Explanation Flow]
    Intent -->|Dependency| DepFlow[Dependency Flow]
    Intent -->|General| GeneralFlow[General Q&A Flow]
    
    BugFlow --> RAG1[RAG: Top 7 chunks]
    BugFlow --> Git1[Git: Recent 10 commits]
    BugFlow --> SA1[Static: Dependencies]
    RAG1 --> Context1[Build Context]
    Git1 --> Context1
    SA1 --> Context1
    
    SearchFlow --> RAG2[RAG: Top 10 chunks]
    RAG2 --> Context2[Build Context]
    
    AuthorFlow --> RAG3[RAG: Find files]
    RAG3 --> Git2[Git: File history + blame]
    Git2 --> Context3[Build Context]
    
    ExplainFlow --> RAG4[RAG: Top 7 chunks]
    ExplainFlow --> SA2[Static: Dependencies]
    RAG4 --> Context4[Build Context]
    SA2 --> Context4
    
    DepFlow --> SA3[Static: Call graph]
    DepFlow --> RAG5[RAG: Top 5 chunks]
    SA3 --> Context5[Build Context]
    RAG5 --> Context5
    
    GeneralFlow --> RAG6[RAG: Top 3 chunks]
    RAG6 --> Context6[Build Context]
    
    Context1 --> Claude1[Claude API]
    Context2 --> Claude2[Claude API]
    Context3 --> Claude3[Claude API]
    Context4 --> Claude4[Claude API]
    Context5 --> Claude5[Claude API]
    Context6 --> Claude6[Claude API]
    
    Claude1 --> Format[Format Response]
    Claude2 --> Format
    Claude3 --> Format
    Claude4 --> Format
    Claude5 --> Format
    Claude6 --> Format
    
    Format --> Response([Return to User])
    
    style Start fill:#e1f5ff
    style Intent fill:#fff3cd
    style Format fill:#d4edda
    style Response fill:#d1ecf1
```

---

## Data Storage & Retrieval

```mermaid
flowchart LR
    subgraph Indexing["📥 Repository Indexing (One-Time)"]
        Repo[Git Repository] --> Chunker[Code Chunker]
        Chunker --> AST[AST Parser<br/>Python specific]
        Chunker --> Generic[Line-based<br/>Other languages]
        
        AST --> Chunks1[Code Chunks<br/>Classes, Functions]
        Generic --> Chunks2[Code Chunks<br/>Line segments]
        
        Chunks1 --> Embed[Embedding Generator<br/>Sentence Transformers]
        Chunks2 --> Embed
        
        Embed --> VectorStore[(ChromaDB<br/>Vector Embeddings)]
        
        Repo --> GitParser[Git Parser]
        GitParser --> CommitDB[(PostgreSQL<br/>Commit History)]
        
        Repo --> StaticParser[Static Analyzer]
        StaticParser --> GraphDB[(Neo4j<br/>Code Relationships)]
    end
    
    subgraph Retrieval["🔍 Query-Time Retrieval"]
        Query[User Query] --> QEmbed[Query Embedding]
        QEmbed --> Search[Vector Similarity<br/>Search]
        Search --> VectorStore
        VectorStore --> Results[Top K Results]
        
        Query --> EntityExtract[Entity Extraction]
        EntityExtract --> GraphQuery[Graph Query]
        GraphQuery --> GraphDB
        GraphDB --> Dependencies[Dependencies]
        
        Query --> FileExtract[File Extraction]
        FileExtract --> HistQuery[History Query]
        HistQuery --> CommitDB
        CommitDB --> History[Git History]
        
        Results --> Combine[Combine Context]
        Dependencies --> Combine
        History --> Combine
        
        Combine --> EnrichedContext[Enriched Context]
    end
    
    style VectorStore fill:#d4edda
    style CommitDB fill:#cfe2ff
    style GraphDB fill:#f8d7da
```

---

## Data Flow by Intent Type

### 1. Bug Analysis Intent

```mermaid
graph LR
    Query[Bug Query] --> RAG[RAG Search<br/>n=7]
    Query --> Git[Recent Commits<br/>n=10]
    Query --> Static[Dependencies]
    
    RAG --> Code[Relevant Code]
    Git --> Changes[Recent Changes]
    Static --> Deps[Call Graph]
    
    Code --> Context[Context Builder]
    Changes --> Context
    Deps --> Context
    
    Context --> Prompt[Bug Analysis Prompt:<br/>1. Root cause<br/>2. Why it's happening<br/>3. Fix with code<br/>4. Prevention]
    
    Prompt --> Claude[Claude API]
    Claude --> Answer[Diagnostic Answer]
```

### 2. Code Explanation Intent

```mermaid
graph LR
    Query[Explanation Query] --> RAG[RAG Search<br/>n=7]
    Query --> Static[Dependencies]
    
    RAG --> Code[Code Context]
    Static --> Deps[Related Functions]
    
    Code --> Context[Context Builder]
    Deps --> Context
    
    Context --> Prompt[Explanation Prompt:<br/>- Plain English<br/>- Use analogies<br/>- No jargon<br/>- Conversational<br/>- No code snippets]
    
    Prompt --> Claude[Claude API]
    Claude --> Answer[Plain English<br/>Explanation]
```

### 3. Author Lookup Intent

```mermaid
graph LR
    Query[Who wrote X?] --> RAG[RAG Search<br/>Find files]
    
    RAG --> Files[Relevant Files]
    
    Files --> Git[Git History +<br/>Blame Info]
    
    Git --> Authors[Author Info:<br/>- Name<br/>- Email<br/>- Date<br/>- Commits]
    
    Authors --> Context[Context Builder]
    
    Context --> Prompt[Author Prompt]
    
    Prompt --> Claude[Claude API]
    Claude --> Answer[Author Attribution]
```

---

## Caching Strategy

```mermaid
flowchart TD
    Query[Query Received] --> CacheCheck{Check Redis<br/>Cache}
    
    CacheCheck -->|Hit| Cached[Return Cached<br/>Response]
    CacheCheck -->|Miss| Process[Process Query]
    
    Process --> Embedding{Embedding<br/>Cached?}
    
    Embedding -->|Yes| UseCache[Use Cached<br/>Embedding]
    Embedding -->|No| Generate[Generate<br/>Embedding]
    
    Generate --> StoreEmbed[Store in Cache<br/>TTL: 1 hour]
    
    UseCache --> Search[Vector Search]
    StoreEmbed --> Search
    
    Search --> Results{Results<br/>Cached?}
    
    Results -->|Yes| UseCachedResults[Use Cached<br/>Results]
    Results -->|No| Retrieve[Retrieve from<br/>ChromaDB]
    
    Retrieve --> StoreResults[Store in Cache<br/>TTL: 1 hour]
    
    UseCachedResults --> Claude[Call Claude API]
    StoreResults --> Claude
    
    Claude --> StoreResponse[Store Response<br/>in Cache<br/>TTL: 1 hour]
    
    StoreResponse --> Return[Return to User]
    Cached --> Return
    
    style CacheCheck fill:#fff3cd
    style Cached fill:#d4edda
    style StoreResponse fill:#d1ecf1
```

---

## Error Handling Flow

```mermaid
flowchart TD
    Request[API Request] --> Validate{Valid<br/>Request?}
    
    Validate -->|No| Error400[400 Bad Request]
    Validate -->|Yes| Process[Process Query]
    
    Process --> ParseError{Parse<br/>Error?}
    ParseError -->|Yes| DefaultIntent[Use Default Intent<br/>+ Confidence 0.3]
    ParseError -->|No| Continue1[Continue]
    
    DefaultIntent --> Continue1
    
    Continue1 --> RAGError{RAG<br/>Error?}
    RAGError -->|Yes| EmptyResults[Return Empty<br/>Results]
    RAGError -->|No| RAGSuccess[RAG Results]
    
    EmptyResults --> Continue2[Continue]
    RAGSuccess --> Continue2
    
    Continue2 --> ClaudeError{Claude API<br/>Error?}
    
    ClaudeError -->|401| AuthError[Invalid API Key]
    ClaudeError -->|404| ModelError[Model Not Found]
    ClaudeError -->|429| RateLimit[Rate Limit]
    ClaudeError -->|500| ServerError[Server Error]
    ClaudeError -->|No| ClaudeSuccess[Success Response]
    
    AuthError --> ErrorResponse[Generic Error<br/>Message]
    ModelError --> ErrorResponse
    RateLimit --> ErrorResponse
    ServerError --> ErrorResponse
    
    ErrorResponse --> Log[Log Error]
    ClaudeSuccess --> Success[Format Response]
    
    Log --> Return500[500 Internal<br/>Server Error]
    Success --> Return200[200 OK]
    
    style Validate fill:#fff3cd
    style ClaudeError fill:#f8d7da
    style Success fill:#d4edda
```

---

## Performance Optimization Flow

```mermaid
graph TB
    subgraph Optimization["⚡ Performance Optimization Layers"]
        L1[Layer 1: Redis Cache<br/>- Query embeddings<br/>- Search results<br/>- Responses]
        
        L2[Layer 2: Database Indexing<br/>- Vector indexes<br/>- Graph indexes<br/>- SQL indexes]
        
        L3[Layer 3: Async Processing<br/>- Parallel RAG/Git/Static calls<br/>- Non-blocking I/O]
        
        L4[Layer 4: Connection Pooling<br/>- Database pools<br/>- HTTP keep-alive]
        
        L1 --> L2
        L2 --> L3
        L3 --> L4
    end
    
    Query[User Query] --> L1
    L4 --> Response[Fast Response<br/>< 3 seconds]
    
    style L1 fill:#d4edda
    style Response fill:#cfe2ff
```

---

## Data Volume & Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Files Indexed** | 389 files | All code, config, docs |
| **Total Chunks** | 443 chunks | AST-based + line-based |
| **Vector Dimensions** | 768 | all-mpnet-base-v2 model |
| **Avg Query Time** | 2-3 seconds | Including Claude API |
| **Cache Hit Rate** | 60-70% | For repeat queries |
| **Embedding Generation** | ~200ms | Per query |
| **Vector Search** | ~100ms | Top 10 results |
| **Claude API Call** | 1-2 seconds | Model response time |
| **Database Queries** | < 50ms | PostgreSQL + Neo4j |

---

## Data Security & Privacy

```mermaid
flowchart LR
    subgraph Input["🔒 Input Security"]
        UserInput[User Input] --> Sanitize[Sanitize & Validate]
        Sanitize --> RateLimit[Rate Limiting]
    end
    
    subgraph Processing["🔐 Processing Security"]
        RateLimit --> Encrypt[Encrypt in Transit<br/>HTTPS/TLS]
        Encrypt --> Isolate[Container Isolation<br/>Docker]
    end
    
    subgraph Storage["💾 Storage Security"]
        Isolate --> DBEncrypt[Database Encryption]
        DBEncrypt --> Access[Access Control<br/>Authentication]
        Access --> Backup[Encrypted Backups]
    end
    
    subgraph Output["📤 Output Security"]
        Backup --> Sanitize2[Sanitize Output]
        Sanitize2 --> Audit[Audit Logging]
        Audit --> Response[Secure Response]
    end
    
    style Input fill:#fff3cd
    style Processing fill:#d1ecf1
    style Storage fill:#f8d7da
    style Output fill:#d4edda
```

---

## Conclusion

The CodeBot AI data flow is designed for:
- ✅ **Efficiency** - Multi-layer caching reduces latency
- ✅ **Accuracy** - Multi-engine approach ensures comprehensive context
- ✅ **Scalability** - Async processing and database optimization
- ✅ **Reliability** - Error handling at every layer
- ✅ **Security** - Encryption and access control throughout

**Query Response Time:** < 3 seconds end-to-end  
**Cache Hit Rate:** 60-70% for common queries  
**Accuracy:** High-quality context retrieval with RAG
