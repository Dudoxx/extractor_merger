"""
Dependencies for the FastAPI frontend.
Provides dependency injection for the API routes.
"""
import time
from typing import Dict, Any, Optional

from fastapi import Request, Depends

from ..core.security import validate_api_key
from ..core.logging import get_request_id, log_request

async def get_token(token: str = Depends(validate_api_key)) -> str:
    """
    Get the validated API token.
    
    Args:
        token (str): The validated API token
        
    Returns:
        str: The validated API token
    """
    return token

async def get_request_metadata(request: Request) -> Dict[str, Any]:
    """
    Get metadata for the current request.
    
    Args:
        request (Request): The FastAPI request object
        
    Returns:
        Dict[str, Any]: Request metadata
    """
    # Generate a request ID
    request_id = get_request_id()
    
    # Store the request start time
    request.state.start_time = time.time()
    
    # Store the request ID
    request.state.request_id = request_id
    
    # Log the request
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                body = await request.json()
            except Exception:
                body = None
        elif "multipart/form-data" in content_type:
            body = {"form_data": "File upload request"}
    
    log_request(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        params=dict(request.query_params),
        body=body,
    )
    
    return {
        "request_id": request_id,
        "start_time": request.state.start_time,
    }

def get_processing_time(request: Request) -> float:
    """
    Calculate the processing time for the current request.
    
    Args:
        request (Request): The FastAPI request object
        
    Returns:
        float: The processing time in seconds
    """
    start_time = getattr(request.state, "start_time", time.time())
    return time.time() - start_time
