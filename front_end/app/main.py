"""
Main entry point for the FastAPI frontend.
Initializes the FastAPI application and includes all routes.
"""
import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

# Add the parent directory to the path so we can import from the src module
sys.path.append(str(Path(__file__).parent.parent.parent))

from .api.routes import extraction, health, docs
from .core.config import (
    PROJECT_NAME,
    VERSION,
    DESCRIPTION,
    API_V1_PREFIX,
    ALLOWED_ORIGINS,
    ALLOWED_METHODS,
    ALLOWED_HEADERS,
)
from .core.errors import ExtractorError, create_error_response
from .core.logging import logger, log_error, get_request_id

# Create FastAPI application
app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description=DESCRIPTION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    allow_credentials=True,
)

# Include routers
app.include_router(extraction.router, prefix=API_V1_PREFIX)
app.include_router(health.router, prefix=API_V1_PREFIX)
app.include_router(docs.router, prefix=API_V1_PREFIX)

# Exception handlers
@app.exception_handler(ExtractorError)
async def extractor_error_handler(request: Request, exc: ExtractorError):
    """
    Handle ExtractorError exceptions.
    
    Args:
        request (Request): The FastAPI request object
        exc (ExtractorError): The exception
        
    Returns:
        JSONResponse: The error response
    """
    # Get request ID from state or generate a new one
    request_id = getattr(request.state, "request_id", get_request_id())
    
    # Log the error
    log_error(request_id, exc, exc.status_code)
    
    # Create error response
    error_response = create_error_response(exc, request_id)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(),
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """
    Handle RequestValidationError exceptions.
    
    Args:
        request (Request): The FastAPI request object
        exc (RequestValidationError): The exception
        
    Returns:
        JSONResponse: The error response
    """
    # Get request ID from state or generate a new one
    request_id = getattr(request.state, "request_id", get_request_id())
    
    # Log the error
    log_error(request_id, exc, status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    # Create error response
    error_response = {
        "status": "error",
        "request_id": request_id,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid request parameters",
            "details": str(exc),
        },
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    
    Args:
        request (Request): The FastAPI request object
        exc (Exception): The exception
        
    Returns:
        JSONResponse: The error response
    """
    # Get request ID from state or generate a new one
    request_id = getattr(request.state, "request_id", get_request_id())
    
    # Log the error
    log_error(request_id, exc, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Create error response
    error_response = {
        "status": "error",
        "request_id": request_id,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An internal error occurred",
            "details": str(exc),
        },
    }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    """
    logger.info(f"Starting {PROJECT_NAME} v{VERSION}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    """
    logger.info(f"Shutting down {PROJECT_NAME} v{VERSION}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
