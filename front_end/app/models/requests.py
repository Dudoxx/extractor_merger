"""
Request models for the FastAPI frontend.
Defines Pydantic models for API requests.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator

class ExtractRequest(BaseModel):
    """Request model for field extraction."""
    text: str = Field(..., description="The input text to extract fields from")
    fields: List[str] = Field(..., description="List of field names to extract")
    chunking_method: Optional[str] = Field(
        "words", 
        description="Method for chunking text (words or paragraphs)"
    )
    chunk_size: Optional[int] = Field(
        None, 
        description="Size of each chunk in words"
    )
    chunk_overlap: Optional[int] = Field(
        None, 
        description="Overlap between chunks in words"
    )
    max_workers: Optional[int] = Field(
        None, 
        description="Maximum number of worker threads"
    )
    output_format: Optional[str] = Field(
        "json", 
        description="Output format (json, text, md, csv, html)"
    )
    system_prompt: Optional[str] = Field(
        None, 
        description="System prompt to use"
    )
    date_fields: Optional[List[str]] = Field(
        None, 
        description="List of date fields to normalize"
    )
    date_format: Optional[str] = Field(
        None, 
        description="Format for date fields"
    )
    unknown_value: Optional[str] = Field(
        None, 
        description="Value to use for unknown fields"
    )
    
    @validator('chunking_method')
    def validate_chunking_method(cls, v):
        """Validate the chunking method."""
        if v not in ["words", "paragraphs"]:
            raise ValueError("Chunking method must be 'words' or 'paragraphs'")
        return v
    
    @validator('output_format')
    def validate_output_format(cls, v):
        """Validate the output format."""
        if v not in ["json", "text", "md", "csv", "html"]:
            raise ValueError("Output format must be 'json', 'text', 'md', 'csv', or 'html'")
        return v
    
    @validator('chunk_size')
    def validate_chunk_size(cls, v):
        """Validate the chunk size."""
        if v is not None and v <= 0:
            raise ValueError("Chunk size must be positive")
        return v
    
    @validator('chunk_overlap')
    def validate_chunk_overlap(cls, v):
        """Validate the chunk overlap."""
        if v is not None and v < 0:
            raise ValueError("Chunk overlap must be non-negative")
        return v
    
    @validator('max_workers')
    def validate_max_workers(cls, v):
        """Validate the max workers."""
        if v is not None and v <= 0:
            raise ValueError("Max workers must be positive")
        return v
    
    @validator('text')
    def validate_text(cls, v):
        """Validate the text."""
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v
    
    @validator('fields')
    def validate_fields(cls, v):
        """Validate the fields."""
        if not v:
            raise ValueError("Fields cannot be empty")
        return v

class ExtractFileRequest(BaseModel):
    """Request model for field extraction from file."""
    fields: List[str] = Field(..., description="List of field names to extract")
    chunking_method: Optional[str] = Field(
        "words", 
        description="Method for chunking text (words or paragraphs)"
    )
    chunk_size: Optional[int] = Field(
        None, 
        description="Size of each chunk in words"
    )
    chunk_overlap: Optional[int] = Field(
        None, 
        description="Overlap between chunks in words"
    )
    max_workers: Optional[int] = Field(
        None, 
        description="Maximum number of worker threads"
    )
    output_format: Optional[str] = Field(
        "json", 
        description="Output format (json, text, md, csv, html)"
    )
    system_prompt: Optional[str] = Field(
        None, 
        description="System prompt to use"
    )
    date_fields: Optional[List[str]] = Field(
        None, 
        description="List of date fields to normalize"
    )
    date_format: Optional[str] = Field(
        None, 
        description="Format for date fields"
    )
    unknown_value: Optional[str] = Field(
        None, 
        description="Value to use for unknown fields"
    )
    
    @validator('chunking_method')
    def validate_chunking_method(cls, v):
        """Validate the chunking method."""
        if v not in ["words", "paragraphs"]:
            raise ValueError("Chunking method must be 'words' or 'paragraphs'")
        return v
    
    @validator('output_format')
    def validate_output_format(cls, v):
        """Validate the output format."""
        if v not in ["json", "text", "md", "csv", "html"]:
            raise ValueError("Output format must be 'json', 'text', 'md', 'csv', or 'html'")
        return v
    
    @validator('chunk_size')
    def validate_chunk_size(cls, v):
        """Validate the chunk size."""
        if v is not None and v <= 0:
            raise ValueError("Chunk size must be positive")
        return v
    
    @validator('chunk_overlap')
    def validate_chunk_overlap(cls, v):
        """Validate the chunk overlap."""
        if v is not None and v < 0:
            raise ValueError("Chunk overlap must be non-negative")
        return v
    
    @validator('max_workers')
    def validate_max_workers(cls, v):
        """Validate the max workers."""
        if v is not None and v <= 0:
            raise ValueError("Max workers must be positive")
        return v
    
    @validator('fields')
    def validate_fields(cls, v):
        """Validate the fields."""
        if not v:
            raise ValueError("Fields cannot be empty")
        return v
