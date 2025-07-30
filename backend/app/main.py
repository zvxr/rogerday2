from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
from app.routers import auth, patients, status

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


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    await close_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Patient Dashboard API", "version": "1.0.0"} 