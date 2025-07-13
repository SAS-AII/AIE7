# Chess.com LangGraph Agent API

Production-ready FastAPI backend for chess analysis using LangGraph multi-agent system with Chess.com API integration.

## Environment Variables Configuration

### Local Development (.env file)

Create a `.env` file in the backend directory with the following variables:

```env
# Required API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
LANGSMITH_API_KEY=lsv2_pt_your-langsmith-api-key-here  
TAVILY_API_KEY=tvly-your-tavily-api-key-here

# Optional: Qdrant Vector Database
# If not provided, will use request parameters instead
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_URL=https://your-cluster.qdrant.io

# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Chess-Agent-Production
```

### Vercel Deployment

In your Vercel dashboard, set these environment variables:
- `QDRANT_API_KEY` (your Qdrant API key)
- `QDRANT_URL` (optional, defaults to https://cloud.qdrant.io)

### Qdrant Configuration Priority

The system checks for Qdrant configuration in this order:
1. **Environment variables** (QDRANT_API_KEY, QDRANT_URL)
2. **Request parameters** (qdrant_api_key, qdrant_url in JSON body)
3. **Graceful fallback** (continues without vector storage if neither available)

This ensures seamless operation whether deployed on Vercel (using env vars) or testing locally with different API keys.

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
All endpoints automatically detect Qdrant availability from environment variables:

#### 1. Player Analysis
```bash
POST /analyze/player
Content-Type: application/json

{
  "username": "hikaru",
  "openai_key": "sk-...",
  "langsmith_key": "...",
  "tavily_key": "...",
  "qdrant_api_key": "..." (optional if QDRANT_API_KEY env var is set)
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
  "qdrant_api_key": "..." (optional if QDRANT_API_KEY env var is set)
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

All endpoints return a `qdrant_available` field in the response indicating whether vector storage is active.

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

# Set environment variables in Vercel dashboard:
# - QDRANT_API_KEY (for vector storage)
# - QDRANT_URL (optional, defaults to cloud.qdrant.io)
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
- **Environment Detection**: Automatic Qdrant configuration from env vars or request params

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

### Testing with Qdrant

If you have a Qdrant API key, you can test vector storage:

**Option 1: Environment Variables (Recommended)**
```bash
# Set in .env file
export QDRANT_API_KEY=your-key-here
export QDRANT_URL=https://your-cluster.qdrant.io

# Then make requests normally (no need to include qdrant_api_key in JSON)
curl -X POST "http://localhost:8000/analyze/pgn" \
  -H "Content-Type: application/json" \
  -d '{
    "pgn": "1. e4 e5...",
    "openai_key": "sk-...",
    "langsmith_key": "...",
    "tavily_key": "..."
  }'
```

**Option 2: Request Parameters**
```bash
curl -X POST "http://localhost:8000/analyze/pgn" \
  -H "Content-Type: application/json" \
  -d '{
    "pgn": "1. e4 e5...",
    "openai_key": "sk-...",
    "langsmith_key": "...",
    "tavily_key": "...",
    "qdrant_api_key": "your-key-here",
    "qdrant_url": "https://your-cluster.qdrant.io"
  }'
```

## Monitoring

- **Health Endpoint**: `/health` for uptime monitoring
- **LangSmith Dashboard**: Full tracing of agent workflows
- **Structured Logs**: JSON logs with request correlation IDs
- **Error Tracking**: Detailed error logs with stack traces
- **Qdrant Status**: Automatic logging of vector database availability

## Dependencies

- **FastAPI**: Modern, fast web framework
- **LangGraph**: Agent workflow orchestration  
- **LangSmith**: Observability and tracing
- **python-chess**: PGN parsing and game analysis
- **Qdrant**: Vector database for game similarity
- **Gunicorn**: Production WSGI server
- **python-dotenv**: Environment variable management 