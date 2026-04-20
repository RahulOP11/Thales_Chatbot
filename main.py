"""
FastAPI application entry point
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.api.routes import router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Thales Chatbot API",
    description="RAG-based chatbot for Karnataka PUC Science Textbooks using LangChain and Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["chatbot"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Thales Chatbot API",
        "description": "Karnataka PUC Science Textbooks RAG Chatbot",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "query": "/api/v1/query",
            "health": "/api/v1/health",
            "metadata": "/api/v1/metadata"
        }
    }


@app.get("/health", tags=["root"])
async def simple_health():
    """Simple health check"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    # Google Cloud Run injects the generic 'PORT' variable
    port = int(os.getenv("PORT", os.getenv("API_PORT", "8080")))
    
    print(f"\n🚀 Starting Thales Chatbot API on {host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/docs\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
