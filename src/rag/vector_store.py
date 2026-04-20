"""
Vector store setup and management using ChromaDB
"""
import os
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv


class VectorStoreManager:
    """Manage ChromaDB vector store for textbook embeddings"""
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        embedding_model: Optional[str] = None,
        collection_name: str = "puc_textbooks"
    ):
        load_dotenv()
        
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_PERSIST_DIR",
            "./vectorstore"
        )
        self.embedding_model_name = embedding_model or os.getenv(
            "EMBEDDING_MODEL",
            "intfloat/multilingual-e5-base"
        )
        self.collection_name = collection_name
        
        self.embeddings = None
        self.vectorstore = None
    
    def initialize_embeddings(self):
        """Initialize the embedding model"""
        if self.embeddings is None:
            print(f"🧠 Loading embedding model: {self.embedding_model_name}")
            print("   This may take a few moments on first run...")
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
            
            print("   ✓ Embedding model loaded")
    
    def create_vectorstore(
        self,
        documents: List[Document],
        batch_size: int = 32
    ):
        """Create vector store from documents"""
        self.initialize_embeddings()
        
        print(f"\n💾 Creating vector store...")
        print(f"   Persist directory: {self.persist_directory}")
        print(f"   Total documents: {len(documents)}")
        print(f"   Batch size: {batch_size}")
        
        # Create persist directory
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Process in batches to manage memory
        print(f"\n🔄 Processing {len(documents)} documents in batches...")
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            print(f"   Batch {batch_num}/{total_batches}: Processing {len(batch)} chunks...")
            
            if self.vectorstore is None:
                # Create new vectorstore with first batch
                self.vectorstore = Chroma.from_documents(
                    documents=batch,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_name=self.collection_name
                )
            else:
                # Add to existing vectorstore
                self.vectorstore.add_documents(batch)
        
        print(f"\n✅ Vector store created successfully!")
        print(f"   Location: {self.persist_directory}")
        
        return self.vectorstore
    
    def load_vectorstore(self):
        """Load existing vector store from disk"""
        self.initialize_embeddings()
        
        persist_path = Path(self.persist_directory)
        
        if not persist_path.exists():
            raise FileNotFoundError(
                f"Vector store not found at {self.persist_directory}. "
                "Please run build_vectorstore.py first."
            )
        
        print(f"📂 Loading vector store from: {self.persist_directory}")
        
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name
        )
        
        # Get collection stats
        collection = self.vectorstore._collection
        count = collection.count()
        
        print(f"   ✓ Loaded {count} document chunks")
        
        return self.vectorstore
    
    def get_retriever(
        self,
        search_type: str = "similarity",
        k: int = 5,
        score_threshold: Optional[float] = None
    ):
        """Get retriever interface for the vector store"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        search_kwargs = {"k": k}
        
        if score_threshold is not None:
            search_type = "similarity_score_threshold"
            search_kwargs["score_threshold"] = score_threshold
        
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[dict] = None
    ) -> List[Document]:
        """Search vector store directly"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        search_kwargs = {}
        if filter_dict:
            search_kwargs["filter"] = filter_dict
        
        return self.vectorstore.similarity_search(
            query,
            k=k,
            **search_kwargs
        )
    
    def get_stats(self) -> dict:
        """Get statistics about the vector store"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        collection = self.vectorstore._collection
        count = collection.count()
        
        # Get sample metadata to determine what's indexed
        sample_docs = self.vectorstore.similarity_search("test", k=100)
        
        books = set()
        grades = set()
        subjects = set()
        languages = set()
        
        for doc in sample_docs:
            metadata = doc.metadata
            if "book_id" in metadata:
                books.add(metadata["book_id"])
            if "grade" in metadata:
                grades.add(metadata["grade"])
            if "subject" in metadata:
                subjects.add(metadata["subject"])
            if "language" in metadata:
                languages.add(metadata["language"])
        
        return {
            "total_chunks": count,
            "indexed_books": sorted(list(books)),
            "grades": sorted(list(grades)),
            "subjects": sorted(list(subjects)),
            "languages": sorted(list(languages))
        }


def main():
    """Build vector store from processed documents"""
    from src.rag.document_processor import TextbookProcessor
    
    print("\n" + "=" * 70)
    print("  Building Vector Store for PUC Textbooks")
    print("=" * 70)
    
    # Get directories
    project_root = Path(__file__).parent.parent.parent
    pdfs_dir = project_root / "data" / "pdfs"
    
    # Check if PDFs exist
    pdf_files = list(pdfs_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"\n⚠ No PDF files found in {pdfs_dir}")
        print("   Please run: python src/utils/download_textbooks.py")
        return
    
    print(f"\n📚 Found {len(pdf_files)} textbook PDFs")
    
    # Process documents
    processor = TextbookProcessor()
    documents = processor.process_all_textbooks(pdfs_dir)
    
    if not documents:
        print("\n✗ No documents to process")
        return
    
    # Create vector store
    vector_manager = VectorStoreManager()
    vector_manager.create_vectorstore(documents, batch_size=32)
    
    # Print stats
    stats = vector_manager.get_stats()
    print("\n📊 Vector Store Statistics:")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Indexed books: {len(stats['indexed_books'])}")
    for book in stats['indexed_books']:
        print(f"     - {book}")
    print(f"   Grades: {', '.join(stats['grades'])}")
    print(f"   Subjects: {', '.join(stats['subjects'])}")
    print(f"   Languages: {', '.join(stats['languages'])}")
    
    print("\n" + "=" * 70)
    print("✅ Vector store build complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
