"""
Health check routes for the FastAPI frontend.
Provides API endpoints for health checks.
"""
import time
import os
import sys
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from typing import Dict, Any

# Add the parent directory to the path so we can import from the src module
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from src.api.dudoxx_client import DudoxxClient

from ...models.responses import HealthResponse
from ...core.config import VERSION, API_KEY, BASE_URL
from ..dependencies import get_request_metadata, get_processing_time

# Start time of the service
START_TIME = time.time()

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(
    request: Request,
    metadata: Dict[str, Any] = Depends(get_request_metadata),
) -> HealthResponse:
    """
    Check the health of the service.
    
    Args:
        request (Request): The FastAPI request object
        metadata (Dict[str, Any]): Request metadata
        
    Returns:
        HealthResponse: The health check response
    """
    # Calculate uptime
    uptime = time.time() - START_TIME
    
    # Check LLM API status
    llm_status = "ok"
    try:
        # Initialize the DUDOXX client
        client = DudoxxClient(api_key=API_KEY, base_url=BASE_URL)
        
        # Make a simple API call to check if the LLM API is working
        client.extract_fields(
            text="This is a test.",
            fields=["test"],
            system_prompt="This is a test. Return {\"test\": \"ok\"}.",
        )
    except Exception as e:
        llm_status = f"error: {str(e)}"
    
    # Create response
    response = HealthResponse(
        status="ok",
        version=VERSION,
        uptime=uptime,
        llm_status=llm_status,
    )
    
    return response
