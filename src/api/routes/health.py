"""
Health check endpoint routes.

This module contains health check and monitoring related endpoints
that use the flowApi client to check external service health.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from ...flowApi.client import APIClient
from ...flowApi.exceptions import (
    APIConnectionError, APITimeoutError, APIHTTPError, 
    APIResponseError, APIAuthenticationError
)
from ..clientManager import ClientManager

router = APIRouter(tags=["health"])


async def get_api_client() -> APIClient:
    """
    Dependency to get the shared APIClient instance.
    
    Returns:
        APIClient: Shared API client instance from ClientManager
    """
    return await ClientManager.get_client()


@router.get("/health")
async def health_check(
    authenticated: bool = False,
    client: APIClient = Depends(get_api_client)
):
    """
    Health check endpoint that checks both local service and external API health.
    
    Args:
        authenticated: Whether to perform authenticated health check
        client: APIClient dependency
        
    Returns:
        dict: Health status information including external API status
        
    Raises:
        HTTPException: If health check fails
    """
    try:
        # Check external API health
        health_response = client.health_check(authenticated=authenticated)
        
        return {
            "status": "healthy",
            "message": "Service is running",
            "external_api": {
                "status": "healthy" if health_response.result else "unhealthy",
                "timestamp": health_response.timestamp,
                "authenticated": authenticated
            }
        }
        
    except APIAuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "Authentication failed for external API health check",
                "error": str(e)
            }
        )
    except (APIConnectionError, APITimeoutError) as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "degraded",
                "message": "External API is unreachable",
                "error": str(e),
                "local_service": "healthy"
            }
        )
    except (APIHTTPError, APIResponseError) as e:
        raise HTTPException(
            status_code=502,
            detail={
                "status": "degraded", 
                "message": "External API returned an error",
                "error": str(e),
                "local_service": "healthy"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Unexpected error during health check",
                "error": str(e)
            }
        )


@router.get("/health/simple")
async def simple_health_check():
    """
    Simple health check endpoint that only checks local service status.
    
    Returns:
        dict: Basic health status information
    """
    return {
        "status": "healthy",
        "message": "Local service is running"
    }