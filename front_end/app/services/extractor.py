"""
Extractor service for the FastAPI frontend.
Provides a service for extracting fields from text using the DUDOXX field extraction system.
"""
import time
import sys
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, BinaryIO

# Add the parent directory to the path so we can import from the src module
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.chunking.text_chunker import chunk_text, chunk_text_by_paragraphs
from src.extraction.field_extractor import extract_fields_from_chunk
from src.processing.parallel_processor import process_chunks_parallel
from src.merging.result_merger import merge_results
from src.utils.validators import validate_and_normalize

from ..core.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    MAX_THREADS,
    DEFAULT_SYSTEM_PROMPT,
    OUTPUT_FORMAT,
    UNKNOWN_VALUE,
    DATE_FORMAT,
)
from ..core.errors import InvalidInputError, ProcessingError, LLMError
from ..core.logging import logger

class ExtractorService:
    """Service for extracting fields from text."""
    
    @staticmethod
    async def extract_fields_from_file(
        file: BinaryIO,
        fields: List[str],
        chunking_method: str = "words",
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        max_workers: Optional[int] = None,
        output_format: Optional[str] = None,
        system_prompt: Optional[str] = None,
        date_fields: Optional[List[str]] = None,
        date_format: Optional[str] = None,
        unknown_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract fields from an uploaded file.
        
        Args:
            file (BinaryIO): The uploaded file
            fields (List[str]): List of field names to extract
            chunking_method (str, optional): Method for chunking text. Defaults to "words".
            chunk_size (int, optional): Size of each chunk in words. Defaults to CHUNK_SIZE.
            chunk_overlap (int, optional): Overlap between chunks in words. Defaults to CHUNK_OVERLAP.
            max_workers (int, optional): Maximum number of worker threads. Defaults to MAX_THREADS.
            output_format (str, optional): Output format. Defaults to OUTPUT_FORMAT.
            system_prompt (str, optional): System prompt to use. Defaults to DEFAULT_SYSTEM_PROMPT.
            date_fields (List[str], optional): List of date fields to normalize. Defaults to None.
            date_format (str, optional): Format for date fields. Defaults to DATE_FORMAT.
            unknown_value (str, optional): Value to use for unknown fields. Defaults to UNKNOWN_VALUE.
            
        Returns:
            Dict[str, Any]: Extraction results
            
        Raises:
            InvalidInputError: If the input is invalid
            ProcessingError: If there is an error during processing
            LLMError: If there is an error with the LLM API
        """
        # Create a temporary file to store the uploaded file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                # Read the uploaded file content
                file_content = file.read()
                
                # Write the uploaded file to the temporary file
                temp_file.write(file_content)
                temp_file.flush()
                
                # Try to decode the file content with different encodings
                encodings = ['utf-8', 'latin-1', 'cp1252']
                text = None
                
                for encoding in encodings:
                    try:
                        # Try to decode the file content
                        if isinstance(file_content, bytes):
                            text = file_content.decode(encoding)
                            logger.info(f"Successfully decoded file with {encoding} encoding")
                            break
                    except UnicodeDecodeError:
                        logger.warning(f"Failed to decode file with {encoding} encoding")
                
                # If all decoding attempts failed, try to read the file directly
                if text is None:
                    try:
                        with open(temp_file.name, 'r', encoding='utf-8') as f:
                            text = f.read()
                            logger.info("Successfully read file with utf-8 encoding")
                    except UnicodeDecodeError:
                        try:
                            with open(temp_file.name, 'r', encoding='latin-1') as f:
                                text = f.read()
                                logger.info("Successfully read file with latin-1 encoding")
                        except Exception as e:
                            logger.error(f"Failed to read file: {str(e)}")
                            raise ProcessingError(f"Failed to read file: {str(e)}")
                
                # If we still don't have text, raise an error
                if not text:
                    raise ProcessingError("Failed to read file content")
                
                # Extract fields from the text
                result = await ExtractorService.extract_fields(
                    text=text,
                    fields=fields,
                    chunking_method=chunking_method,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    max_workers=max_workers,
                    output_format=output_format,
                    system_prompt=system_prompt,
                    date_fields=date_fields,
                    date_format=date_format,
                    unknown_value=unknown_value,
                )
                
                return result
            
            finally:
                # Delete the temporary file
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
    
    @staticmethod
    async def extract_fields(
        text: str,
        fields: List[str],
        chunking_method: str = "words",
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        max_workers: Optional[int] = None,
        output_format: Optional[str] = None,
        system_prompt: Optional[str] = None,
        date_fields: Optional[List[str]] = None,
        date_format: Optional[str] = None,
        unknown_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract fields from text.
        
        Args:
            text (str): The input text to extract fields from
            fields (List[str]): List of field names to extract
            chunking_method (str, optional): Method for chunking text. Defaults to "words".
            chunk_size (int, optional): Size of each chunk in words. Defaults to CHUNK_SIZE.
            chunk_overlap (int, optional): Overlap between chunks in words. Defaults to CHUNK_OVERLAP.
            max_workers (int, optional): Maximum number of worker threads. Defaults to MAX_THREADS.
            output_format (str, optional): Output format. Defaults to OUTPUT_FORMAT.
            system_prompt (str, optional): System prompt to use. Defaults to DEFAULT_SYSTEM_PROMPT.
            date_fields (List[str], optional): List of date fields to normalize. Defaults to None.
            date_format (str, optional): Format for date fields. Defaults to DATE_FORMAT.
            unknown_value (str, optional): Value to use for unknown fields. Defaults to UNKNOWN_VALUE.
            
        Returns:
            Dict[str, Any]: Extraction results
            
        Raises:
            InvalidInputError: If the input is invalid
            ProcessingError: If there is an error during processing
            LLMError: If there is an error with the LLM API
        """
        # Use default values if not provided
        chunk_size = chunk_size or CHUNK_SIZE
        chunk_overlap = chunk_overlap or CHUNK_OVERLAP
        max_workers = max_workers or MAX_THREADS
        output_format = output_format or OUTPUT_FORMAT
        system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        date_format = date_format or DATE_FORMAT
        unknown_value = unknown_value or UNKNOWN_VALUE
        
        # Validate input
        if not text:
            raise InvalidInputError("Text input is required", "The 'text' field cannot be empty")
        
        if not fields:
            raise InvalidInputError("Fields are required", "The 'fields' field cannot be empty")
        
        # Start timer
        start_time = time.time()
        
        try:
            # Chunk the text
            logger.info(f"Chunking text using {chunking_method} method...")
            if chunking_method == "words":
                chunks = chunk_text(text, chunk_size, chunk_overlap)
            else:  # paragraphs
                chunks = chunk_text_by_paragraphs(text, chunk_size, chunk_overlap)
            
            logger.info(f"Text chunked into {len(chunks)} chunks")
            
            # Define the processing function
            def process_chunk(chunk, chunk_idx):
                return extract_fields_from_chunk(
                    chunk, 
                    fields,
                    chunk_index=chunk_idx,
                    system_prompt=system_prompt,
                    output_format=output_format,
                    unknown_value=unknown_value,
                    date_format=date_format
                )
            
            # Process chunks in parallel
            logger.info(f"Processing chunks in parallel with {max_workers} threads...")
            chunk_results = process_chunks_parallel(chunks, process_chunk, max_workers)
            
            # Merge results
            logger.info("Merging results...")
            merged_results = merge_results(chunk_results, fields, unknown_value)
            
            # Validate and normalize results
            validated_results = validate_and_normalize(
                merged_results, 
                fields, 
                date_fields,
                unknown_value,
                date_format
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create metrics
            metrics = {
                "chunks_processed": len(chunks),
                "llm_calls": len(chunks),
                "processing_time": processing_time,
            }
            
            logger.info(f"Extraction completed in {processing_time:.2f} seconds")
            
            return {
                "extracted_fields": validated_results,
                "metrics": metrics,
                "processing_time": processing_time,
            }
            
        except Exception as e:
            # Log the error
            logger.error(f"Error during extraction: {str(e)}", exc_info=True)
            
            # Determine the type of error
            if "Invalid input" in str(e):
                raise InvalidInputError(str(e))
            elif "API" in str(e) or "LLM" in str(e):
                raise LLMError(str(e))
            else:
                raise ProcessingError(str(e))
