"""
Simple singleton client manager for maintaining a single APIClient instance.

This module provides a ClientManager class that ensures all requests share
the same APIClient instance, eliminating redundant authentication calls.
"""

import asyncio
from typing import Optional

from ..flowApi.client import APIClient


class ClientManager:
    """
    Simple singleton manager for APIClient instances.
    
    Ensures that all requests share the same APIClient instance,
    which maintains authentication state across requests.
    """
    
    _instance: Optional[APIClient] = None
    _lock: asyncio.Lock = asyncio.Lock()
    
    @classmethod
    async def get_client(cls) -> APIClient:
        """
        Get the shared APIClient instance.
        
        Creates a new instance on first call, then returns the same
        instance for all subsequent calls.
        
        Returns:
            APIClient: The shared client instance
        """
        if cls._instance is None:
            async with cls._lock:
                # Double-check pattern to avoid race conditions
                if cls._instance is None:
                    cls._instance = APIClient()
        
        return cls._instance
    
    @classmethod
    async def reset_client(cls) -> None:
        """
        Reset the client instance (useful for testing or error recovery).
        
        Creates a new client instance, discarding the previous one.
        """
        async with cls._lock:
            if cls._instance is not None:
                cls._instance.close()
            cls._instance = APIClient()
    
    @classmethod
    async def close_client(cls) -> None:
        """
        Close and cleanup the client instance.
        
        Should be called during application shutdown.
        """
        async with cls._lock:
            if cls._instance is not None:
                cls._instance.close()
                cls._instance = None