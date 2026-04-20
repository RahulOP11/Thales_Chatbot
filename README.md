# Thales Chatbot - Karnataka PUC Science RAG System

A bilingual (English/Kannada) RAG-based chatbot for Karnataka Pre-University Course (PUC) science textbooks, powered by LangChain, Google Gemini, and ChromaDB.

## 🌟 Features

- **Comprehensive Coverage**: 1st and 2nd PUC Physics, Chemistry, and Biology textbooks
- **Bilingual Support**: Answers questions in both English and Kannada
- **Accurate Citations**: Provides page numbers and chapter references
- **Free LLM**: Uses Google Gemini's free tier (no OpenAI costs)
- **Fast Retrieval**: ChromaDB vector store with multilingual embeddings
- **REST API**: FastAPI backend with automatic documentation
- **Cloud Deployed**: Free deployment on Render with cold start tolerance

## 🏗️ Architecture

```
User Question → FastAPI → RAG Chain → Vector DB (ChromaDB) → Retrieve Relevant Chunks
                    ↓
              Google Gemini (LLM) → Generate Answer + Citations
```

**Tech Stack:**
- **LLM**: Google Gemini 1.5 Flash (free tier, 60 requests/min)
- **Embeddings**: `intfloat/multilingual-e5-base` (768-dim, English + Kannada support)
- **Vector DB**: ChromaDB (persistent, no separate server needed)
- **Framework**: LangChain for RAG orchestration
- **API**: FastAPI with async support
- **Deployment**: Render free tier

## 📋 Prerequisites

- Python 3.10 or higher
- Google Gemini API key (free): Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- 2GB free disk space (for textbooks and vector store)
- 1GB RAM minimum for local development

## 🚀 Quick Start (Local Development)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Thales_chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

**Get Gemini API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and paste into `.env` file

### 3. Download and Process Textbooks

```bash
# Download PUC textbooks from KTBS
python src/utils/download_textbooks.py

# Note: If URLs are outdated, manually download PDFs and place in data/pdfs/
# Follow naming convention: {Grade}_{Subject}_{Language}.pdf
# Example: 1PUC_Physics_English.pdf
```

### 4. Build Vector Store

```bash
# Process textbooks and create embeddings
python build_vectorstore.py

# This will:
# - Extract text from PDFs
# - Chunk into 1000-character segments
# - Create multilingual embeddings
# - Store in ChromaDB (./vectorstore directory)
# Takes ~5-10 minutes depending on textbook count
```

### 5. Start API Server

```bash
# Run FastAPI server
python main.py

# Or with uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server starts at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### 6. Test the API

**Using curl:**
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Ask a question
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Newton'\''s first law of motion?",
    "language_preference": "en",
    "grade_filter": "1PUC"
  }'

# Kannada question
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "ನ್ಯೂಟನ್ ನ ಮೊದಲ ನಿಯಮ ಏನು?",
    "language_preference": "kn"
  }'
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "question": "Explain photosynthesis",
        "subject_filter": "Biology"
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Citations: {len(result['citations'])}")
```

## 📚 API Endpoints

### POST `/api/v1/query`
Query the chatbot with a question.

**Request Body:**
```json
{
  "question": "What is Ohm's law?",
  "language_preference": "en",  // Optional: "en" or "kn"
  "grade_filter": "1PUC",       // Optional: "1PUC" or "2PUC"
  "subject_filter": "Physics"    // Optional: "Physics", "Chemistry", "Biology"
}
```

**Response:**
```json
{
  "answer": "Ohm's law states that the current through a conductor...",
  "citations": [
    {
      "source": "1PUC Physics - English",
      "chapter": "Current Electricity",
      "page": 87,
      "text_snippet": "Ohm's law: V = IR..."
    }
  ],
  "language_detected": "en",
  "processing_time": 2.34,
  "retrieval_count": 5
}
```

### GET `/api/v1/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "vector_db_status": "connected",
  "total_chunks": 4523,
  "indexed_books": ["1PUC_Physics_English", "1PUC_Chemistry_English", ...],
  "embedding_model": "intfloat/multilingual-e5-base"
}
```

### GET `/api/v1/metadata`
Get information about available textbooks.

**Response:**
```json
{
  "grades": ["1PUC", "2PUC"],
  "subjects": ["Physics", "Chemistry", "Biology"],
  "languages": ["English", "Kannada"],
  "textbooks": [
    {
      "book_id": "1PUC_Physics_English",
      "grade": "1PUC",
      "subject": "Physics",
      "language": "English"
    }
  ]
}
```

## 🌐 Cloud Deployment (Render)

### Option 1: Automatic Deployment

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo>
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Add `GOOGLE_API_KEY` in Environment Variables
   - Click "Apply" to deploy

3. **Wait for Build:**
   - First build takes ~10-15 minutes (downloads textbooks, builds vector store)
   - Subsequent deploys are faster if no changes to textbooks

### Option 2: Manual Deployment

1. Create new Web Service on Render
2. Connect GitHub repository
3. Configure:
   - **Build Command:** 
     ```bash
     pip install -r requirements.txt && python src/utils/download_textbooks.py && python build_vectorstore.py
     ```
   - **Start Command:** 
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 10000 --workers 1
     ```
4. Add Environment Variable: `GOOGLE_API_KEY=<your-key>`
5. Deploy

### Render Free Tier Notes

- **Memory**: 512MB RAM limit (tight but manageable with optimization)
- **Cold Starts**: Service sleeps after 15min inactivity, takes ~30-60s to wake
- **Build Time**: ~10-15 minutes initially, ~5 minutes for updates
- **Vector Store**: Rebuilt on each deploy (no persistent disk on free tier)
- **Workaround**: Pre-build vector store, commit to repo (if <500MB compressed)

## 🔧 Configuration

Environment variables (`.env` file):

```bash
# Required
GOOGLE_API_KEY=your_api_key_here

# LLM Settings
GEMINI_MODEL=gemini-1.5-flash        # or gemini-1.5-pro for better quality
TEMPERATURE=0.3                       # Lower = more deterministic

# Vector Store
EMBEDDING_MODEL=intfloat/multilingual-e5-base
CHROMA_PERSIST_DIR=./vectorstore
CHUNK_SIZE=1000                       # Characters per chunk
CHUNK_OVERLAP=200                     # Overlap between chunks

# Retrieval
TOP_K=5                               # Number of chunks to retrieve
SIMILARITY_THRESHOLD=0.7              # Minimum similarity score

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## 🧪 Testing

```bash
# Test document processing
python src/rag/document_processor.py

# Test vector store creation
python src/rag/vector_store.py

# Test RAG chain
python src/rag/retrieval_chain.py

# Start API and visit http://localhost:8000/docs for interactive testing
```

## 📂 Project Structure

```
Thales_chatbot/
├── data/
│   ├── pdfs/              # Downloaded textbook PDFs
│   └── processed/         # Processed chunks (JSON, for debugging)
├── vectorstore/           # ChromaDB persistent storage
├── src/
│   ├── api/
│   │   └── routes.py      # FastAPI endpoints
│   ├── models/
│   │   └── schemas.py     # Pydantic models
│   ├── rag/
│   │   ├── document_processor.py  # PDF processing & chunking
│   │   ├── vector_store.py        # ChromaDB management
│   │   └── retrieval_chain.py     # RAG chain with Gemini
│   └── utils/
│       └── download_textbooks.py  # KTBS textbook downloader
├── main.py                # FastAPI application
├── build_vectorstore.py   # Build script for deployment
├── requirements.txt
├── .env.example
├── render.yaml           # Render deployment config
└── README.md
```

## 🐛 Troubleshooting

### Issue: "GOOGLE_API_KEY not set"
**Solution:** 
- Copy `.env.example` to `.env`
- Add your actual API key from Google AI Studio
- Restart the server

### Issue: "No PDF files found"
**Solution:**
- Check if PDFs downloaded to `data/pdfs/`
- KTBS URLs may be outdated - manually download from [KTBS website](https://ktbs.kar.nic.in)
- Ensure filenames follow pattern: `{Grade}_{Subject}_{Language}.pdf`

### Issue: "Vector store not found"
**Solution:**
- Run `python build_vectorstore.py` to create vector store
- Check if `vectorstore/` directory was created
- Verify PDFs exist in `data/pdfs/`

### Issue: "Memory error during embedding"
**Solution:**
- Reduce batch size in `vector_store.py` (default: 32)
- Use smaller embedding model (e.g., `all-MiniLM-L6-v2`)
- Close other applications to free RAM

### Issue: "Render deployment fails"
**Solution:**
- Check build logs for specific error
- Verify `GOOGLE_API_KEY` is set in Render dashboard
- Ensure Python version is 3.10+ in `render.yaml`
- Reduce memory usage by using smaller embedding model

### Issue: "Slow cold start on Render"
**Solution:**
- Expected behavior on free tier (15min inactivity timeout)
- Consider upgrading to paid tier for always-on service
- Or use Railway ($5/month) for better performance
- Pre-build and commit vector store to reduce startup time

## 📖 Usage Examples

**Basic Question:**
```python
POST /api/v1/query
{
  "question": "What is the formula for kinetic energy?"
}
```

**Filtered by Grade:**
```python
POST /api/v1/query
{
  "question": "Explain electromagnetic induction",
  "grade_filter": "2PUC"
}
```

**Kannada Question:**
```python
POST /api/v1/query
{
  "question": "ಜೀವಕೋಶ ಎಂದರೇನು?",  // What is a cell?
  "language_preference": "kn",
  "subject_filter": "Biology"
}
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Better textbook URL discovery
- Enhanced chapter detection
- Image/diagram extraction from PDFs
- Quiz generation feature
- Frontend web interface
- Performance optimizations

## 📄 License

This project is for educational purposes. Textbook content copyright belongs to Karnataka Textbook Society (KTBS).

## 🙏 Acknowledgments

- Karnataka Textbook Society (KTBS) for making textbooks available
- LangChain for RAG framework
- Google for free Gemini API access
- Hugging Face for multilingual embeddings

## 📞 Support

For issues, questions, or suggestions, please open a GitHub issue.

---

**Built with ❤️ for Karnataka PUC students**
