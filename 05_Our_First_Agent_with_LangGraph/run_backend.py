#!/usr/bin/env python3
"""
Script to run the FastAPI backend server from the project root.
This ensures proper Python path configuration.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

if __name__ == "__main__":
    import uvicorn
    
    # Change to backend directory for proper working directory
    os.chdir(backend_path)
    
    print("🚀 Starting Chess.com LangGraph Agent API...")
    print(f"📁 Working directory: {os.getcwd()}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."]
    ) 