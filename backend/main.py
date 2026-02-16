
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import os
from pathlib import Path
from config import settings
from schemas import QueryRequest, QueryResponse, StatsResponse, ProcessedDocument
from ingestion import extract_pdf_text, chunk_text, generate_embeddings, process_document
from vector_store import VectorStore
from llm_client import LLMClient

# Initialize FastAPI app
app = FastAPI(
    title="DocuMind",
    description="Personal Knowledge Base with RAG",
    version="1.0.0"
)

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
vector_store = VectorStore()
llm_client = LLMClient()

# Create uploads directory (fixed for Docker)
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files BEFORE route definitions
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend")), name="static")

# Serve the frontend at root URL
@app.get("/")
async def serve_frontend():
    return FileResponse(BASE_DIR / "frontend" / "index.html")

# API info endpoint (moved from "/" to "/api")
@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "message": "Welcome to DocuMind API",
        "version": "1.0.0",
        "endpoints": {
            "POST /upload": "Upload documents",
            "POST /query": "Ask questions",
            "GET /stats": "Get statistics",
            "DELETE /clear": "Clear database",
            "GET /health": "Health check"
        }
    }

# POST endpoint (used for sending data TO server)
@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and process documents for indexing
    
    Accepts: PDF, TXT, MD files
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    processed_count = 0   # Track how many files succeeded
    errors = []           # List to store error messages for failed files
    
    for file in files:
        try:
            # Validate file type
            allowed_extensions = [".pdf", ".txt", ".md"]
            file_ext = Path(file.filename).suffix.lower()
            
            if file_ext not in allowed_extensions:
                errors.append(f"{file.filename}: Unsupported file type")
                continue

            # Save file to disk temporarily, 'wb':write mode 
            file_path = UPLOAD_DIR / file.filename
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Process the document
            if file_ext == '.pdf':
                text = extract_pdf_text(str(file_path))
            else:  # .txt or .md
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Process and add to vector store
            documents = process_document(file.filename, text)
            vector_store.add_documents(documents)

            # Increment success counter (file proc. successfully)
            processed_count += 1
            
            # Clean up temporary file, as now its in the db
            os.remove(file_path)
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    return {
        "message": f"Processed {processed_count} file(s)",
        "processed": processed_count,
        "total": len(files),
        "errors": errors if errors else None
    }

# POST endpoint for asking questions
@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the knowledge base and get an AI-generated answer
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Get relevant chunks from vector store
        results = vector_store.query(
            query_text=request.query,
            n_results=request.top_k
        )
        
        if not results["documents"]:
            return QueryResponse(
                query=request.query,
                answer="I couldn't find any relevant information in your knowledge base for this question.",
                sources=[],
                chunks_used=0
            )
        
        # Generate answer using LLM
        answer = llm_client.generate_answer(
            query=request.query,
            context_chunks=results["documents"]
        )
        
        # Prepare sources
        sources = [
            {
                "text": doc,
                "source_file": meta.get("source_file", "unknown"),
                "chunk_index": meta.get("chunk_index", 0)
            }
            for doc, meta in zip(results["documents"], results["metadatas"])
        ]
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            chunks_used=len(results["documents"])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get statistics about indexed documents."""
    try:
        stats = vector_store.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.delete("/clear")
async def clear_database():
    """Clear all documents from the vector store."""
    try:
        success = vector_store.clear()
        if success:
            return {"message": "Database cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear database")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        stats = vector_store.get_stats()
        return {
            "status": "healthy",
            "vector_store": "connected",
            "documents_indexed": stats["unique_documents"],
            "chunks_indexed": stats["total_chunks"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
