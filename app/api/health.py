from fastapi import APIRouter, HTTPException
from app.core.database import health_check_database
from app.cache.redis_client import redis_client
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    """
    Health check endpoint.
    
    Checks the health of:
    - Database connection
    - Redis connection
    - Overall system status
    """
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "unknown",
            "redis": "unknown"
        }
    }
    
    # Check database
    try:
        db_healthy = await health_check_database()
        status["services"]["database"] = "healthy" if db_healthy else "unhealthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        status["services"]["database"] = "unhealthy"
    
    # Check Redis
    try:
        redis_healthy = await redis_client.health_check()
        status["services"]["redis"] = "healthy" if redis_healthy else "unhealthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        status["services"]["redis"] = "unhealthy"
    
    # Determine overall status
    if any(service == "unhealthy" for service in status["services"].values()):
        status["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=status)
    
    logger.info("Health check passed")
    return status

@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.
    
    This endpoint checks if the service is ready to accept requests.
    It's more comprehensive than the basic health check.
    """
    try:
        # Check database
        db_ready = await health_check_database()
        if not db_ready:
            raise HTTPException(status_code=503, detail="Database not ready")
        
        # Check Redis
        redis_ready = await redis_client.health_check()
        if not redis_ready:
            raise HTTPException(status_code=503, detail="Redis not ready")
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Service is ready to accept requests"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")
