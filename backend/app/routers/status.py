from fastapi import APIRouter

router = APIRouter(tags=["status"])


@router.get("/status")
async def get_status():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Patient Dashboard API is running"} 