"""
Extraction routes for the FastAPI frontend.
Provides API endpoints for field extraction.
"""
from fastapi import APIRouter, Depends, Request, File, UploadFile, Form
from typing import Dict, Any, List, Optional
import json

from ...models.requests import ExtractRequest, ExtractFileRequest
from ...models.responses import ExtractResponse, Metrics
from ...services.extractor import ExtractorService
from ...core.errors import create_error_response, ExtractorError
from ...core.logging import log_response, log_error
from ..dependencies import get_token, get_request_metadata, get_processing_time

router = APIRouter()

@router.post("/extract/file", response_model=ExtractResponse)
async def extract_fields_from_file(
    request: Request,
    file: UploadFile = File(...),
    fields: str = Form(...),
    chunking_method: Optional[str] = Form("words"),
    chunk_size: Optional[int] = Form(None),
    chunk_overlap: Optional[int] = Form(None),
    max_workers: Optional[int] = Form(None),
    output_format: Optional[str] = Form("json"),
    system_prompt: Optional[str] = Form(None),
    date_fields: Optional[str] = Form(None),
    date_format: Optional[str] = Form(None),
    unknown_value: Optional[str] = Form(None),
    token: str = Depends(get_token),
    metadata: Dict[str, Any] = Depends(get_request_metadata),
) -> ExtractResponse:
    """
    Extract fields from an uploaded file.
    
    Args:
        request (Request): The FastAPI request object
        file (UploadFile): The uploaded file
        fields (str): Comma-separated list of field names to extract
        chunking_method (str, optional): Method for chunking text. Defaults to "words".
        chunk_size (int, optional): Size of each chunk in words. Defaults to None.
        chunk_overlap (int, optional): Overlap between chunks in words. Defaults to None.
        max_workers (int, optional): Maximum number of worker threads. Defaults to None.
        output_format (str, optional): Output format. Defaults to "json".
        system_prompt (str, optional): System prompt to use. Defaults to None.
        date_fields (str, optional): Comma-separated list of date fields to normalize. Defaults to None.
        date_format (str, optional): Format for date fields. Defaults to None.
        unknown_value (str, optional): Value to use for unknown fields. Defaults to None.
        token (str): The validated API token
        metadata (Dict[str, Any]): Request metadata
        
    Returns:
        ExtractResponse: The extraction response
    """
    try:
        # Parse fields
        fields_list = [field.strip() for field in fields.split(",")]
        
        # Parse date fields if provided
        date_fields_list = None
        if date_fields:
            date_fields_list = [field.strip() for field in date_fields.split(",")]
        
        # Extract fields
        result = await ExtractorService.extract_fields_from_file(
            file=file.file,
            fields=fields_list,
            chunking_method=chunking_method,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            output_format=output_format,
            system_prompt=system_prompt,
            date_fields=date_fields_list,
            date_format=date_format,
            unknown_value=unknown_value,
        )
        
        # Calculate processing time
        processing_time = get_processing_time(request)
        
        # Create response
        response = ExtractResponse(
            status="success",
            request_id=metadata["request_id"],
            processing_time=processing_time,
            extracted_fields=result["extracted_fields"],
            metrics=Metrics(
                chunks_processed=result["metrics"]["chunks_processed"],
                llm_calls=result["metrics"]["llm_calls"],
                processing_time=result["metrics"]["processing_time"],
            ),
        )
        
        # Log response
        log_response(
            request_id=metadata["request_id"],
            status_code=200,
            response_time=processing_time,
            response_body=response.dict(),
        )
        
        return response
    
    except ExtractorError as e:
        # Calculate processing time
        processing_time = get_processing_time(request)
        
        # Log error
        log_error(
            request_id=metadata["request_id"],
            error=e,
            status_code=e.status_code,
        )
        
        # Create error response
        error_response = create_error_response(
            exception=e,
            request_id=metadata["request_id"],
        )
        
        # Log response
        log_response(
            request_id=metadata["request_id"],
            status_code=e.status_code,
            response_time=processing_time,
            response_body=error_response.dict(),
        )
        
        # Re-raise the exception
        raise e

@router.post("/extract", response_model=ExtractResponse)
async def extract_fields(
    request: Request,
    extract_request: ExtractRequest,
    token: str = Depends(get_token),
    metadata: Dict[str, Any] = Depends(get_request_metadata),
) -> ExtractResponse:
    """
    Extract fields from text.
    
    Args:
        request (Request): The FastAPI request object
        extract_request (ExtractRequest): The extraction request
        token (str): The validated API token
        metadata (Dict[str, Any]): Request metadata
        
    Returns:
        ExtractResponse: The extraction response
    """
    try:
        # Extract fields
        result = await ExtractorService.extract_fields(
            text=extract_request.text,
            fields=extract_request.fields,
            chunking_method=extract_request.chunking_method,
            chunk_size=extract_request.chunk_size,
            chunk_overlap=extract_request.chunk_overlap,
            max_workers=extract_request.max_workers,
            output_format=extract_request.output_format,
            system_prompt=extract_request.system_prompt,
            date_fields=extract_request.date_fields,
            date_format=extract_request.date_format,
            unknown_value=extract_request.unknown_value,
        )
        
        # Calculate processing time
        processing_time = get_processing_time(request)
        
        # Create response
        response = ExtractResponse(
            status="success",
            request_id=metadata["request_id"],
            processing_time=processing_time,
            extracted_fields=result["extracted_fields"],
            metrics=Metrics(
                chunks_processed=result["metrics"]["chunks_processed"],
                llm_calls=result["metrics"]["llm_calls"],
                processing_time=result["metrics"]["processing_time"],
            ),
        )
        
        # Log response
        log_response(
            request_id=metadata["request_id"],
            status_code=200,
            response_time=processing_time,
            response_body=response.dict(),
        )
        
        return response
    
    except ExtractorError as e:
        # Calculate processing time
        processing_time = get_processing_time(request)
        
        # Log error
        log_error(
            request_id=metadata["request_id"],
            error=e,
            status_code=e.status_code,
        )
        
        # Create error response
        error_response = create_error_response(
            exception=e,
            request_id=metadata["request_id"],
        )
        
        # Log response
        log_response(
            request_id=metadata["request_id"],
            status_code=e.status_code,
            response_time=processing_time,
            response_body=error_response.dict(),
        )
        
        # Re-raise the exception
        raise e
