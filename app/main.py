"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    scan_router,
    ask_router,
    action_router,
    graph_router,
    settings_router
)

app = FastAPI(
    title="Project Companion API",
    description="Universal project companion bot API",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(scan_router)
app.include_router(ask_router)
app.include_router(action_router)
app.include_router(graph_router)
app.include_router(settings_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Project Companion API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

