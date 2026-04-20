"""
Document processor for extracting and chunking textbook PDFs
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class TextbookProcessor:
    """Process PDF textbooks into chunked documents with metadata"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict]:
        """Extract text from PDF with page-level metadata"""
        print(f"📄 Processing: {pdf_path.name}")
        
        try:
            doc = fitz.open(pdf_path)
            pages_data = []
            
            for page_num, page in enumerate(doc, start=1):
                # Extract text with proper encoding handling
                text = page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                
                # Clean up text with readable replacements
                # Replace corrupted symbols with plain text equivalents
                replacements = {
                    # Common mojibake patterns to text
                    'â¦': 'ohm',
                    'Â²': '^2',
                    'Â³': '^3',
                    'Â¹': '^1', 
                    'â»Â¹': '^-1',
                    'â»': '^-',
                    'Â°': ' degrees',
                    'Âµ': 'micro',
                    'â': ' proportional to ',
                    'â€': '-',
                    'Ã—': ' x ',
                    'Ã·': ' / ',
                    'Ã': 'x',  # Additional multiplication patterns
                    'Â ': ' ',  # Non-breaking space
                    'Ï': 'rho',  # Greek rho
                    'âQ': 'delta-Q',  # Delta Q
                    'ât': 'delta-t',  # Delta t
                    'âtâ': 'delta-t ',  # Delta t with arrow
                    'âV': 'delta-V',  # Delta V
                    'âI': 'delta-I',  # Delta I
                    'â‰ˆ': ' approximately ',
                    'â‰': ' not equal ',
                    # Remove corrupted special chars
                    '\uf0b7': '',
                    'â€œ': '"',
                    'â€': '"',
                    'â€™': "'",
                    'â€˜': "'",
                    'ï£«': '',
                    'ï£¬': '',
                    'ï£¶': '',
                    'ï£¸': '',
                    'ï£·': '',
                }
                
                for old, new in replacements.items():
                    text = text.replace(old, new)
                
                # Skip pages with very little text (likely cover pages, blank pages)
                if len(text.strip()) < 50:
                    continue
                
                pages_data.append({
                    "page_number": page_num,
                    "text": text,
                    "char_count": len(text)
                })
            
            doc.close()
            print(f"  ✓ Extracted {len(pages_data)} pages")
            return pages_data
            
        except Exception as e:
            print(f"  ✗ Error processing {pdf_path.name}: {str(e)}")
            return []
    
    def parse_metadata_from_filename(self, filename: str) -> Dict:
        """Parse metadata from standardized filename format"""
        # Expected format: {Grade}_{Subject}_{Language}.pdf
        # Example: 1PUC_Physics_English.pdf
        
        stem = Path(filename).stem
        parts = stem.split("_")
        
        if len(parts) >= 3:
            return {
                "grade": parts[0],
                "subject": parts[1],
                "language": parts[2],
                "book_id": stem
            }
        else:
            # Fallback for non-standard filenames
            return {
                "grade": "Unknown",
                "subject": "Unknown",
                "language": "Unknown",
                "book_id": stem
            }
    
    def detect_chapter_from_text(self, text: str) -> Optional[str]:
        """Attempt to detect chapter information from text content"""
        # Simple heuristic: look for "Chapter" or "CHAPTER" in first 200 chars
        first_lines = text[:200].upper()
        
        if "CHAPTER" in first_lines:
            # Extract chapter line
            for line in text[:300].split("\n"):
                if "chapter" in line.lower():
                    return line.strip()
        
        return None
    
    def chunk_pages(
        self,
        pages_data: List[Dict],
        metadata: Dict
    ) -> List[Document]:
        """Chunk page texts into smaller documents with metadata"""
        documents = []
        
        for page_info in pages_data:
            page_text = page_info["text"]
            page_num = page_info["page_number"]
            
            # Detect potential chapter info
            chapter = self.detect_chapter_from_text(page_text)
            
            # Split page text into chunks
            chunks = self.splitter.split_text(page_text)
            
            for chunk_idx, chunk in enumerate(chunks):
                # Create document with rich metadata
                doc_metadata = {
                    **metadata,
                    "page": page_num,
                    "chunk_index": chunk_idx,
                    "chapter": chapter,
                    "source_file": metadata.get("book_id", "unknown")
                }
                
                doc = Document(
                    page_content=chunk,
                    metadata=doc_metadata
                )
                documents.append(doc)
        
        return documents
    
    def process_textbook(self, pdf_path: Path) -> List[Document]:
        """Process a single textbook PDF into chunked documents"""
        # Parse metadata from filename
        metadata = self.parse_metadata_from_filename(pdf_path.name)
        
        # Extract text from PDF
        pages_data = self.extract_text_from_pdf(pdf_path)
        
        if not pages_data:
            return []
        
        # Chunk pages into documents
        documents = self.chunk_pages(pages_data, metadata)
        
        print(f"  ✓ Created {len(documents)} chunks")
        return documents
    
    def process_all_textbooks(
        self,
        pdfs_dir: Path,
        output_json: Optional[Path] = None
    ) -> List[Document]:
        """Process all PDFs in directory"""
        print("\n📚 Processing all textbooks...\n")
        
        all_documents = []
        pdf_files = list(pdfs_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"⚠ No PDF files found in {pdfs_dir}")
            return []
        
        for pdf_path in pdf_files:
            documents = self.process_textbook(pdf_path)
            all_documents.extend(documents)
        
        print(f"\n✅ Total chunks created: {len(all_documents)}")
        
        # Optionally save to JSON for inspection
        if output_json:
            self.save_chunks_to_json(all_documents, output_json)
        
        return all_documents
    
    def save_chunks_to_json(self, documents: List[Document], output_path: Path):
        """Save processed chunks to JSON for inspection/debugging"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        chunks_data = []
        for doc in documents:
            chunks_data.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
        
        print(f"📝 Saved chunks to: {output_path}")


def main():
    """Main entry point for testing"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get directories
    project_root = Path(__file__).parent.parent.parent
    pdfs_dir = project_root / "data" / "pdfs"
    output_json = project_root / "data" / "processed" / "chunks.json"
    
    # Initialize processor
    chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    processor = TextbookProcessor(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Process all textbooks
    documents = processor.process_all_textbooks(pdfs_dir, output_json)
    
    # Print summary
    if documents:
        print("\n" + "=" * 70)
        print("📊 Processing Summary:")
        print(f"  Total chunks: {len(documents)}")
        
        # Count by book
        book_counts = {}
        for doc in documents:
            book_id = doc.metadata.get("book_id", "unknown")
            book_counts[book_id] = book_counts.get(book_id, 0) + 1
        
        print(f"  Unique books: {len(book_counts)}")
        for book_id, count in sorted(book_counts.items()):
            print(f"    - {book_id}: {count} chunks")
        print("=" * 70)


if __name__ == "__main__":
    main()
