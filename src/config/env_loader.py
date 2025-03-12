"""
Environment variable loader for the DUDOXX field extraction system.
Loads variables from the environment file and makes them available to the application.
"""
import os
from dotenv import load_dotenv

def load_environment(env_file="dudoxx-llm.env"):
    """
    Load environment variables from file, overriding OS settings.
    
    Args:
        env_file (str): Path to the environment file
        
    Returns:
        dict: Dictionary of loaded environment variables
    """
    # Get the absolute path to the environment file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(base_dir, env_file)
    
    # Load the environment variables
    load_dotenv(env_path, override=True)
    
    # Return a dictionary of all loaded environment variables
    return {key: value for key, value in os.environ.items() if key.startswith('DUDOXX_')}
