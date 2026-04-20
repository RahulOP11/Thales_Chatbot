"""
RAG retrieval chain using LangChain and Google Gemini
"""
import os
import time
from typing import List, Dict, Optional, Tuple
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from dotenv import load_dotenv

from src.rag.vector_store import VectorStoreManager


class RAGChatbot:
    """RAG-based chatbot for PUC science textbooks"""
    
    def __init__(self):
        load_dotenv()
        
        # Initialize components
        self.vector_manager = VectorStoreManager()
        self.llm = None
        self.qa_chain = None
        
        # Configuration
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.temperature = float(os.getenv("TEMPERATURE", "0.3"))
        self.top_k = int(os.getenv("TOP_K", "5"))
        
        # Track initialization
        self._initialized = False
    
    def initialize(self):
        """Lazy initialization of LLM and retrieval chain"""
        if self._initialized:
            return
        
        print("🚀 Initializing RAG Chatbot...")
        
        # Check for API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise ValueError(
                "GOOGLE_API_KEY not set. Please:\n"
                "1. Get free API key from: https://makersuite.google.com/app/apikey\n"
                "2. Copy .env.example to .env\n"
                "3. Add your API key to .env file"
            )
        
        # Initialize LLM
        print(f"🤖 Loading {self.model_name}...")
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=api_key,
            convert_system_message_to_human=True
        )
        
        # Load vector store
        self.vector_manager.load_vectorstore()
        
        # Store prompt template
        self.prompt_template = self._create_prompt_template()
        
        self._initialized = True
        print("✅ RAG Chatbot initialized successfully!\n")
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Create custom prompt template for the QA chain"""
        template = """You are an expert tutor for Karnataka PUC (Pre-University Course) science students. Your role is to answer questions based ONLY on the provided textbook content.

Guidelines:
1. Answer questions accurately using only the information from the context provided
2. Support both English and Kannada questions naturally
3. If the context contains the answer, provide a clear and detailed explanation
4. If the context doesn't contain enough information, say: "I cannot find this information in the PUC textbooks provided. Please ask questions related to Physics, Chemistry, or Biology topics from 1st or 2nd PUC syllabus."
5. Include specific details like formulas, definitions, or processes when relevant
6. Be educational and clear in your explanations
7. Do not make up information not present in the context

Context from textbooks:
{context}

Question: {question}

Answer (provide a comprehensive response based on the textbook content):"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def detect_language(self, text: str) -> str:
        """Detect if text is primarily English or Kannada"""
        # Simple heuristic: check for Kannada Unicode range
        kannada_chars = sum(1 for char in text if '\u0C80' <= char <= '\u0CFF')
        
        if kannada_chars > len(text) * 0.3:  # >30% Kannada chars
            return "kn"
        return "en"
    
    def build_filter(
        self,
        grade_filter: Optional[str] = None,
        subject_filter: Optional[str] = None,
        language_preference: Optional[str] = None
    ) -> Optional[Dict]:
        """Build metadata filter for retrieval in ChromaDB format"""
        conditions = []
        
        if grade_filter:
            conditions.append({"grade": {"$eq": grade_filter}})
        
        if subject_filter:
            conditions.append({"subject": {"$eq": subject_filter}})
        
        if language_preference:
            lang_map = {"en": "English", "kn": "Kannada"}
            if language_preference in lang_map:
                conditions.append({"language": {"$eq": lang_map[language_preference]}})
        
        # ChromaDB filter format
        if len(conditions) == 0:
            return None
        elif len(conditions) == 1:
            return conditions[0]
        else:
            return {"$and": conditions}
    
    def extract_citations(self, source_documents: List[Document]) -> List[Dict]:
        """Extract citation information from retrieved documents"""
        citations = []
        seen_sources = set()
        
        for doc in source_documents:
            metadata = doc.metadata
            
            # Create unique source identifier
            source_key = (
                metadata.get("book_id", "Unknown"),
                metadata.get("page", 0)
            )
            
            # Avoid duplicate citations from same page
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)
            
            # Format source name
            grade = metadata.get("grade", "Unknown")
            subject = metadata.get("subject", "Unknown")
            language = metadata.get("language", "Unknown")
            source_name = f"{grade} {subject} - {language}"
            
            citation = {
                "source": source_name,
                "chapter": metadata.get("chapter"),
                "page": metadata.get("page"),
                "text_snippet": doc.page_content[:200] + "..."  # First 200 chars
            }
            
            citations.append(citation)
        
        return citations
    
    def query(
        self,
        question: str,
        language_preference: Optional[str] = None,
        grade_filter: Optional[str] = None,
        subject_filter: Optional[str] = None
    ) -> Tuple[str, List[Dict], str, float, int]:
        """
        Query the RAG system
        
        Returns:
            Tuple of (answer, citations, detected_language, processing_time, retrieval_count)
        """
        if not self._initialized:
            self.initialize()
        
        start_time = time.time()
        
        # Detect language if not specified
        detected_lang = language_preference or self.detect_language(question)
        
        # Build metadata filter
        filter_dict = self.build_filter(grade_filter, subject_filter, language_preference)
        
        # For filtered retrieval, we need to use the vector store directly
        if filter_dict:
            # Custom retrieval with filters
            relevant_docs = self.vector_manager.search(
                question,
                k=self.top_k,
                filter_dict=filter_dict
            )
            
            # Build context manually
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Create prompt manually
            prompt = self.prompt_template.format(
                context=context,
                question=question
            )
            
            # Get answer from LLM
            response = self.llm.invoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
            source_documents = relevant_docs
        else:
            # Use standard retrieval without filters
            relevant_docs = self.vector_manager.search(
                question,
                k=self.top_k
            )
            
            # Build context
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Create prompt
            prompt = self.prompt_template.format(
                context=context,
                question=question
            )
            
            # Get answer from LLM
            answer_response = self.llm.invoke(prompt)
            answer = answer_response.content if hasattr(answer_response, 'content') else str(answer_response)
            source_documents = relevant_docs
        
        # Extract citations
        citations = self.extract_citations(source_documents)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return (
            answer,
            citations,
            detected_lang,
            processing_time,
            len(source_documents)
        )
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        if not self._initialized:
            self.initialize()
        
        return self.vector_manager.get_stats()


def main():
    """Test the RAG chatbot"""
    print("\n" + "=" * 70)
    print("  Testing RAG Chatbot")
    print("=" * 70 + "\n")
    
    # Initialize chatbot
    chatbot = RAGChatbot()
    
    # Test questions
    test_questions = [
        ("What is Newton's first law of motion?", "en", None),
        ("Explain the process of photosynthesis", "en", None),
        ("What is Ohm's law?", "en", "1PUC"),
    ]
    
    for question, lang_pref, grade_filter in test_questions:
        print(f"❓ Question: {question}")
        if grade_filter:
            print(f"   Filter: Grade={grade_filter}")
        print()
        
        try:
            answer, citations, detected_lang, proc_time, ret_count = chatbot.query(
                question=question,
                language_preference=lang_pref,
                grade_filter=grade_filter
            )
            
            print(f"💬 Answer:\n{answer}\n")
            print(f"📚 Citations ({len(citations)}):")
            for i, citation in enumerate(citations, 1):
                print(f"   [{i}] {citation['source']}")
                if citation['page']:
                    print(f"       Page {citation['page']}")
                if citation['chapter']:
                    print(f"       Chapter: {citation['chapter']}")
            
            print(f"\n⏱  Processing time: {proc_time:.2f}s")
            print(f"🔍 Retrieved chunks: {ret_count}")
            print(f"🌐 Language: {detected_lang}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n" + "-" * 70 + "\n")


if __name__ == "__main__":
    main()
