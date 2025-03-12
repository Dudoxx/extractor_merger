"""
Response models for the FastAPI frontend.
Defines Pydantic models for API responses.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class Metrics(BaseModel):
    """Metrics model for extraction metrics."""
    chunks_processed: int = Field(..., description="Number of chunks processed")
    total_tokens: Optional[int] = Field(None, description="Total tokens processed")
    llm_calls: int = Field(..., description="Number of LLM API calls")
    processing_time: float = Field(..., description="Total processing time in seconds")

class ExtractResponse(BaseModel):
    """Response model for field extraction."""
    status: str = Field("success", description="Response status")
    request_id: str = Field(..., description="Unique request ID")
    processing_time: float = Field(..., description="Total processing time in seconds")
    extracted_fields: Dict[str, Any] = Field(..., description="Extracted fields and values")
    metrics: Optional[Metrics] = Field(None, description="Extraction metrics")

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field("ok", description="Service status")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Service uptime in seconds")
    llm_status: str = Field(..., description="LLM API status")

class DocumentationExample(BaseModel):
    """Model for documentation examples."""
    title: str = Field(..., description="Example title")
    description: str = Field(..., description="Example description")
    request: Dict[str, Any] = Field(..., description="Example request")
    response: Dict[str, Any] = Field(..., description="Example response")

class DocumentationResponse(BaseModel):
    """Response model for documentation."""
    service_name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    description: str = Field(..., description="Service description")
    endpoints: List[Dict[str, Any]] = Field(..., description="API endpoints")
    examples: List[DocumentationExample] = Field(..., description="Usage examples")
