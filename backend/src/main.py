# [Task]: T020 [From]: plan.md §Project Structure
"""
FastAPI main application entry point.
Configures CORS, routes, and error handling.
"""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

from .db import create_db_and_tables
from .middleware.error_handler import setup_error_handlers
from .api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG", "false").lower() != "true" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Creates database tables on startup.
    """
    logger.info("Starting application...")
    create_db_and_tables()
    logger.info("Database tables created/verified")
    yield
    logger.info("Application shutdown")


# Create FastAPI application
app = FastAPI(
    title="Todo App API",
    description="RESTful API for Todo Full-Stack Web Application (Phase II)",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handlers
setup_error_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
