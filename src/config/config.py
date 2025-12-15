"""
Enhanced configuration class for loading environment variables including RAG settings.

This module provides the Config class that loads CLIENT_ID, CLIENT_SECRET,
RAG_FOLDER and additional RAG-specific configuration from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Optional, Union


class Config:
    """
    Configuration manager that loads settings from environment variables.
    
    Uses python-dotenv to load variables from a .env file in the project root,
    then reads required and optional configuration values from the environment.
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
    
    def load_config(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Load configuration from environment variables.
        
        Returns:
            Dictionary containing all configuration values
            
        Raises:
            EnvironmentError: If any required environment variable is missing
            ValueError: If any required environment variable is empty
        """
        # Required configuration
        required_vars = ['CLIENT_ID', 'CLIENT_SECRET', 'RAG_FOLDER']
        config = {}
        
        # Load required variables
        for var_name in required_vars:
            value = os.environ.get(var_name)
            
            if value is None:
                raise EnvironmentError(f"Required environment variable '{var_name}' is not set")
            
            if not value.strip():
                raise ValueError(f"Required environment variable '{var_name}' is empty")
            
            config[var_name] = value
        
        # Optional RAG configuration with defaults
        optional_config = {
            # Document processing
            'RAG_CHUNK_SIZE': ('1000', int),
            'RAG_CHUNK_OVERLAP': ('200', int),
            
            # Embedding settings
            'RAG_EMBEDDING_MODEL': ('all-MiniLM-L6-v2', str),
            'RAG_EMBEDDING_BATCH_SIZE': ('32', int),
            
            # Vector store settings
            'RAG_VECTOR_DB_PATH': ('./data/chroma_db', str),
            'RAG_COLLECTION_NAME': ('documents', str),
            
            # Retrieval settings
            'RAG_SIMILARITY_THRESHOLD': ('0.7', float),
            'RAG_MAX_CONTEXT_CHUNKS': ('5', int),
            
            # Context formatting
            'RAG_CONTEXT_SEPARATOR': ('\n\n---\n\n', str),
            'RAG_INCLUDE_SOURCE_INFO': ('true', bool),
            
            # System settings
            'RAG_ENABLE_AUTO_INDEXING': ('true', bool),
        }
        
        # Load optional variables with type conversion
        for var_name, (default_value, var_type) in optional_config.items():
            value = os.environ.get(var_name, default_value)
            
            try:
                if var_type == bool:
                    # Handle boolean conversion
                    config[var_name] = value.lower() in ('true', '1', 'yes', 'on')
                elif var_type == int:
                    config[var_name] = int(value)
                elif var_type == float:
                    config[var_name] = float(value)
                else:
                    config[var_name] = value
                    
            except (ValueError, AttributeError) as e:
                # Use default value if conversion fails
                if var_type == bool:
                    config[var_name] = default_value.lower() in ('true', '1', 'yes', 'on')
                elif var_type == int:
                    config[var_name] = int(default_value)
                elif var_type == float:
                    config[var_name] = float(default_value)
                else:
                    config[var_name] = default_value
        
        return config
    
    def get_rag_config(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get RAG-specific configuration values.
        
        Returns:
            Dictionary containing only RAG configuration
        """
        full_config = self.load_config()
        
        # Filter RAG-specific configuration
        rag_config = {}
        for key, value in full_config.items():
            if key.startswith('RAG_') or key == 'RAG_FOLDER':
                # Remove RAG_ prefix for cleaner keys
                clean_key = key.replace('RAG_', '').lower()
                rag_config[clean_key] = value
        
        return rag_config
    
    def get_api_config(self) -> Dict[str, str]:
        """
        Get API-specific configuration values.
        
        Returns:
            Dictionary containing API configuration
        """
        full_config = self.load_config()
        
        return {
            'CLIENT_ID': full_config['CLIENT_ID'],
            'CLIENT_SECRET': full_config['CLIENT_SECRET']
        }
    
    def validate_rag_folder(self) -> bool:
        """
        Validate that the RAG folder exists and is accessible.
        
        Returns:
            True if RAG folder is valid, False otherwise
        """
        try:
            config = self.load_config()
            rag_folder = Path(config['RAG_FOLDER'])
            
            return (
                rag_folder.exists() and 
                rag_folder.is_dir() and 
                os.access(rag_folder, os.R_OK)
            )
            
        except Exception:
            return False
    
    def get_vector_db_path(self) -> Path:
        """
        Get the vector database path, ensuring parent directories exist.
        
        Returns:
            Path object for vector database
        """
        config = self.load_config()
        db_path = Path(config.get('RAG_VECTOR_DB_PATH', './data/chroma_db'))
        
        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        return db_path