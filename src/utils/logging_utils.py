"""
Logging utilities for the DUDOXX field extraction system.
Provides functions for logging API calls, prompts, and responses.
"""
import os
import json
import logging
import datetime
from pathlib import Path
from src.config import settings

# Configure logging
log_level_str = settings.LOG_LEVEL.upper()
log_level = getattr(logging, log_level_str, logging.INFO)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create logger
logger = logging.getLogger('dudoxx_extractor')

# Create logs directory if it doesn't exist
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

# Add file handler
log_file = logs_dir / f'dudoxx_extractor_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def get_logger():
    """
    Get the logger instance.
    
    Returns:
        logging.Logger: Logger instance
    """
    return logger

def log_api_call(prompt, response, duration, chunk_index=None):
    """
    Log an API call to the LLM.
    
    Args:
        prompt (str): The prompt sent to the LLM
        response (dict): The response received from the LLM
        duration (float): The duration of the API call in seconds
        chunk_index (int, optional): The index of the chunk being processed
    """
    # Log to console and file
    chunk_info = f" (Chunk {chunk_index})" if chunk_index is not None else ""
    logger.info(f"API call{chunk_info} completed in {duration:.2f} seconds")
    
    # If detailed logging is enabled, log the prompt and response
    if settings.DETAILED_LOGGING.lower() == 'true':
        logger.debug(f"Prompt{chunk_info}: {prompt}")
        logger.debug(f"Response{chunk_info}: {json.dumps(response, indent=2)}")
    
    # Save detailed logs to separate files if enabled
    if settings.SAVE_PROMPTS.lower() == 'true':
        save_prompt_and_response(prompt, response, chunk_index)

def save_prompt_and_response(prompt, response, chunk_index=None):
    """
    Save the prompt and response to separate files.
    
    Args:
        prompt (str): The prompt sent to the LLM
        response (dict): The response received from the LLM
        chunk_index (int, optional): The index of the chunk being processed
    """
    # Create prompts and responses directories if they don't exist
    prompts_dir = logs_dir / 'prompts'
    responses_dir = logs_dir / 'responses'
    prompts_dir.mkdir(exist_ok=True)
    responses_dir.mkdir(exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate filenames
    chunk_suffix = f"_chunk_{chunk_index}" if chunk_index is not None else ""
    prompt_file = prompts_dir / f"prompt_{timestamp}{chunk_suffix}.txt"
    response_file = responses_dir / f"response_{timestamp}{chunk_suffix}.json"
    
    # Save prompt
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    # Save response
    with open(response_file, 'w', encoding='utf-8') as f:
        json.dump(response, f, indent=2)
