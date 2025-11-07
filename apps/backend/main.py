# apps/backend/main.py
"""
GymGPT API Main Application

This is the entry point for the GymGPT API, which provides intelligent
workout planning with equipment adaptation and soreness management.

Available endpoints:
- GET /health - Basic health check
- POST /plans/workout - Generate single workout
- POST /plans/week - Generate weekly training plan

See API documentation at: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import plans

# Initialize FastAPI application with metadata
app = FastAPI(
    title="GymGPT",
    version="0.1.0",
    description="AI-powered workout planning API with equipment and soreness adaptation"
)

# Configure CORS middleware for development
# TODO: Restrict to specific frontend domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later for your frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Basic health check endpoint.
    
    Returns:
        dict: Simple status indicator
    """
    return {"ok": True}

# Mount the workout planning routes under /plans
app.include_router(plans.router, prefix="/plans", tags=["plans"])