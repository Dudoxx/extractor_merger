"""
DUDOXX API client module for the field extraction system.
Provides a client for interacting with the DUDOXX LLM API using the OpenAI SDK.
"""
import json
import re
import time
from openai import OpenAI
from src.config import settings
from src.utils.logging_utils import log_api_call, get_logger

# Get logger
logger = get_logger()

class DudoxxClient:
    """Client for interacting with the DUDOXX LLM API."""
    
    def __init__(
        self, 
        api_key=None, 
        base_url=None, 
        model_name=None,
        timeout=None,
        max_retries=None,
        retry_delay=None
    ):
        """
        Initialize the DUDOXX API client.
        
        Args:
            api_key (str, optional): API key for authentication. Defaults to settings.API_KEY.
            base_url (str, optional): Base URL for the API. Defaults to settings.BASE_URL.
            model_name (str, optional): Model name to use. Defaults to settings.MODEL_NAME.
            timeout (int, optional): Request timeout in seconds. Defaults to settings.REQUEST_TIMEOUT.
            max_retries (int, optional): Maximum number of retries. Defaults to settings.MAX_RETRIES.
            retry_delay (int, optional): Delay between retries in seconds. Defaults to settings.RETRY_DELAY.
        """
        self.api_key = api_key or settings.API_KEY
        self.base_url = base_url or settings.BASE_URL
        self.model_name = model_name or settings.MODEL_NAME
        self.timeout = timeout or settings.REQUEST_TIMEOUT
        self.max_retries = max_retries or settings.MAX_RETRIES
        self.retry_delay = retry_delay or settings.RETRY_DELAY
        
        if not self.api_key:
            raise ValueError("API key is required")
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )
    
    def extract_fields(self, text, fields, system_prompt=None, chunk_index=None):
        """
        Extract fields from text using the DUDOXX LLM.
        
        Args:
            text (str): The input text to extract fields from
            fields (list): List of field names to extract
            system_prompt (str, optional): System prompt to use. Defaults to settings.DEFAULT_SYSTEM_PROMPT.
            chunk_index (int, optional): The index of the chunk being processed. Used for logging.
            
        Returns:
            dict: Extracted fields and values
        """
        system_prompt = system_prompt or settings.DEFAULT_SYSTEM_PROMPT
        user_prompt = self._build_user_prompt(text, fields)
        
        # Log the API call
        logger.info(f"Sending request to DUDOXX API{' for chunk ' + str(chunk_index) if chunk_index is not None else ''}")
        
        # Send the request with retries
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # Use OpenAI SDK for chat completion
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Extract content from response
                extracted_content = response.choices[0].message.content
                
                # Convert response to dict for logging
                response_dict = {
                    "id": response.id,
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": response.model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": extracted_content
                            },
                            "finish_reason": response.choices[0].finish_reason
                        }
                    ]
                }
                
                # Log the API call
                log_api_call(user_prompt, response_dict, duration, chunk_index)
                
                # Parse the extracted content based on the output format
                return self._parse_response(extracted_content)
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to extract fields after {self.max_retries} attempts")
                    raise Exception(f"Failed to extract fields after {self.max_retries} attempts: {str(e)}")
    
    def _build_user_prompt(self, text, fields):
        """
        Build the user prompt for field extraction.
        
        Args:
            text (str): The input text to extract fields from
            fields (list): List of field names to extract
            
        Returns:
            str: User prompt for field extraction
        """
        field_list = ", ".join(fields)
        unknown_value = settings.UNKNOWN_VALUE
        output_format = settings.OUTPUT_FORMAT
        date_format = settings.DATE_FORMAT
        
        prompt = f"""Extract the following fields from the text: {field_list}.
If a field is not explicitly stated in the text, mark it as '{unknown_value}'.
Provide the answer in {output_format} format.

For date fields, use the format: {date_format}
For example:
- "February 9th 1949" → 09/02/1949
- "Feb 9, 1949" → 09/02/1949
- "9th Feb 1949" → 09/02/1949

Do not add information not found in the text. Only extract what is explicitly stated.

Text:
{text}
"""
        return prompt
    
    def _parse_response(self, response_text):
        """
        Parse the response based on the configured output format.
        
        Args:
            response_text (str): Response text from the API
            
        Returns:
            dict: Parsed response
        """
        output_format = settings.OUTPUT_FORMAT.lower()
        
        if output_format == 'json':
            # Extract JSON from the response
            try:
                # Try to parse the entire response as JSON
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from markdown code blocks
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass
                
                # If all else fails, return the raw text
                return {"error": "Failed to parse JSON response", "raw_response": response_text}
        
        elif output_format == 'text':
            # Return the raw text response
            return {"text_response": response_text}
        
        else:  # Default to dictionary-like parsing
            # Parse key-value pairs from the text
            result = {}
            
            # Look for patterns like "Field: Value" or "Field - Value"
            matches = re.findall(r'([^:\n-]+)(?::|-)([^\n]+)', response_text)
            for field, value in matches:
                result[field.strip()] = value.strip()
            
            return result
