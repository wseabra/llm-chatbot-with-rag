"""
Logging configuration for the FastAPI RAG Application.

This module provides centralized logging configuration that can be used
across the entire application for consistent logging behavior.
"""

import logging
import logging.config
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def get_logging_config(
    level: str = "INFO",
    format_type: str = "production",
    log_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type (development, production, simple)
        log_file: Optional log file path
        
    Returns:
        Logging configuration dictionary
    """
    
    # Define format strings
    formats = {
        "development": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "production": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "simple": {
            "format": "%(levelname)s - %(name)s - %(message)s",
            "datefmt": None
        }
    }
    
    format_config = formats.get(format_type, formats["production"])
    
    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": format_config["format"],
                "datefmt": format_config["datefmt"]
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "default",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            # Application loggers
            "src.api.app": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.rag.rag_manager": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.rag.embeddings": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.rag.vector_store": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.rag.document_loader": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.rag.document_processor": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.api.rag_dependency": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.api.routes.chat": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.api.routes.health": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "src.flowApi.client": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            # Third-party loggers (reduce noise)
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "chromadb": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "sentence_transformers": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "urllib3": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "httpx": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": level,
            "handlers": ["console"]
        }
    }
    
    # Add file handler if log file is specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "default",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        
        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            if "handlers" in logger_config:
                logger_config["handlers"].append("file")
        
        config["root"]["handlers"].append("file")
    
    return config


def setup_logging(
    level: str = None,
    format_type: str = None,
    log_file: str = None,
    force: bool = True
) -> None:
    """
    Setup application logging configuration.
    
    Args:
        level: Logging level. If None, uses environment variable or INFO
        format_type: Format type. If None, uses environment variable or production
        log_file: Log file path. If None, uses environment variable
        force: Whether to force reconfiguration
    """
    
    # Get configuration from environment variables if not provided
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    if format_type is None:
        format_type = os.getenv("LOG_FORMAT", "production").lower()
    
    if log_file is None:
        log_file = os.getenv("LOG_FILE")
    
    # Get logging configuration
    config = get_logging_config(level, format_type, log_file)
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log configuration info
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={level}, format={format_type}")
    if log_file:
        logger.info(f"Log file: {log_file}")


def setup_development_logging() -> None:
    """Setup logging for development environment."""
    setup_logging(
        level="DEBUG",
        format_type="development",
        log_file=None
    )


def setup_production_logging(log_file: str = "./logs/app.log") -> None:
    """Setup logging for production environment."""
    setup_logging(
        level="INFO",
        format_type="production",
        log_file=log_file
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Environment-based automatic configuration
def configure_logging_from_environment() -> None:
    """Configure logging based on environment variables."""
    
    # Check for environment type
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        setup_production_logging()
    elif env == "development":
        setup_development_logging()
    else:
        # Default configuration
        setup_logging()


# Auto-configure if this module is imported
if __name__ != "__main__":
    # Only auto-configure if no logging has been set up yet
    if not logging.getLogger().handlers:
        configure_logging_from_environment()