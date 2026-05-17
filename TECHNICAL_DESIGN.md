# CodeBot AI - Technical Design & Architecture

## System Architecture Overview

```mermaid
graph TB
    subgraph Client["👥 Client Layer"]
        Browser[Web Browser<br/>Chrome/Firefox/Safari]
        Mobile[Mobile Browser<br/>iOS/Android]
    end
    
    subgraph Frontend["🎨 Frontend Layer - Port 3000"]
        React[React 18.3.1<br/>TypeScript 5.2.2]
        Vite[Vite Build Tool<br/>Hot Module Reload]
        TailwindCSS[Tailwind CSS<br/>Responsive Design]
        Axios[Axios HTTP Client<br/>API Communication]
        
        React --> Components
        
        subgraph Components["📦 Component Architecture"]
            Layout[Main Layout]
            Chat[Chat Window]
            Search[Search Panel]
            Dashboard[Repo Dashboard]
            History[Conversation History]
        end
    end
    
    subgraph Gateway["🚪 API Gateway - Port 8000"]
        FastAPI[FastAPI 0.104.1<br/>Python 3.11]
        CORS[CORS Middleware]
        Validation[Pydantic Validation]
        Health[Health Check Endpoints]
    end
    
    subgraph Intelligence["🧠 Intelligence Layer"]
        QueryParser[Query Parser<br/>Intent Detection]
        ExceptionParser[Exception Parser<br/>Stack Trace Analysis]
        Orchestrator[Agent Orchestrator<br/>Multi-Engine Coordination]
        ContextBuilder[Context Builder<br/>Prompt Engineering]
    end
    
    subgraph Engines["⚙️ Processing Engines"]
        RAG[RAG Engine<br/>Vector Search]
        StaticAnalyzer[Static Analyzer<br/>Code Relationships]
        GitAnalyzer[Git Analyzer<br/>History & Blame]
    end
    
    subgraph AI["🤖 AI Layer"]
        Claude[Anthropic Claude<br/>Sonnet 4.6<br/>200K Context]
    end
    
    subgraph Storage["💾 Data Storage Layer"]
        ChromaDB[(ChromaDB<br/>Vector Database<br/>443 chunks)]
        Neo4j[(Neo4j 5.14<br/>Graph Database<br/>Code Graph)]
        PostgreSQL[(PostgreSQL 15<br/>Relational DB<br/>Git History)]
        Redis[(Redis 7<br/>Cache Layer<br/>TTL: 1 hour)]
    end
    
    Browser --> React
    Mobile --> React
    React --> FastAPI
    
    FastAPI --> CORS
    CORS --> Validation
    Validation --> QueryParser
    
    QueryParser --> ExceptionParser
    ExceptionParser --> Orchestrator
    
    Orchestrator --> RAG
    Orchestrator --> StaticAnalyzer
    Orchestrator --> GitAnalyzer
    
    RAG --> ChromaDB
    StaticAnalyzer --> Neo4j
    GitAnalyzer --> PostgreSQL
    
    Orchestrator --> ContextBuilder
    ContextBuilder --> Claude
    Claude --> Redis
    
    Redis --> FastAPI
    
    style Client fill:#e1f5ff
    style Frontend fill:#fff3cd
    style Gateway fill:#d1ecf1
    style Intelligence fill:#f8d7da
    style Engines fill:#d4edda
    style AI fill:#fce8e6
    style Storage fill:#e7f3ff
```

---

## Detailed Component Architecture

### 1. Frontend Architecture

```mermaid
graph TB
    subgraph UI["React Frontend Application"]
        App[App.tsx<br/>Root Component]
        
        App --> Router{React Router}
        
        Router --> ChatRoute[/chat<br/>Chat Interface]
        Router --> SearchRoute[/search<br/>Code Search]
        Router --> DashboardRoute[/dashboard<br/>Repository Info]
        Router --> HistoryRoute[/history<br/>Past Conversations]
        
        subgraph Context["State Management"]
            ChatContext[ChatContext<br/>Conversation State]
            AppContext[AppContext<br/>Global App State]
        end
        
        ChatRoute --> ChatWindow[ChatWindow Component]
        ChatWindow --> MessageList[MessageList<br/>Display Messages]
        ChatWindow --> MessageInput[MessageInput<br/>Send Queries]
        MessageList --> CodeBlock[CodeBlock<br/>Syntax Highlighting]
        
        SearchRoute --> SearchPanel[SearchPanel Component]
        SearchPanel --> SearchResults[SearchResults<br/>Code Matches]
        
        DashboardRoute --> RepoStats[RepoStats<br/>Metrics Display]
        DashboardRoute --> IndexingStatus[IndexingStatus<br/>Progress Tracking]
        
        HistoryRoute --> ConversationList[ConversationList<br/>LocalStorage]
        
        subgraph Services["API Services"]
            APIClient[api.ts<br/>Axios Instance]
            ChatService[chatService.ts<br/>Chat Endpoints]
            SearchService[searchService.ts<br/>Search Endpoints]
            RepoService[repoService.ts<br/>Repo Endpoints]
        end
        
        ChatWindow --> ChatService
        SearchPanel --> SearchService
        RepoStats --> RepoService
        
        ChatService --> APIClient
        SearchService --> APIClient
        RepoService --> APIClient
        
        ChatContext -.-> ChatWindow
        AppContext -.-> RepoStats
    end
    
    APIClient --> Backend[FastAPI Backend<br/>http://localhost:8000]
    
    style App fill:#fff3cd
    style Context fill:#d4edda
    style Services fill:#d1ecf1
```

#### Frontend Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 18.3.1 | UI component library |
| **Language** | TypeScript | 5.2.2 | Type safety |
| **Build Tool** | Vite | 5.1.0 | Fast dev server & bundling |
| **Styling** | Tailwind CSS | 3.4.1 | Utility-first styling |
| **HTTP Client** | Axios | 1.6.0 | API communication |
| **Icons** | Lucide React | 0.344.0 | Icon library |
| **Code Highlighting** | react-syntax-highlighter | 15.5.0 | Code display |
| **State** | React Context | Built-in | Global state |
| **Storage** | LocalStorage | Browser API | Conversation persistence |

---

### 2. Backend Architecture

```mermaid
graph TB
    subgraph API["FastAPI Backend"]
        Main[main.py<br/>Application Entry]
        
        Main --> Routes[API Routes]
        
        subgraph Endpoints["REST Endpoints"]
            ChatEP[POST /api/chat<br/>Main chat endpoint]
            SearchEP[POST /api/search<br/>Code search]
            StatusEP[GET /api/repo/status<br/>Repository info]
            IndexEP[POST /api/repo/index<br/>Trigger indexing]
            HealthEP[GET /health<br/>Health check]
        end
        
        Routes --> ChatEP
        Routes --> SearchEP
        Routes --> StatusEP
        Routes --> IndexEP
        Routes --> HealthEP
        
        ChatEP --> Parsers
        
        subgraph Parsers["Query Processing"]
            QParser[QueryParser<br/>Intent + Entities]
            EParser[ExceptionParser<br/>Stack Traces]
        end
        
        Parsers --> Orchestrator[AgentOrchestrator<br/>Query Router]
        
        Orchestrator --> EngineLayer
        
        subgraph EngineLayer["Processing Engines"]
            RAGEngine[RAG Engine<br/>embeddings + search]
            StaticEngine[Static Analyzer<br/>AST + dependencies]
            GitEngine[Git Analyzer<br/>history + blame]
        end
        
        EngineLayer --> DBLayer
        
        subgraph DBLayer["Data Access"]
            ChromaClient[ChromaDB Client]
            Neo4jClient[Neo4j Driver]
            PGClient[PostgreSQL psycopg2]
            RedisClient[Redis Client]
        end
        
        Orchestrator --> ContextBuilder[Context Builder<br/>Prompt Templates]
        ContextBuilder --> ClaudeClient[Anthropic SDK<br/>Claude API]
        
        ClaudeClient --> Response[Response Formatter]
        Response --> ChatEP
    end
    
    style Main fill:#fff3cd
    style Endpoints fill:#d1ecf1
    style Parsers fill:#f8d7da
    style Orchestrator fill:#fce8e6
    style EngineLayer fill:#d4edda
    style DBLayer fill:#e7f3ff
```

#### Backend Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104.1 | High-performance async API |
| **Language** | Python | 3.11 | Programming language |
| **ASGI Server** | Uvicorn | 0.24.0 | Production server |
| **Validation** | Pydantic | 2.5.0 | Data validation |
| **AI SDK** | Anthropic | 0.102.0 | Claude API client |
| **Embeddings** | sentence-transformers | 2.7.0 | Vector embeddings |
| **Vector DB** | ChromaDB | 0.4.18 | Vector storage |
| **Graph DB** | Neo4j | 5.14.1 | Code relationships |
| **SQL DB** | PostgreSQL | psycopg2 2.9.9 | Git history |
| **Cache** | Redis | 5.0.1 | Query caching |
| **Git** | GitPython | 3.1.40 | Repository access |

---

### 3. Intelligence Layer Architecture

```mermaid
graph LR
    subgraph QueryProcessing["Query Processing Pipeline"]
        Input[User Query] --> QP[Query Parser]
        
        QP --> IntentDetection{Intent<br/>Detection}
        QP --> EntityExtract[Entity Extraction:<br/>- Files<br/>- Functions<br/>- Classes<br/>- Errors]
        QP --> KeywordExtract[Keyword Extraction<br/>Stopword Filtering]
        
        IntentDetection --> BugIntent[BUG_ANALYSIS]
        IntentDetection --> SearchIntent[CODE_SEARCH]
        IntentDetection --> AuthorIntent[AUTHOR_LOOKUP]
        IntentDetection --> ExplainIntent[CODE_EXPLANATION]
        IntentDetection --> DepIntent[DEPENDENCY_CHECK]
        IntentDetection --> GenIntent[GENERAL_QUESTION]
        
        EntityExtract --> Confidence[Confidence<br/>Calculation]
        KeywordExtract --> Confidence
        IntentDetection --> Confidence
        
        Confidence --> ParsedQuery[ParsedQuery Object:<br/>- intent<br/>- entities<br/>- keywords<br/>- confidence]
    end
    
    ParsedQuery --> Orchestrator[Agent Orchestrator]
    
    subgraph Routing["Query Routing"]
        Orchestrator --> RouteLogic{Route Based<br/>on Intent}
        
        RouteLogic -->|BUG_ANALYSIS| BugHandler[_handle_bug_analysis]
        RouteLogic -->|CODE_SEARCH| SearchHandler[_handle_code_search]
        RouteLogic -->|AUTHOR_LOOKUP| AuthorHandler[_handle_author_lookup]
        RouteLogic -->|CODE_EXPLANATION| ExplainHandler[_handle_explanation]
        RouteLogic -->|DEPENDENCY_CHECK| DepHandler[_handle_dependency_check]
        RouteLogic -->|GENERAL_QUESTION| GenHandler[_handle_general_question]
    end
    
    BugHandler --> Multi[Multi-Engine<br/>Data Gathering]
    SearchHandler --> Multi
    AuthorHandler --> Multi
    ExplainHandler --> Multi
    DepHandler --> Multi
    GenHandler --> Multi
    
    style IntentDetection fill:#fff3cd
    style Orchestrator fill:#f8d7da
    style Multi fill:#d4edda
```

#### Intent Detection Patterns

| Intent | Regex Patterns | Example Queries |
|--------|----------------|-----------------|
| **BUG_ANALYSIS** | `bug\|error\|fail\|crash\|broken` | "Why is this function failing?" |
| **CODE_SEARCH** | `find\|search\|locate\|where is` | "Find the authentication code" |
| **AUTHOR_LOOKUP** | `who wrote\|who created\|author` | "Who wrote this class?" |
| **CODE_EXPLANATION** | `explain\|how does\|what does\|why` | "Why are API tokens used?" |
| **DEPENDENCY_CHECK** | `depends on\|who calls\|impact` | "What depends on this function?" |
| **GENERAL_QUESTION** | Default fallback | "What is this project about?" |

---

### 4. RAG Engine Architecture

```mermaid
graph TB
    subgraph Indexing["📥 Indexing Phase (One-Time)"]
        Repo[Git Repository] --> FileScanner[File Scanner<br/>Glob Pattern Matching]
        
        FileScanner --> TypeDetect{File Type<br/>Detection}
        
        TypeDetect -->|Python| PythonChunker[Python Chunker<br/>AST-Based]
        TypeDetect -->|Other| GenericChunker[Generic Chunker<br/>Line-Based]
        
        PythonChunker --> Chunks1[Code Chunks:<br/>- Classes<br/>- Functions<br/>- Methods]
        GenericChunker --> Chunks2[Code Chunks:<br/>- Fixed-size blocks<br/>- With overlap]
        
        Chunks1 --> Embedder[Embedding Generator<br/>all-mpnet-base-v2]
        Chunks2 --> Embedder
        
        Embedder --> Vectors[768-dim Vectors]
        
        Vectors --> ChromaDB[(ChromaDB<br/>Vector Store<br/>443 chunks)]
    end
    
    subgraph Query["🔍 Query Phase (Runtime)"]
        UserQuery[User Query] --> QueryEmbed[Generate<br/>Query Embedding]
        
        QueryEmbed --> CacheCheck{Check<br/>Redis Cache}
        
        CacheCheck -->|Hit| CachedVec[Use Cached<br/>Embedding]
        CacheCheck -->|Miss| GenVec[Generate New<br/>Embedding]
        
        GenVec --> StoreCache[Store in Cache]
        
        CachedVec --> Search[Cosine Similarity<br/>Search]
        StoreCache --> Search
        
        Search --> ChromaDB
        ChromaDB --> TopK[Top K Results<br/>K = 3-10]
        
        TopK --> Rerank[Score Filtering<br/>Min Score = 0.5]
        
        Rerank --> Results[Relevant<br/>Code Chunks]
    end
    
    style PythonChunker fill:#d4edda
    style GenericChunker fill:#fff3cd
    style ChromaDB fill:#e7f3ff
    style CacheCheck fill:#fce8e6
```

#### RAG Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Embedding Model** | all-mpnet-base-v2 | 768-dim sentence embeddings |
| **Chunk Size** | 1000 lines | Max lines per chunk |
| **Chunk Overlap** | 200 lines | Overlap between chunks |
| **Top K Results** | 3-10 | Varies by intent type |
| **Min Similarity** | 0.5 | Minimum relevance score |
| **Cache TTL** | 3600s | 1 hour cache expiration |
| **Supported Languages** | 30+ | Python, Java, JS, TS, Go, etc. |

---

### 5. Database Architecture

```mermaid
graph TB
    subgraph VectorDB["ChromaDB - Vector Database"]
        Collections[Collections]
        Collections --> CodeChunks[code_chunks<br/>Collection]
        
        CodeChunks --> Metadata[Metadata:<br/>- filepath<br/>- chunk_id<br/>- type<br/>- name<br/>- language<br/>- start_line<br/>- end_line]
        
        CodeChunks --> Embeddings[Embeddings:<br/>768-dimensional<br/>vectors]
        
        CodeChunks --> Documents[Documents:<br/>Code content<br/>+ context]
    end
    
    subgraph GraphDB["Neo4j - Graph Database"]
        Nodes[Node Types]
        Nodes --> FileNode[File Node<br/>filepath, language]
        Nodes --> FuncNode[Function Node<br/>name, params]
        Nodes --> ClassNode[Class Node<br/>name, methods]
        
        Rels[Relationship Types]
        Rels --> Imports[IMPORTS<br/>file → file]
        Rels --> Contains[CONTAINS<br/>file → class/func]
        Rels --> Calls[CALLS<br/>func → func]
        Rels --> Inherits[INHERITS<br/>class → class]
    end
    
    subgraph RelationalDB["PostgreSQL - Relational Database"]
        Tables[Tables]
        Tables --> Commits[commits<br/>- sha<br/>- author<br/>- date<br/>- message<br/>- files_changed]
        
        Tables --> FileChanges[file_changes<br/>- commit_sha<br/>- filepath<br/>- change_type<br/>- insertions<br/>- deletions]
        
        Indexes[Indexes]
        Indexes --> CommitDate[idx_commits_date]
        Indexes --> FilePath[idx_file_changes_path]
        Indexes --> CommitSHA[idx_file_changes_commit]
    end
    
    subgraph CacheDB["Redis - Cache Layer"]
        CacheTypes[Cache Keys]
        CacheTypes --> QueryCache[query_embed:*<br/>TTL: 1h]
        CacheTypes --> ResultCache[search_results:*<br/>TTL: 1h]
        CacheTypes --> ResponseCache[response:*<br/>TTL: 1h]
    end
    
    style VectorDB fill:#d4edda
    style GraphDB fill:#f8d7da
    style RelationalDB fill:#cfe2ff
    style CacheDB fill:#fff3cd
```

#### Database Schemas

**ChromaDB Schema:**
```python
{
    "id": "chunk_id_hash",
    "embedding": [768-dim vector],
    "metadata": {
        "filepath": "/path/to/file.py",
        "type": "function|class|method|module",
        "name": "function_name",
        "language": "python",
        "start_line": 10,
        "end_line": 50,
        "methods": ["method1", "method2"],
        "imports": ["module1", "module2"]
    },
    "document": "actual code content"
}
```

**Neo4j Schema:**
```cypher
// Nodes
(:File {filepath, language, size})
(:Function {name, params, returns})
(:Class {name, methods[]})

// Relationships
(:File)-[:IMPORTS]->(:File)
(:File)-[:CONTAINS]->(:Function|:Class)
(:Function)-[:CALLS]->(:Function)
(:Class)-[:INHERITS]->(:Class)
```

**PostgreSQL Schema:**
```sql
CREATE TABLE commits (
    sha VARCHAR(40) PRIMARY KEY,
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    commit_date TIMESTAMP,
    message TEXT,
    files_changed INTEGER
);

CREATE TABLE file_changes (
    id SERIAL PRIMARY KEY,
    commit_sha VARCHAR(40) REFERENCES commits(sha),
    filepath VARCHAR(500),
    change_type VARCHAR(20),
    insertions INTEGER,
    deletions INTEGER
);
```

---

### 6. AI Integration Architecture

```mermaid
graph LR
    subgraph PromptEngineering["Prompt Engineering Layer"]
        ContextBuilder[Context Builder] --> Templates{Prompt<br/>Templates}
        
        Templates -->|Exception| ExceptPrompt[Exception Analysis:<br/>- Root cause<br/>- Why happening<br/>- Fix with code<br/>- Prevention]
        
        Templates -->|Bug| BugPrompt[Bug Analysis:<br/>- Root cause<br/>- Solution]
        
        Templates -->|Explain| ExplainPrompt[Code Explanation:<br/>- Plain English<br/>- Use analogies<br/>- No jargon<br/>- Conversational]
        
        Templates -->|Search| SearchPrompt[Code Search:<br/>- Based on context<br/>- Answer query]
        
        Templates -->|General| GenPrompt[General Q&A:<br/>- Helpful answer<br/>- Use context]
    end
    
    ExceptPrompt --> Claude[Claude API]
    BugPrompt --> Claude
    ExplainPrompt --> Claude
    SearchPrompt --> Claude
    GenPrompt --> Claude
    
    subgraph ClaudeConfig["Claude Configuration"]
        Claude --> Model[Model:<br/>claude-sonnet-4-6]
        Claude --> Tokens[Max Tokens:<br/>4096]
        Claude --> Context[Context Window:<br/>200K tokens]
    end
    
    Claude --> Response[Response<br/>Processing]
    
    Response --> Format[Format &<br/>Return]
    
    style Templates fill:#fff3cd
    style Claude fill:#fce8e6
    style Response fill:#d4edda
```

#### Claude API Configuration

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Model** | claude-sonnet-4-6 | Latest Sonnet model |
| **Max Tokens** | 4096 | Response length limit |
| **Context Window** | 200K tokens | Maximum context size |
| **Temperature** | Default (1.0) | Response randomness |
| **API Version** | 2023-06-01 | Anthropic API version |

---

### 7. Docker Container Architecture

```mermaid
graph TB
    subgraph DockerCompose["Docker Compose Orchestration"]
        Network[Docker Network<br/>codebot-complete_default]
        
        Network --> Frontend[Frontend Container<br/>nginx:alpine<br/>Port 3000→80]
        Network --> API[API Container<br/>python:3.11-slim<br/>Port 8000]
        Network --> PG[PostgreSQL Container<br/>postgres:15-alpine<br/>Port 5432]
        Network --> N4J[Neo4j Container<br/>neo4j:5.14-community<br/>Port 7687, 7474]
        Network --> RedisC[Redis Container<br/>redis:7-alpine<br/>Port 6379]
        
        subgraph Volumes["Persistent Volumes"]
            PGVol[(postgres_data)]
            N4JVol[(neo4j_data)]
            ChromaVol[(chroma_data)]
            RepoVol[(repo_data)]
        end
        
        API --> ChromaVol
        API --> RepoVol
        PG --> PGVol
        N4J --> N4JVol
    end
    
    subgraph HealthChecks["Health Checks"]
        API --> APIHC[HTTP GET /health<br/>Interval: 30s<br/>Timeout: 10s]
        PG --> PGHC[pg_isready<br/>Interval: 10s]
        N4J --> N4JHC[cypher-shell<br/>Interval: 30s]
        RedisC --> RedisHC[redis-cli ping<br/>Interval: 10s]
    end
    
    style Frontend fill:#fff3cd
    style API fill:#d1ecf1
    style PG fill:#cfe2ff
    style N4J fill:#f8d7da
    style RedisC fill:#fce8e6
    style Volumes fill:#e7f3ff
```

#### Container Specifications

| Container | Base Image | CPU | Memory | Ports | Health Check |
|-----------|-----------|-----|--------|-------|--------------|
| **Frontend** | nginx:alpine | 0.5 | 256MB | 3000:80 | HTTP / |
| **API** | python:3.11-slim | 2.0 | 2GB | 8000:8000 | GET /health |
| **PostgreSQL** | postgres:15-alpine | 1.0 | 512MB | 5432:5432 | pg_isready |
| **Neo4j** | neo4j:5.14 | 1.0 | 1GB | 7687,7474 | cypher-shell |
| **Redis** | redis:7-alpine | 0.5 | 256MB | 6379:6379 | ping |

---

### 8. Security Architecture

```mermaid
graph TB
    subgraph External["External Access"]
        User[User/Client]
    end
    
    subgraph SecurityLayers["Security Layers"]
        HTTPS[HTTPS/TLS<br/>Encrypted Transport]
        CORS[CORS Policy<br/>Origin Validation]
        RateLimit[Rate Limiting<br/>60 req/min]
        Validation[Input Validation<br/>Pydantic Schemas]
    end
    
    subgraph Authentication["Authentication & Authorization"]
        APIKey[API Key Management<br/>Anthropic]
        DBAuth[Database Auth<br/>Username/Password]
        Secrets[Environment Secrets<br/>.env file]
    end
    
    subgraph DataProtection["Data Protection"]
        Encryption[Data Encryption<br/>At Rest & In Transit]
        Isolation[Container Isolation<br/>Docker Networks]
        Backup[Automated Backups<br/>Volume Snapshots]
    end
    
    User --> HTTPS
    HTTPS --> CORS
    CORS --> RateLimit
    RateLimit --> Validation
    
    Validation --> APIKey
    APIKey --> DBAuth
    DBAuth --> Secrets
    
    Secrets --> Encryption
    Encryption --> Isolation
    Isolation --> Backup
    
    style HTTPS fill:#d4edda
    style CORS fill:#fff3cd
    style Validation fill:#d1ecf1
    style Encryption fill:#fce8e6
```

---

### 9. Monitoring & Observability

```mermaid
graph LR
    subgraph Application["Application Layer"]
        API[FastAPI Backend]
        Frontend[React Frontend]
    end
    
    subgraph Logging["Logging"]
        AppLogs[Application Logs<br/>Python logging]
        AccessLogs[Access Logs<br/>Uvicorn]
        ErrorLogs[Error Logs<br/>Exception tracking]
    end
    
    subgraph Metrics["Metrics & Health"]
        Health[Health Endpoints<br/>GET /health]
        RAGMetrics[RAG Metrics:<br/>- Chunks indexed<br/>- Query performance]
        DBMetrics[DB Metrics:<br/>- Connection pool<br/>- Query time]
        CacheMetrics[Cache Metrics:<br/>- Hit rate<br/>- Miss rate]
    end
    
    subgraph Monitoring["Monitoring (Future)"]
        Prometheus[Prometheus<br/>Time-series DB]
        Grafana[Grafana<br/>Visualization]
        Alerts[Alerting<br/>PagerDuty/Email]
    end
    
    API --> AppLogs
    Frontend --> AccessLogs
    API --> ErrorLogs
    
    API --> Health
    API --> RAGMetrics
    API --> DBMetrics
    API --> CacheMetrics
    
    Health --> Prometheus
    RAGMetrics --> Prometheus
    DBMetrics --> Prometheus
    CacheMetrics --> Prometheus
    
    Prometheus --> Grafana
    Grafana --> Alerts
    
    style Health fill:#d4edda
    style Prometheus fill:#cfe2ff
    style Grafana fill:#fff3cd
```

---

## Deployment Architecture

### Development Environment

```
localhost:3000 (Frontend) → localhost:8000 (API)
                          ↓
                    [All DBs on localhost]
                    - PostgreSQL: 5432
                    - Neo4j: 7687, 7474
                    - Redis: 6379
                    - ChromaDB: In-process
```

### Production Environment (Recommended)

```mermaid
graph TB
    subgraph Internet["🌐 Internet"]
        Users[Users]
    end
    
    subgraph LoadBalancer["⚖️ Load Balancer"]
        LB[Nginx/HAProxy<br/>SSL Termination]
    end
    
    subgraph AppServers["🖥️ Application Servers"]
        Frontend1[Frontend Pod 1]
        Frontend2[Frontend Pod 2]
        API1[API Pod 1]
        API2[API Pod 2]
        API3[API Pod 3]
    end
    
    subgraph Databases["💾 Managed Databases"]
        RDS[RDS PostgreSQL<br/>Multi-AZ]
        Neo4jCloud[Neo4j Aura<br/>Managed]
        ElastiCache[ElastiCache Redis<br/>Cluster Mode]
    end
    
    subgraph Storage["📦 Object Storage"]
        S3[S3 Bucket<br/>ChromaDB Persistence]
    end
    
    Users --> LB
    LB --> Frontend1
    LB --> Frontend2
    Frontend1 --> API1
    Frontend2 --> API2
    Frontend1 --> API3
    
    API1 --> RDS
    API2 --> RDS
    API3 --> RDS
    
    API1 --> Neo4jCloud
    API2 --> Neo4jCloud
    API3 --> Neo4jCloud
    
    API1 --> ElastiCache
    API2 --> ElastiCache
    API3 --> ElastiCache
    
    API1 --> S3
    API2 --> S3
    API3 --> S3
    
    style LB fill:#fff3cd
    style AppServers fill:#d1ecf1
    style Databases fill:#cfe2ff
    style Storage fill:#e7f3ff
```

---

## Technology Stack Summary

### Frontend Stack
- React 18.3.1 + TypeScript
- Vite build tool
- Tailwind CSS
- Axios HTTP client
- React Context for state
- LocalStorage for persistence

### Backend Stack
- FastAPI 0.104.1 (Python 3.11)
- Pydantic validation
- Uvicorn ASGI server
- Anthropic SDK (Claude)
- Sentence Transformers

### Data Layer
- **Vector DB:** ChromaDB 0.4.18
- **Graph DB:** Neo4j 5.14
- **SQL DB:** PostgreSQL 15
- **Cache:** Redis 7

### Infrastructure
- Docker & Docker Compose
- Nginx (production)
- Multi-stage builds
- Health checks & auto-restart

---

## Performance Characteristics

| Metric | Target | Actual |
|--------|--------|--------|
| **API Response Time** | < 3s | 2-3s |
| **Frontend Load Time** | < 2s | 1.5s |
| **Query Processing** | < 1s | 0.8s |
| **Database Queries** | < 100ms | 50ms avg |
| **Cache Hit Rate** | > 50% | 60-70% |
| **Concurrent Users** | 100+ | Tested: 50 |
| **Uptime** | 99.9% | Target |

---

## Scalability Considerations

### Horizontal Scaling
- ✅ **API Servers:** Stateless, can scale to N instances
- ✅ **Frontend:** Static files, CDN-ready
- ✅ **Databases:** Use managed services (RDS, Aura)
- ✅ **Cache:** Redis cluster mode

### Vertical Scaling
- ⚙️ **API Memory:** 2GB → 4GB for larger repos
- ⚙️ **Neo4j:** 1GB → 2GB for complex graphs
- ⚙️ **PostgreSQL:** SSD storage for performance

### Data Scaling
- 📊 **Current:** 389 files, 443 chunks
- 📈 **Tested:** Up to 1000 files, 1200 chunks
- 🎯 **Target:** 10,000 files, 15,000 chunks

---

## Conclusion

The CodeBot AI technical architecture is designed for:

- ✅ **Modularity** - Independent, replaceable components
- ✅ **Scalability** - Horizontal and vertical scaling
- ✅ **Reliability** - Health checks, auto-restart, fallbacks
- ✅ **Performance** - Multi-layer caching, async processing
- ✅ **Security** - Encryption, isolation, validation
- ✅ **Maintainability** - Clear separation of concerns

**Production-ready architecture for enterprise deployment!** 🚀
