"""
Interview Practice Partner - Main Application Entry Point
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from api.endpoints import router as api_router
import os

# Import exception types for global handlers
from services.ollama_client import OllamaConnectionError, OllamaGenerationError
from services.interview_session_manager import (
    SessionNotFoundError,
    InvalidSessionStateError
)

app = FastAPI(
    title="Interview Practice Partner",
    description="AI-powered mock interview system with adaptive questioning and feedback",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers for better error messages
@app.exception_handler(OllamaConnectionError)
async def ollama_connection_error_handler(request: Request, exc: OllamaConnectionError):
    """Handle Ollama connection errors globally with retry advice."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Interview service is temporarily unavailable. Please ensure Ollama is running and try again."
        }
    )


@app.exception_handler(OllamaGenerationError)
async def ollama_generation_error_handler(request: Request, exc: OllamaGenerationError):
    """Handle Ollama generation errors globally."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Failed to generate response. Please try again."
        }
    )


@app.exception_handler(SessionNotFoundError)
async def session_not_found_error_handler(request: Request, exc: SessionNotFoundError):
    """Handle session not found errors globally."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": "Session not found. It may have expired or been deleted."
        }
    )


@app.exception_handler(InvalidSessionStateError)
async def invalid_session_state_error_handler(request: Request, exc: InvalidSessionStateError):
    """Handle invalid session state errors globally."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": str(exc)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected errors."""
    # Log the error for debugging
    print(f"Unexpected error: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again or contact support if the issue persists."
        }
    )

# Include API routes
app.include_router(api_router)

# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/api")
async def root():
    return {
        "message": "Interview Practice Partner API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
