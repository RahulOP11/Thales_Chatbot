"""
Utility script to download Karnataka PUC science textbooks from KTBS website
"""
import os
import sys
import httpx
import asyncio
from pathlib import Path
from typing import List, Dict
import time


# Define textbook URLs (these need to be updated with actual KTBS URLs)
# Note: KTBS website structure may vary - these are placeholder patterns
TEXTBOOKS = [
    # 1st PUC English Medium
    {
        "grade": "1PUC",
        "subject": "Physics",
        "language": "English",
        "filename": "1PUC_Physics_English.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/1PUC_Physics_English.pdf"
    },
    {
        "grade": "1PUC",
        "subject": "Chemistry",
        "language": "English",
        "filename": "1PUC_Chemistry_English.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/1PUC_Chemistry_English.pdf"
    },
    {
        "grade": "1PUC",
        "subject": "Biology",
        "language": "English",
        "filename": "1PUC_Biology_English.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/1PUC_Biology_English.pdf"
    },
    # 1st PUC Kannada Medium
    {
        "grade": "1PUC",
        "subject": "Physics",
        "language": "Kannada",
        "filename": "1PUC_Physics_Kannada.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/1PUC_Physics_Kannada.pdf"
    },
    {
        "grade": "1PUC",
        "subject": "Chemistry",
        "language": "Kannada",
        "filename": "1PUC_Chemistry_Kannada.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/1PUC_Chemistry_Kannada.pdf"
    },
    {
        "grade": "1PUC",
        "subject": "Biology",
        "language": "Kannada",
        "filename": "1PUC_Biology_Kannada.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/1PUC_Biology_Kannada.pdf"
    },
    # 2nd PUC English Medium
    {
        "grade": "2PUC",
        "subject": "Physics",
        "language": "English",
        "filename": "2PUC_Physics_English.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/2PUC_Physics_English.pdf"
    },
    {
        "grade": "2PUC",
        "subject": "Chemistry",
        "language": "English",
        "filename": "2PUC_Chemistry_English.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/2PUC_Chemistry_English.pdf"
    },
    {
        "grade": "2PUC",
        "subject": "Biology",
        "language": "English",
        "filename": "2PUC_Biology_English.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/2PUC_Biology_English.pdf"
    },
    # 2nd PUC Kannada Medium
    {
        "grade": "2PUC",
        "subject": "Physics",
        "language": "Kannada",
        "filename": "2PUC_Physics_Kannada.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/2PUC_Physics_Kannada.pdf"
    },
    {
        "grade": "2PUC",
        "subject": "Chemistry",
        "language": "Kannada",
        "filename": "2PUC_Chemistry_Kannada.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/2PUC_Chemistry_Kannada.pdf"
    },
    {
        "grade": "2PUC",
        "subject": "Biology",
        "language": "Kannada",
        "filename": "2PUC_Biology_Kannada.pdf",
        "url": "https://ktbs.kar.nic.in/new/website/downloads/2PUC_Biology_Kannada.pdf"
    },
]


async def download_file(client: httpx.AsyncClient, book: Dict, output_dir: Path) -> bool:
    """Download a single textbook PDF"""
    filepath = output_dir / book["filename"]
    
    # Skip if already exists
    if filepath.exists():
        print(f"✓ {book['filename']} already exists, skipping...")
        return True
    
    try:
        print(f"⬇ Downloading {book['filename']}...")
        response = await client.get(book["url"], timeout=120.0, follow_redirects=True)
        
        if response.status_code == 200:
            filepath.write_bytes(response.content)
            file_size_mb = len(response.content) / (1024 * 1024)
            print(f"✓ Downloaded {book['filename']} ({file_size_mb:.2f} MB)")
            return True
        else:
            print(f"✗ Failed to download {book['filename']}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error downloading {book['filename']}: {str(e)}")
        return False


async def download_all_textbooks(output_dir: Path):
    """Download all textbooks asynchronously"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📚 Karnataka PUC Science Textbook Downloader")
    print(f"📁 Output directory: {output_dir}")
    print(f"📖 Total textbooks to download: {len(TEXTBOOKS)}\n")
    
    async with httpx.AsyncClient() as client:
        tasks = [download_file(client, book, output_dir) for book in TEXTBOOKS]
        results = await asyncio.gather(*tasks)
    
    success_count = sum(results)
    print(f"\n✅ Download complete: {success_count}/{len(TEXTBOOKS)} successful")
    
    if success_count < len(TEXTBOOKS):
        print("\n⚠ Some downloads failed. This might be due to:")
        print("  1. Incorrect URLs - KTBS website structure may have changed")
        print("  2. Network connectivity issues")
        print("  3. Files not available on KTBS website")
        print("\n💡 Next steps:")
        print("  - Visit https://ktbs.kar.nic.in to find correct textbook URLs")
        print("  - Update URLs in src/utils/download_textbooks.py")
        print("  - Or manually download PDFs and place them in data/pdfs/")
        print("  - Ensure filenames follow pattern: {Grade}_{Subject}_{Language}.pdf")


def verify_pdfs(output_dir: Path):
    """Verify downloaded PDFs are valid"""
    try:
        import fitz  # PyMuPDF
        
        print("\n🔍 Verifying PDF files...")
        valid_count = 0
        
        for book in TEXTBOOKS:
            filepath = output_dir / book["filename"]
            if not filepath.exists():
                continue
                
            try:
                doc = fitz.open(filepath)
                page_count = len(doc)
                doc.close()
                
                if page_count > 0:
                    print(f"✓ {book['filename']}: {page_count} pages")
                    valid_count += 1
                else:
                    print(f"✗ {book['filename']}: Invalid PDF (0 pages)")
            except Exception as e:
                print(f"✗ {book['filename']}: Corrupted ({str(e)})")
        
        print(f"\n✅ Verified: {valid_count} valid PDFs")
        
    except ImportError:
        print("\n⚠ PyMuPDF not installed, skipping verification")
        print("  Install with: pip install PyMuPDF")


def main():
    """Main entry point"""
    # Get project root directory
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "data" / "pdfs"
    
    print("=" * 70)
    asyncio.run(download_all_textbooks(output_dir))
    verify_pdfs(output_dir)
    print("=" * 70)


if __name__ == "__main__":
    main()
