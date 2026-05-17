# 🤖 CodeBot AI - Intelligent Code Analysis Chatbot

**✅ COMPLETE IMPLEMENTATION - READY TO RUN**

AI-powered code assistant with RAG (Retrieval Augmented Generation), static analysis, and git integration. Analyzes your codebase, answers questions, debugs issues, and tracks code history.

## 🎯 Features

- ✅ **Semantic Code Search** - Natural language queries to find code
- ✅ **Bug Analysis** - Analyzes exception logs and finds root causes
- ✅ **Git Integration** - Track who wrote what and when
- ✅ **Dependency Analysis** - Understand code relationships
- ✅ **Code Explanation** - AI explains complex code
- ✅ **Real-time Indexing** - Auto-syncs with git repository

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (if running without Docker)
- Git repository to analyze
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone this repository
git clone <your-repo-url>
cd code-aware-chatbot

# Copy environment template
cp .env.example .env

# Edit .env and add your Anthropic API key
nano .env  # or use your preferred editor
```

### 2. Configure Your Target Repository

```bash
# Option A: Use an existing local repository
# Set REPO_PATH in .env to point to your repository
REPO_PATH=/path/to/your/repository

# Option B: Clone a repository to analyze
git clone <target-repo-url> ./target_repo
```

### 3. Start All Services

```bash
# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api
```

### 4. Initialize the System

```bash
# Wait for all services to be healthy (check logs)
# Then trigger initial indexing
curl -X POST http://localhost:8000/api/repo/index
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Try a chat query
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find the authentication code",
    "conversation_id": "test-conv-1"
  }'
```

## 📁 Project Structure

```
code-aware-chatbot/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── engines/                # Core processing engines
│   │   ├── rag_engine.py      # Semantic search
│   │   ├── static_analyzer.py # Code analysis
│   │   ├── git_analyzer.py    # Git integration
│   │   └── chunking.py        # Code chunking
│   ├── parsers/                # Query parsers
│   │   ├── query_parser.py    # Intent detection
│   │   └── exception_parser.py # Exception parsing
│   ├── agents/                 # Agent orchestration
│   │   ├── orchestrator.py    # Main router
│   │   └── context_builder.py # Context assembly
│   └── models/                 # Data models
│       └── schemas.py          # Pydantic models
├── docker-compose.yml          # Service orchestration
├── Dockerfile                  # API container
├── .env                        # Environment variables
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...       # Get from Anthropic
POSTGRES_PASSWORD=securepass123
NEO4J_PASSWORD=securepass123
REPO_PATH=./target_repo

# Optional
DEBUG=False
LOG_LEVEL=INFO
RAG_TOP_K=5
SYNC_INTERVAL_SECONDS=300
```

## 📚 API Endpoints

### Chat Endpoints

```bash
# Main chat interface
POST /api/chat
{
  "message": "Why is authentication failing?",
  "conversation_id": "conv_123"
}

# Streaming responses
POST /api/chat/stream
```

### Search Endpoints

```bash
# Semantic code search
POST /api/search
{
  "query": "JWT token validation",
  "max_results": 10
}
```

### Analysis Endpoints

```bash
# Bug analysis
POST /api/analyze/bug
{
  "description": "Users can't login",
  "stack_trace": "Traceback..."
}

# Dependency analysis
GET /api/analyze/dependencies/{function_name}
```

### Repository Management

```bash
# Repository status
GET /api/repo/status

# Sync repository
POST /api/repo/sync

# Re-index repository
POST /api/repo/index
```

## 💬 Usage Examples

### Example 1: Bug Analysis with Exception Log

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I'\''m getting this error:\n\nTraceback (most recent call last):\n  File \"/app/src/auth.py\", line 48, in validate_token\n    raise ValueError(\"Invalid token format\")\nValueError: Invalid token format\n\nThis started after yesterday'\''s deployment."
  }'
```

**Response:**
```json
{
  "response": "The error is in src/auth.py at line 48...",
  "sources": [...],
  "git_info": [{
    "author": "Sarah Mitchell",
    "date": "2024-05-15",
    "message": "Add token validation"
  }],
  "intent": "bug_analysis",
  "confidence": "high"
}
```

### Example 2: Find Code

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find the function that validates JWT tokens"
  }'
```

### Example 3: Who Wrote This

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Who wrote the payment processing code?"
  }'
```

## 🔍 How It Works

1. **User Query** → Parsed for intent (bug, search, explanation)
2. **Parallel Processing:**
   - RAG Engine searches vector database
   - Static Analyzer queries code graph
   - Git Analyzer gets commit history
3. **Context Builder** → Merges all results
4. **Claude AI** → Analyzes and generates response
5. **User** → Receives comprehensive answer

## 🛠️ Development

### Running Without Docker

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set up databases (PostgreSQL, Neo4j, Redis)
# Update .env with connection details

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Setup

```bash
# PostgreSQL
CREATE DATABASE codebot;

# Neo4j - Access browser at http://localhost:7474
# Default credentials: neo4j / neo4j
# Change password on first login

# Redis - No setup needed
```

## 📊 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f neo4j
```

### Database Access

```bash
# PostgreSQL
docker exec -it codebot-postgres psql -U postgres -d codebot

# Neo4j Browser
# Open http://localhost:7474 in browser

# Redis CLI
docker exec -it codebot-redis redis-cli
```

## 🐛 Troubleshooting

### Issue: API not starting

```bash
# Check logs
docker-compose logs api

# Check if databases are ready
docker-compose ps

# Restart services
docker-compose restart
```

### Issue: No search results

```bash
# Check if repository is indexed
curl http://localhost:8000/api/repo/status

# Trigger reindexing
curl -X POST http://localhost:8000/api/repo/index
```

### Issue: Out of memory

```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory

# Or reduce batch size in config.py
RAG_CHUNK_SIZE=500
```

## 🔐 Security

- Store `.env` file securely - never commit to git
- Use strong passwords for databases
- Run behind reverse proxy in production
- Enable rate limiting
- Use HTTPS in production

## 📈 Performance Tuning

```bash
# Increase workers for production
uvicorn main:app --workers 4

# Adjust indexing batch size
RAG_CHUNK_SIZE=1000

# Enable caching
CACHE_QUERY_RESULTS=True
CACHE_TTL_SECONDS=3600
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

- GitHub Issues: [Report bugs](your-repo/issues)
- Email: support@yourcompany.com
- Documentation: [Full docs](your-docs-url)

## 🎓 Learn More

- [Anthropic Claude API](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [Neo4j Graph Database](https://neo4j.com/docs/)

---

**Made with ❤️ using Claude, FastAPI, and modern AI technology**
