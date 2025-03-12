"""
Documentation routes for the FastAPI frontend.
Provides API endpoints for documentation.
"""
from fastapi import APIRouter, Request, Depends
from typing import Dict, Any, List

from ...models.responses import DocumentationResponse, DocumentationExample
from ...core.config import PROJECT_NAME, VERSION, DESCRIPTION, API_V1_PREFIX
from ..dependencies import get_request_metadata

router = APIRouter()

@router.get("/docs", response_model=DocumentationResponse)
async def get_documentation(
    request: Request,
    metadata: Dict[str, Any] = Depends(get_request_metadata),
) -> DocumentationResponse:
    """
    Get API documentation.
    
    Args:
        request (Request): The FastAPI request object
        metadata (Dict[str, Any]): Request metadata
        
    Returns:
        DocumentationResponse: The documentation response
    """
    # Define API endpoints
    endpoints = [
        {
            "path": f"{API_V1_PREFIX}/extract",
            "method": "POST",
            "description": "Extract fields from text",
            "requires_auth": True,
            "request_body": "ExtractRequest",
            "response_body": "ExtractResponse",
        },
        {
            "path": f"{API_V1_PREFIX}/extract/file",
            "method": "POST",
            "description": "Extract fields from an uploaded file",
            "requires_auth": True,
            "request_body": "multipart/form-data",
            "response_body": "ExtractResponse",
        },
        {
            "path": f"{API_V1_PREFIX}/health",
            "method": "GET",
            "description": "Check the health of the service",
            "requires_auth": False,
            "response_body": "HealthResponse",
        },
        {
            "path": f"{API_V1_PREFIX}/docs",
            "method": "GET",
            "description": "Get API documentation",
            "requires_auth": False,
            "response_body": "DocumentationResponse",
        },
    ]
    
    # Define examples
    examples = [
        DocumentationExample(
            title="Extract fields from an uploaded file",
            description="Extract first name, last name, and birthdate from an uploaded file",
            request={
                "file": "(binary file data)",
                "fields": "first_name,last_name,birthdate",
                "chunking_method": "words",
                "chunk_size": 500,
                "chunk_overlap": 100,
                "max_workers": 5,
                "output_format": "json",
            },
            response={
                "status": "success",
                "request_id": "f8d7e6c5-b4a3-42d1-9f0e-8c7b6a5d4e3c",
                "processing_time": 1.25,
                "extracted_fields": {
                    "first_name": "John",
                    "last_name": "Smith",
                    "birthdate": "09/02/1949",
                },
                "metrics": {
                    "chunks_processed": 4,
                    "llm_calls": 4,
                    "processing_time": 1.25,
                },
            },
        ),
        DocumentationExample(
            title="Extract fields from text",
            description="Extract first name, last name, and birthdate from text",
            request={
                "text": "Patient: John Smith, DOB: 09/02/1949...",
                "fields": ["first_name", "last_name", "birthdate"],
                "chunking_method": "words",
                "chunk_size": 500,
                "chunk_overlap": 100,
                "max_workers": 5,
                "output_format": "json",
            },
            response={
                "status": "success",
                "request_id": "f8d7e6c5-b4a3-42d1-9f0e-8c7b6a5d4e3c",
                "processing_time": 1.25,
                "extracted_fields": {
                    "first_name": "John",
                    "last_name": "Smith",
                    "birthdate": "09/02/1949",
                },
                "metrics": {
                    "chunks_processed": 4,
                    "llm_calls": 4,
                    "processing_time": 1.25,
                },
            },
        ),
        DocumentationExample(
            title="Extract medical history",
            description="Extract medical history from text",
            request={
                "text": "Patient: John Smith, Medical History: Type 2 Diabetes (diagnosed March 15 2010), Hypertension since 2005...",
                "fields": ["medical_history"],
                "chunking_method": "words",
                "chunk_size": 500,
                "chunk_overlap": 100,
                "max_workers": 5,
                "output_format": "json",
            },
            response={
                "status": "success",
                "request_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
                "processing_time": 1.5,
                "extracted_fields": {
                    "medical_history": [
                        "Type 2 Diabetes (diagnosed 15/03/2010)",
                        "Hypertension since 2005",
                    ],
                },
                "metrics": {
                    "chunks_processed": 4,
                    "llm_calls": 4,
                    "processing_time": 1.5,
                },
            },
        ),
    ]
    
    # Create response
    response = DocumentationResponse(
        service_name=PROJECT_NAME,
        version=VERSION,
        description=DESCRIPTION,
        endpoints=endpoints,
        examples=examples,
    )
    
    return response
