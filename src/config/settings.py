"""
Central settings module for the DUDOXX field extraction system.
Provides access to all configuration parameters with sensible defaults.
"""
import os
from .env_loader import load_environment

# Load environment variables
env_vars = load_environment()

# API Configuration
API_KEY = env_vars.get('DUDOXX_API_KEY')
BASE_URL = env_vars.get('DUDOXX_BASE_URL', 'https://llm-proxy.dudoxx.com/v1')
MODEL_NAME = env_vars.get('DUDOXX_MODEL_NAME', 'dudoxx')
MEMORY_ENTRIES = int(env_vars.get('DUDOXX_MEMORY_ENTRIES', '5'))

# Chunking Configuration
CHUNK_SIZE = int(env_vars.get('DUDOXX_CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(env_vars.get('DUDOXX_CHUNK_OVERLAP', '100'))
MIN_CHUNK_SIZE = int(env_vars.get('DUDOXX_MIN_CHUNK_SIZE', '200'))

# Parallel Processing Configuration
MAX_THREADS = int(env_vars.get('DUDOXX_MAX_THREADS', '5'))
BATCH_SIZE = int(env_vars.get('DUDOXX_BATCH_SIZE', '10'))

# API Request Configuration
REQUEST_TIMEOUT = int(env_vars.get('DUDOXX_REQUEST_TIMEOUT', '30'))
MAX_RETRIES = int(env_vars.get('DUDOXX_MAX_RETRIES', '3'))
RETRY_DELAY = int(env_vars.get('DUDOXX_RETRY_DELAY', '2'))

# Extraction Configuration
DEFAULT_SYSTEM_PROMPT = env_vars.get(
    'DUDOXX_DEFAULT_SYSTEM_PROMPT', 
    "You are an expert data extractor. Only output the fields requested, based solely on the given text."
)
OUTPUT_FORMAT = env_vars.get('DUDOXX_OUTPUT_FORMAT', 'json')
UNKNOWN_VALUE = env_vars.get('DUDOXX_UNKNOWN_VALUE', 'unknown')

# Date Formatting
DATE_FORMAT = env_vars.get('DUDOXX_DATE_FORMAT', 'dd/mm/YYYY')

# Logging Configuration
DETAILED_LOGGING = env_vars.get('DUDOXX_DETAILED_LOGGING', 'false')
SAVE_PROMPTS = env_vars.get('DUDOXX_SAVE_PROMPTS', 'false')
LOG_LEVEL = env_vars.get('DUDOXX_LOG_LEVEL', 'INFO')
