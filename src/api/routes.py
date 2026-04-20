"""
FastAPI routes for the chatbot API
"""
import time
from fastapi import APIRouter, HTTPException, status
from src.models.schemas import (
    QueryRequest,
    QueryResponse,
    Citation,
    HealthResponse,
    MetadataResponse
)
from src.rag.retrieval_chain import RAGChatbot

# Initialize router
router = APIRouter()

# Global chatbot instance (lazy initialization)
chatbot = None


def get_chatbot() -> RAGChatbot:
    """Get or initialize chatbot instance"""
    global chatbot
    if chatbot is None:
        chatbot = RAGChatbot()
        chatbot.initialize()
    return chatbot


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_chatbot(request: QueryRequest):
    """
    Query the RAG chatbot with a question
    
    - **question**: The question to ask (required)
    - **language_preference**: Preferred language ('en' or 'kn', optional)
    - **grade_filter**: Filter by grade ('1PUC' or '2PUC', optional)
    - **subject_filter**: Filter by subject ('Physics', 'Chemistry', or 'Biology', optional)
    """
    try:
        bot = get_chatbot()
        
        # Force strict defensive type-checking to protect Cloud Run libraries
        safe_question = str(request.question)
        safe_lang = str(request.language_preference) if request.language_preference else None
        safe_grade = str(request.grade_filter) if request.grade_filter else None
        safe_subj = str(request.subject_filter) if request.subject_filter else None
        
        # Query the chatbot
        answer, citations_data, detected_lang, proc_time, ret_count = bot.query(
            question=safe_question,
            language_preference=safe_lang,
            grade_filter=safe_grade,
            subject_filter=safe_subj
        )
        
        # Convert citations to Pydantic models
        citations = [Citation(**citation) for citation in citations_data]
        
        return QueryResponse(
            answer=answer,
            citations=citations,
            language_detected=detected_lang,
            processing_time=round(proc_time, 2),
            retrieval_count=ret_count
        )
        
    except ValueError as e:
        # Configuration errors (like missing API key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        # Other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}\n\nTRACEBACK:\n{tb}"
        )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint
    
    Returns the status of the API and vector database
    """
    try:
        bot = get_chatbot()
        stats = bot.get_system_stats()
        
        return HealthResponse(
            status="healthy",
            vector_db_status="connected",
            total_chunks=stats["total_chunks"],
            indexed_books=stats["indexed_books"],
            embedding_model=bot.vector_manager.embedding_model_name
        )
        
    except FileNotFoundError:
        return HealthResponse(
            status="degraded",
            vector_db_status="not_found",
            total_chunks=0,
            indexed_books=[],
            embedding_model="N/A"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.get("/metadata", response_model=MetadataResponse, status_code=status.HTTP_200_OK)
async def get_metadata():
    """
    Get metadata about available textbooks
    
    Returns information about grades, subjects, languages, and indexed textbooks
    """
    try:
        bot = get_chatbot()
        stats = bot.get_system_stats()
        
        # Format textbook list
        textbooks = []
        for book_id in stats["indexed_books"]:
            parts = book_id.split("_")
            if len(parts) >= 3:
                textbooks.append({
                    "book_id": book_id,
                    "grade": parts[0],
                    "subject": parts[1],
                    "language": parts[2]
                })
        
        return MetadataResponse(
            grades=stats["grades"],
            subjects=stats["subjects"],
            languages=stats["languages"],
            textbooks=textbooks
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching metadata: {str(e)}"
        )
