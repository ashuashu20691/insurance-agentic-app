#!/usr/bin/env python3
"""
Run the FastAPI backend server
"""
import uvicorn
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_database, seed_sample_policies

if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    init_database()
    seed_sample_policies()
    print("Database initialized with sample policies.")
    
    # Run server
    print("Starting API server on http://localhost:8000")
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
