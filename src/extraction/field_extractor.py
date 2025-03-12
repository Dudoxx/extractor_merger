"""
Field extractor module for the DUDOXX field extraction system.
Provides functions for extracting fields from text chunks.
"""
from src.api.dudoxx_client import DudoxxClient
from src.extraction.prompt_builder import build_system_prompt, build_extraction_prompt, build_few_shot_examples
from src.config import settings

class FieldExtractor:
    """Field extractor for extracting fields from text chunks."""
    
    def __init__(
        self,
        api_client=None,
        system_prompt=None,
        output_format=None,
        unknown_value=None,
        date_format=None,
        use_few_shot=True
    ):
        """
        Initialize the field extractor.
        
        Args:
            api_client (DudoxxClient, optional): DUDOXX API client. If None, a new client will be created.
            system_prompt (str, optional): System prompt to use. Defaults to settings.DEFAULT_SYSTEM_PROMPT.
            output_format (str, optional): Output format (json, text, dict). Defaults to settings.OUTPUT_FORMAT.
            unknown_value (str, optional): Value to use for unknown fields. Defaults to settings.UNKNOWN_VALUE.
            date_format (str, optional): Format for date fields. Defaults to settings.DATE_FORMAT.
            use_few_shot (bool, optional): Whether to use few-shot examples. Defaults to True.
        """
        self.api_client = api_client or DudoxxClient()
        self.system_prompt = build_system_prompt(system_prompt)
        self.output_format = output_format or settings.OUTPUT_FORMAT
        self.unknown_value = unknown_value or settings.UNKNOWN_VALUE
        self.date_format = date_format or settings.DATE_FORMAT
        self.use_few_shot = use_few_shot
    
    def extract_fields(self, text, fields, chunk_index=None):
        """
        Extract fields from text.
        
        Args:
            text (str): The input text to extract fields from
            fields (list): List of field names to extract
            chunk_index (int, optional): The index of the chunk being processed. Used for logging.
            
        Returns:
            dict: Extracted fields and values
        """
        # Build few-shot examples if enabled
        examples = build_few_shot_examples(fields, self.output_format) if self.use_few_shot else None
        
        # Build the extraction prompt
        prompt = build_extraction_prompt(
            text=text,
            fields=fields,
            examples=examples,
            output_format=self.output_format,
            unknown_value=self.unknown_value,
            date_format=self.date_format
        )
        
        # Extract fields using the API client
        return self.api_client.extract_fields(text, fields, self.system_prompt, chunk_index=chunk_index)

def extract_fields_from_chunk(chunk, fields, chunk_index=None, **kwargs):
    """
    Extract fields from a text chunk.
    
    Args:
        chunk (str): The text chunk to extract fields from
        fields (list): List of field names to extract
        chunk_index (int, optional): The index of the chunk being processed. Used for logging.
        **kwargs: Additional arguments to pass to FieldExtractor
        
    Returns:
        dict: Extracted fields and values
    """
    extractor = FieldExtractor(**kwargs)
    return extractor.extract_fields(chunk, fields, chunk_index=chunk_index)
