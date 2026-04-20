"""
Build script for creating vector store (used during deployment)
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.vector_store import main as build_vectorstore

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  DEPLOYMENT BUILD: Creating Vector Store")
    print("=" * 70)
    build_vectorstore()
