from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
from app.routers import auth, patients, status, questions, forms
from app.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="Patient Dashboard API",
    description="API for patient dashboard application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(status.router)
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(questions.router)
app.include_router(forms.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Patient Dashboard API...")
    await init_db()
    logger.info("Database initialized successfully")
    
    # Test Claude service initialization
    try:
        from services.claude import get_claude_service
        claude_service = get_claude_service()
        logger.info("Claude service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Claude service: {e}")
    
    logger.info("Patient Dashboard API startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    await close_db()


@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "Patient Dashboard API", "version": "1.0.0"}

@app.get("/test-logging")
async def test_logging():
    """Test endpoint to verify logging is working"""
    logger.info("Test logging endpoint accessed")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    return {"message": "Logging test completed", "check_logs": True} 