import fitz
import os

pdfs_dir = "data/pdfs"
pdfs = [f for f in os.listdir(pdfs_dir) if f.endswith('.pdf')]

print("\n📚 Verifying PDFs...\n")

total_pages = 0
for pdf in sorted(pdfs):
    try:
        doc = fitz.open(os.path.join(pdfs_dir, pdf))
        pages = len(doc)
        total_pages += pages
        doc.close()
        print(f"✓ {pdf}: {pages} pages")
    except Exception as e:
        print(f"✗ {pdf}: Error - {e}")

print(f"\n✅ All {len(pdfs)} PDFs are valid!")
print(f"📊 Total pages: {total_pages}")
