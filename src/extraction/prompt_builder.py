"""
Prompt builder module for the DUDOXX field extraction system.
Provides functions for building effective prompts for field extraction.
"""
from src.config import settings

def build_system_prompt(custom_prompt=None):
    """
    Build the system prompt for field extraction.
    
    Args:
        custom_prompt (str, optional): Custom system prompt. Defaults to settings.DEFAULT_SYSTEM_PROMPT.
        
    Returns:
        str: System prompt for field extraction
    """
    return custom_prompt or settings.DEFAULT_SYSTEM_PROMPT

def build_extraction_prompt(text, fields, examples=None, output_format=None, unknown_value=None, date_format=None):
    """
    Build the user prompt for field extraction.
    
    Args:
        text (str): The input text to extract fields from
        fields (list): List of field names to extract
        examples (list, optional): List of few-shot examples. Each example should be a dict with 'input' and 'output' keys.
        output_format (str, optional): Output format (json, text, dict). Defaults to settings.OUTPUT_FORMAT.
        unknown_value (str, optional): Value to use for unknown fields. Defaults to settings.UNKNOWN_VALUE.
        date_format (str, optional): Format for date fields. Defaults to settings.DATE_FORMAT.
        
    Returns:
        str: User prompt for field extraction
    """
    # Use environment settings if not provided
    output_format = output_format or settings.OUTPUT_FORMAT
    unknown_value = unknown_value or settings.UNKNOWN_VALUE
    date_format = date_format or settings.DATE_FORMAT
    
    # Format the list of fields
    field_list = ", ".join(fields)
    
    # Start building the prompt
    prompt = f"""Extract the following fields from the text: {field_list}.
If a field is not explicitly stated in the text, mark it as '{unknown_value}'.
Provide the answer in {output_format} format.
"""
    
    # Add date formatting instructions if date_format is provided
    if date_format:
        prompt += f"""
For date fields, use the format: {date_format}
For example:
- "February 9th 1949" → 09/02/1949
- "Feb 9, 1949" → 09/02/1949
- "9th Feb 1949" → 09/02/1949
"""
    
    # Add few-shot examples if provided
    if examples and len(examples) > 0:
        prompt += "\nExamples:\n"
        for i, example in enumerate(examples):
            prompt += f"\nExample {i+1}:\n"
            prompt += f"Input: {example['input']}\n"
            prompt += f"Output: {example['output']}\n"
    
    # Add instructions to avoid hallucination
    prompt += "\nDo not add information not found in the text. Only extract what is explicitly stated.\n"
    
    # Add the input text
    prompt += f"\nText:\n{text}\n"
    
    return prompt

def build_few_shot_examples(fields, output_format=None):
    """
    Build few-shot examples for field extraction.
    
    Args:
        fields (list): List of field names to extract
        output_format (str, optional): Output format (json, text, dict). Defaults to settings.OUTPUT_FORMAT.
        
    Returns:
        list: List of few-shot examples
    """
    # Use environment settings if not provided
    output_format = output_format or settings.OUTPUT_FORMAT
    
    # Create examples based on the fields and output format
    examples = []
    
    # Example for name fields
    if any(field in fields for field in ['first_name', 'last_name', 'name', 'full_name']):
        if output_format.lower() == 'json':
            examples.append({
                'input': "John Smith was born on February 9th, 1949 in New York City.",
                'output': '{"first_name": "John", "last_name": "Smith", "birthdate": "09/02/1949", "birthplace": "New York City"}'
            })
        else:
            examples.append({
                'input': "John Smith was born on February 9th, 1949 in New York City.",
                'output': "first_name: John\nlast_name: Smith\nbirthdate: 09/02/1949\nbirthplace: New York City"
            })
    
    # Example for date fields
    if any(field in fields for field in ['date', 'birthdate', 'birth_date', 'start_date', 'end_date']):
        if output_format.lower() == 'json':
            examples.append({
                'input': "The event started on Jan 15th, 2023 and ended on February 28, 2023.",
                'output': '{"start_date": "15/01/2023", "end_date": "28/02/2023"}'
            })
        else:
            examples.append({
                'input': "The event started on Jan 15th, 2023 and ended on February 28, 2023.",
                'output': "start_date: 15/01/2023\nend_date: 28/02/2023"
            })
    
    # Example for address or location fields
    if any(field in fields for field in ['address', 'location', 'city', 'state', 'country']):
        if output_format.lower() == 'json':
            examples.append({
                'input': "The company headquarters is located at 123 Main St, Suite 400, San Francisco, CA 94105, USA.",
                'output': '{"address": "123 Main St, Suite 400", "city": "San Francisco", "state": "CA", "zip_code": "94105", "country": "USA"}'
            })
        else:
            examples.append({
                'input': "The company headquarters is located at 123 Main St, Suite 400, San Francisco, CA 94105, USA.",
                'output': "address: 123 Main St, Suite 400\ncity: San Francisco\nstate: CA\nzip_code: 94105\ncountry: USA"
            })
    
    return examples
