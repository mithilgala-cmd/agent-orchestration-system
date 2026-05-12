import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def validate_environment():
    """Ensures all required environment variables are set before startup."""
    required_vars = ["GROQ_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        error_msg = f"CRITICAL: Missing environment variables: {', '.join(missing)}. Check your .env file."
        logger.error(error_msg)
        raise EnvironmentError(error_msg)
    
    logger.info("Environment validation successful.")

def get_env_var(name: str, default: str = None) -> str:
    """Retrieve an environment variable or return a default value."""
    return os.getenv(name, default)
