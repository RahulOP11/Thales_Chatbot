"""
Pydantic models for API request/response schemas
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation information from retrieved textbook content"""
    source: str = Field(..., description="Textbook source (e.g., '1PUC Physics - English')")
    chapter: Optional[str] = Field(None, description="Chapter name or number")
    page: Optional[int] = Field(None, description="Page number")
    text_snippet: str = Field(..., description="Relevant text excerpt from textbook")


class QueryRequest(BaseModel):
    """Request model for chatbot queries"""
    question: str = Field(..., min_length=1, max_length=500, description="User's question")
    language_preference: Optional[str] = Field(
        None, 
        pattern="^(en|kn)?$",
        description="Language preference: 'en' for English, 'kn' for Kannada, or null for auto-detect"
    )
    grade_filter: Optional[str] = Field(
        None,
        pattern="^(1PUC|2PUC)?$",
        description="Filter by grade: '1PUC', '2PUC', or null for all grades"
    )
    subject_filter: Optional[str] = Field(
        None,
        pattern="^(Physics|Chemistry|Biology)?$",
        description="Filter by subject: 'Physics', 'Chemistry', 'Biology', or null for all subjects"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Newton's first law of motion?",
                "language_preference": "en",
                "grade_filter": "1PUC"
            }
        }


class QueryResponse(BaseModel):
    """Response model for chatbot queries"""
    answer: str = Field(..., description="Generated answer from RAG system")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    language_detected: str = Field(..., description="Detected or used language (en/kn)")
    processing_time: float = Field(..., description="Processing time in seconds")
    retrieval_count: int = Field(..., description="Number of relevant chunks retrieved")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Newton's first law of motion states that an object at rest stays at rest...",
                "citations": [
                    {
                        "source": "1PUC Physics - English",
                        "chapter": "Laws of Motion",
                        "page": 45,
                        "text_snippet": "An object at rest will remain at rest..."
                    }
                ],
                "language_detected": "en",
                "processing_time": 2.34,
                "retrieval_count": 5
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vector_db_status: str
    total_chunks: int
    indexed_books: List[str]
    embedding_model: str


class MetadataResponse(BaseModel):
    """Available textbooks and metadata"""
    grades: List[str]
    subjects: List[str]
    languages: List[str]
    textbooks: List[dict]
