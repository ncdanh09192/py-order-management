from prisma import Prisma
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global Prisma client instance
prisma_client = None

async def get_database() -> Prisma:
    """Get Prisma database client"""
    global prisma_client
    
    if prisma_client is None:
        prisma_client = Prisma()
        await prisma_client.connect()
        logger.info("Connected to database")
    
    return prisma_client

async def close_database():
    """Close database connection"""
    global prisma_client
    
    if prisma_client:
        await prisma_client.disconnect()
        prisma_client = None
        logger.info("Disconnected from database")

async def health_check_database() -> bool:
    """Check database health"""
    try:
        db = await get_database()
        await db.execute_raw("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False
