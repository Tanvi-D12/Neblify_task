"""Configuration management for the Deel AI Challenge API."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    API_TITLE: str = os.getenv("API_TITLE", "Deel AI Challenge API")
    
    # Data Configuration
    DATA_USERS_PATH: str = os.getenv("DATA_USERS_PATH", "data/users.csv")
    DATA_TRANSACTIONS_PATH: str = os.getenv("DATA_TRANSACTIONS_PATH", "data/transactions.csv")
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Cache Configuration
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))


# Global settings instance
settings = Settings()
