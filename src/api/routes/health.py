"""
Health check endpoint routes.

This module contains the essential health check endpoint
that uses the flowApi client to check external service health.
"""

from fastapi import APIRouter, HTTPException, Depends

from ...flowApi.client import APIClient
from ...flowApi.exceptions import (
    APIConnectionError, APITimeoutError, APIHTTPError, 
    APIResponseError
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
async def health_check(client: APIClient = Depends(get_api_client)):
    """
    Health check endpoint that checks both local service and external API health.
    
    Health checks should not require authentication as they are used for monitoring
    and service discovery purposes.
    
    Args:
        client: APIClient dependency
        
    Returns:
        dict: Health status information including external API status
        
    Raises:
        HTTPException: If health check fails
    """
    try:
        # Check external API health (always unauthenticated)
        health_response = client.health_check()
        
        return {
            "status": "healthy",
            "message": "Service is running",
            "external_api": {
                "status": "healthy" if health_response.result else "unhealthy",
                "timestamp": health_response.timestamp
            }
        }
        
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