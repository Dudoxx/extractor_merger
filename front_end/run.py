#!/usr/bin/env python3
"""
Run script for the FastAPI frontend.
Starts the FastAPI application using uvicorn with multiple workers for improved concurrency.
"""
import uvicorn
import multiprocessing
import argparse

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the FastAPI application with multiple workers")
    parser.add_argument("--workers", type=int, default=multiprocessing.cpu_count(), 
                        help="Number of worker processes (default: number of CPU cores)")
    parser.add_argument("--host", type=str, default="0.0.0.0", 
                        help="Host to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, 
                        help="Port to bind the server to (default: 8000)")
    parser.add_argument("--reload", action="store_true", 
                        help="Enable auto-reload on code changes (only works with a single worker)")
    args = parser.parse_args()
    
    # If reload is enabled, we can only use a single worker
    if args.reload:
        workers = 1
        print(f"Auto-reload enabled, using a single worker")
    else:
        workers = args.workers
        print(f"Using {workers} worker processes")
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=workers,
    )
