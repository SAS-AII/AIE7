# Chess.com LangGraph Agent API

Production-ready FastAPI backend for chess analysis using LangGraph multi-agent system with Chess.com API integration.

## Architecture Overview

This backend implements a sophisticated chess analysis system using LangGraph to orchestrate multiple specialized tools:

### LangGraph Workflow

```
┌─────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Request   │───▶│  Agent Node     │───▶│  Tool Execution  │
│  (Username/ │    │ (GPT-4 + Tools) │    │                  │
│    PGN)     │    └─────────────────┘    │ ┌──────────────┐ │
└─────────────┘           │               │ │ PlayerTool   │ │
                          │               │ │ GameAnalyzer │ │
        ┌─────────────────┘               │ │ RatingTracker│ │
        │                                 │ └──────────────┘ │
        ▼                                 └──────────────────┘
┌─────────────┐                                   │
│ Should      │                                   │
│ Continue?   │◄──────────────────────────────────┘
│             │
└─────┬───┬───┘
      │   │
   ┌──▼─┐ └─▶ END
   │Tool│
   │Call│
   └────┘
```

### Multi-Agent System

The system uses three specialized LangChain tools:

1. **ChessComPlayerTool**: Fetches player profiles, ratings, and statistics
2. **ChessComGameAnalyzerTool**: Downloads and analyzes Chess.com games or provided PGN
3. **ChessComRatingTrackerTool**: Tracks rating trends and opening repertoire

### Component Architecture

```
backend/
├── main.py                 # FastAPI application with CORS
├── routers/
│   ├── health.py          # Health check endpoint
│   └── chess_analysis.py  # Chess analysis endpoints
├── agents/
│   ├── tools.py           # LangChain tools for Chess.com API
│   └── graph.py           # LangGraph workflow orchestration
├── models.py              # Pydantic request/response schemas
├── utils/
│   ├── logging.py         # Loguru-based logger
│   ├── chess_parsers.py   # PGN parsing utilities
│   └── qdrant_client.py   # Vector database integration
└── gunicorn_conf.py       # Production server configuration
```

## API Endpoints

### Health Check
- `GET /health` - Returns system status

### Chess Analysis
All endpoints accept API keys in the request body for security:

#### 1. Player Analysis
```bash
POST /analyze/player
Content-Type: application/json

{
  "username": "hikaru",
  "openai_key": "sk-...",
  "langsmith_key": "...",
  "tavily_key": "...",
  "qdrant_api_key": "..." (optional)
}
```

#### 2. PGN Game Analysis
```bash
POST /analyze/pgn
Content-Type: application/json

{
  "pgn": "1. e4 e5 2. Nf3 Nc6...",
  "openai_key": "sk-...",
  "langsmith_key": "...",
  "tavily_key": "...",
  "qdrant_api_key": "..." (optional)
}
```

#### 3. Recent Games Analysis
```bash
POST /analyze/recent-games
Content-Type: application/json

{
  "username": "hikaru",
  "num_games": 10,
  "openai_key": "sk-...",
  "langsmith_key": "...",
  "tavily_key": "..."
}
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Required API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
LANGSMITH_API_KEY=your-langsmith-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here

# Optional: Qdrant Vector Database
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_URL=https://your-cluster.qdrant.io

# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Chess-Agent-Production
```

## Local Development

### Installation
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Or using uv from project root
uv sync
```

### Running the Server
```bash
# Development server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
cd backend
gunicorn -c gunicorn_conf.py main:app
```

## Production Deployment

### Vercel Deployment
```bash
# Deploy to Vercel
vercel deploy

# Environment variables in Vercel dashboard:
# - OPENAI_API_KEY
# - LANGSMITH_API_KEY  
# - TAVILY_API_KEY
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn_conf.py", "main:app"]
```

## LangGraph Agent Workflow

The chess analysis follows this LangGraph pattern:

1. **State Initialization**: User request creates `ChessAgentState` with messages
2. **Agent Node**: GPT-4 model processes request and determines which tools to call
3. **Tool Execution**: Relevant chess tools fetch data from Chess.com API
4. **Response Synthesis**: Agent compiles tool results into comprehensive analysis
5. **Conditional Flow**: System continues until analysis is complete

### Example Tool Chain

For player analysis:
```
Request → Agent → ChessComPlayerTool → ChessComRatingTrackerTool → Agent → Response
```

For PGN analysis:
```
Request → Agent → ChessComGameAnalyzerTool → Agent → Response
```

## Features

### Chess Analysis Capabilities
- **Player Profiles**: Complete player statistics and ratings across time controls
- **Game Analysis**: PGN parsing with opening classification and tactical analysis
- **Rating Trends**: Historical performance and opening repertoire analysis
- **Vector Storage**: Optional game storage in Qdrant for similarity search

### Production Features
- **LangSmith Tracing**: Full observability of agent workflows
- **Structured Logging**: Loguru-based logging with rotation
- **Input Validation**: Pydantic models for all requests/responses
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **CORS Support**: Permissive CORS for public API usage

### Performance Optimizations
- **Gunicorn Workers**: Calculated as `(CPU * 2) + 1`
- **Connection Pooling**: HTTP client reuse for Chess.com API calls
- **Async Processing**: Full async/await support throughout
- **Memory Management**: In-memory PGN processing for Vercel compatibility

## Testing

### Example Requests

Test player analysis:
```bash
curl -X POST "http://localhost:8000/analyze/player" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "hikaru",
    "openai_key": "sk-...",
    "langsmith_key": "...",
    "tavily_key": "..."
  }'
```

Test PGN analysis:
```bash
curl -X POST "http://localhost:8000/analyze/pgn" \
  -H "Content-Type: application/json" \
  -d '{
    "pgn": "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6",
    "openai_key": "sk-...",
    "langsmith_key": "...",
    "tavily_key": "..."
  }'
```

## Monitoring

- **Health Endpoint**: `/health` for uptime monitoring
- **LangSmith Dashboard**: Full tracing of agent workflows
- **Structured Logs**: JSON logs with request correlation IDs
- **Error Tracking**: Detailed error logs with stack traces

## Dependencies

- **FastAPI**: Modern, fast web framework
- **LangGraph**: Agent workflow orchestration  
- **LangSmith**: Observability and tracing
- **python-chess**: PGN parsing and game analysis
- **Qdrant**: Vector database for game similarity
- **Gunicorn**: Production WSGI server 