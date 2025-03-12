"""
Error handling utilities for the FastAPI frontend.
Provides custom exception classes and error responses.
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = "error"
    request_id: Optional[str] = None
    error: Dict[str, Any]

class ExtractorError(HTTPException):
    """Base exception for extractor errors."""
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = code
        self.error_message = message
        self.error_details = details
        super().__init__(status_code=status_code, detail=message, headers=headers)

class InvalidInputError(ExtractorError):
    """Exception for invalid input errors."""
    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_INPUT",
            message=message,
            details=details,
            headers=headers,
        )

class ProcessingError(ExtractorError):
    """Exception for processing errors."""
    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="PROCESSING_ERROR",
            message=message,
            details=details,
            headers=headers,
        )

class LLMError(ExtractorError):
    """Exception for LLM API errors."""
    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="LLM_ERROR",
            message=message,
            details=details,
            headers=headers,
        )

def create_error_response(
    exception: ExtractorError,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """
    Create an error response from an exception.
    
    Args:
        exception (ExtractorError): The exception
        request_id (str, optional): The request ID
        
    Returns:
        ErrorResponse: The error response
    """
    return ErrorResponse(
        status="error",
        request_id=request_id,
        error={
            "code": exception.error_code,
            "message": exception.error_message,
            "details": exception.error_details,
        },
    )
