"""
Logging configuration for the FastAPI frontend.
Provides logging utilities for the API.
"""
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .config import LOG_LEVEL, DETAILED_LOGGING

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            logs_dir / f"dudoxx_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
    ],
)

# Create logger
logger = logging.getLogger("dudoxx_api")

def get_request_id() -> str:
    """
    Generate a unique request ID.
    
    Returns:
        str: The request ID
    """
    return str(uuid.uuid4())

def log_request(
    request_id: str,
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log an API request.
    
    Args:
        request_id (str): The request ID
        method (str): The HTTP method
        path (str): The request path
        params (dict, optional): The query parameters
        body (dict, optional): The request body
    """
    log_data = {
        "request_id": request_id,
        "method": method,
        "path": path,
    }
    
    if params:
        log_data["params"] = params
    
    if body and DETAILED_LOGGING.lower() == "true":
        # Redact sensitive information
        if "text" in body:
            # Truncate long text
            body["text"] = body["text"][:100] + "..." if len(body["text"]) > 100 else body["text"]
        
        log_data["body"] = body
    
    logger.info(f"Request: {log_data}")

def log_response(
    request_id: str,
    status_code: int,
    response_time: float,
    response_body: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log an API response.
    
    Args:
        request_id (str): The request ID
        status_code (int): The HTTP status code
        response_time (float): The response time in seconds
        response_body (dict, optional): The response body
    """
    log_data = {
        "request_id": request_id,
        "status_code": status_code,
        "response_time": f"{response_time:.2f}s",
    }
    
    if response_body and DETAILED_LOGGING.lower() == "true":
        # Redact sensitive information
        if "extracted_fields" in response_body:
            log_data["extracted_fields"] = list(response_body["extracted_fields"].keys())
        
        if "metrics" in response_body:
            log_data["metrics"] = response_body["metrics"]
    
    logger.info(f"Response: {log_data}")

def log_error(
    request_id: str,
    error: Exception,
    status_code: Optional[int] = None,
) -> None:
    """
    Log an API error.
    
    Args:
        request_id (str): The request ID
        error (Exception): The error
        status_code (int, optional): The HTTP status code
    """
    log_data = {
        "request_id": request_id,
        "error": str(error),
        "error_type": type(error).__name__,
    }
    
    if status_code:
        log_data["status_code"] = status_code
    
    logger.error(f"Error: {log_data}", exc_info=True)
