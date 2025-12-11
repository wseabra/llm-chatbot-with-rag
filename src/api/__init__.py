"""
API module for FastAPI implementation.

This module contains all FastAPI-related code including routes, endpoints,
and application configuration.
"""

from .app import create_app

__all__ = ["create_app"]