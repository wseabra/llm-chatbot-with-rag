"""
Configuration class for loading environment variables.

This module provides the Config class that loads CLIENT_ID, CLIENT_SECRET,
and RAG_FOLDER from environment variables using python-dotenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Optional


class Config:
    """
    Configuration manager that loads settings from environment variables.
    
    Uses python-dotenv to load variables from a .env file in the project root,
    then reads CLIENT_ID, CLIENT_SECRET, and RAG_FOLDER from the environment.
    """
    
    def __init__(self, dotenv_path: Optional[str] = None, load_dotenv_file: bool = True):
        """
        Initialize the Config class.
        
        Args:
            dotenv_path: Optional path to .env file. If None, uses project root/.env
            load_dotenv_file: Whether to load the .env file. Set to False for testing.
        """
        if load_dotenv_file:
            if dotenv_path is None:
                # Find project root (assuming it's 2 levels up from this file)
                project_root = Path(__file__).parent.parent.parent
                dotenv_path = project_root / '.env'
            
            # Load environment variables from .env file
            load_dotenv(dotenv_path)
    
    def load_config(self) -> Dict[str, str]:
        """
        Load configuration from environment variables.
        
        Returns:
            Dictionary containing CLIENT_ID, CLIENT_SECRET, and RAG_FOLDER
            
        Raises:
            EnvironmentError: If any required environment variable is missing
            ValueError: If any required environment variable is empty
        """
        required_vars = ['CLIENT_ID', 'CLIENT_SECRET', 'RAG_FOLDER']
        config = {}
        
        for var_name in required_vars:
            value = os.environ.get(var_name)
            
            if value is None:
                raise EnvironmentError(f"Required environment variable '{var_name}' is not set")
            
            if not value.strip():
                raise ValueError(f"Required environment variable '{var_name}' is empty")
            
            config[var_name] = value
        
        return config.copy()  # Return a copy to prevent external modification