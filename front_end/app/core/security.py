"""
Security utilities for the FastAPI frontend.
Provides functions for token validation and authentication.
"""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from .config import API_TOKEN

# Define the API key header
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def validate_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """
    Validate the API key from the Authorization header.
    
    Args:
        api_key_header (str): The API key from the Authorization header
        
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: If the API key is invalid or missing
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if the header starts with "Bearer "
    if not api_key_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format. Use 'Bearer {token}'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract the token
    token = api_key_header.replace("Bearer ", "")
    
    # Validate the token
    if token != API_TOKEN:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token
