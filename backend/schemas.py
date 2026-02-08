"""
API Schemas
Pydantic models for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Dict


# Query/Ask schemas
class QueryRequest(BaseModel):
    """Request model for /query endpoint"""
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User's question"
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of chunks to retrieve"
    )


class Source(BaseModel):
    """Information about a source chunk"""
    text: str
    source_file: str
    chunk_index: int


class QueryResponse(BaseModel):
    """Response model for /query endpoint"""
    query: str
    answer: str
    sources: List[Source]
    chunks_used: int


# Stats schema
class StatsResponse(BaseModel):
    """Response model for /stats endpoint"""
    total_chunks: int
    unique_documents: int
    source_files: List[str]


# Document processing schema
class ProcessedDocument(BaseModel):
    """Schema for a processed document chunk"""
    content: str
    embedding: List[float]
    metadata: dict


# Upload schemas
class UploadFileResponse(BaseModel):
    """Response for file upload"""
    status: str
    filename: str
    document_id: str
    chunks_added: int
    file_type: str


class UploadTextRequest(BaseModel):
    """Request model for uploading text/notes"""
    text: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=200)
    source_type: str = "note"


class UploadResponse(BaseModel):
    """Response model for upload endpoint"""
    status: str
    document_id: str
    chunks_added: int


# Health schema
class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    documents_indexed: int
    chunks_indexed: int
