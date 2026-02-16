"""
DocuMind Document Ingestion Pipeline
Handles loading, chunking, and embedding documents.
"""

import os
import tiktoken    #Count tokens (for chunking)
from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader  #Extract text from PDFs
from openai import OpenAI
from backend.config import get_settings
from backend.config import settings


print(f"DEBUG - LLM_MODEL: {settings.LLM_MODEL}")
print(f"DEBUG - API_KEY starts with: {settings.OPENAI_API_KEY[:10]}...")

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

#returns a list of dictionaries, where each dictionary represents one loaded document
def load_document(folder_path: str = None) -> List[Dict[str,str]]:
    """
    Load all PDF, txt, and md files from a folder
    
    Args:
        folder_path: Path to documents folder
    
    Returns:
        List of dicts with keys: filename, content, file_type
    """
    if folder_path == None:
        folder_path = settings.DOCUMENTS_FOLDER  #if user didnt provide a file path
    
    documents = [] #empty list tp create all loaded documents
    folder = Path(folder_path) #folder object , Path handler mkdir()

        # Create folder if it doesn't exist
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        print(f"Created documents folder: {folder_path}")
        return documents
    
    print(f"Loading documents from: {folder_path}")
    
    # Loop through all files in the folder
    for file_path in folder.iterdir():
        if not file_path.is_file():
            continue
        
        suffix = file_path.suffix.lower()  # .pdf, .txt, .md
        content = None
        
        try:
            if suffix == '.pdf':
                content = extract_pdf_text(str(file_path))
                print(f" Loaded PDF: {file_path.name} ({len(content)} chars)")
            
            elif suffix in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f" Loaded {suffix[1:].upper()}: {file_path.name} ({len(content)} chars)")
            
            else:
                print(f"Skipped (unsupported): {file_path.name}")
                continue
            
            if content and content.strip():
                documents.append({
                    'filename': file_path.name,
                    'content': content,
                    'file_type': suffix[1:]  # Remove the dot
                })
            else:
                print(f" Empty content: {file_path.name}")
        
        except Exception as e:
            print(f" Error loading {file_path.name}: {e}")
    
    print(f"\nTotal documents loaded: {len(documents)}\n")
    return documents
 

#Input: Path to PDF file (string),output: Extracted text (string)
def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from all pages of a PDF file
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Extracted text with page separators
    """
    reader = PdfReader(pdf_path) #Opens the PDF file
    text_parts = [] #store text from each page separately
    
    for page_num,page in enumerate(reader.pages,start=1):
        page_text = page.extract_text() #Uses pypdf to extract text from the page
        if page_text and page_text.strip():
            text_parts.append(f"[Page {page_num}]\n{page_text}")

    #Takes all pages and joins them with double line breaks
    return "\n\n".join(text_parts) 



def chunk_text(content: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split text into overlapping chunks based on token count
    
    Args:
        content: Text to chunk
        chunk_size: Tokens per chunk (defaults to config setting)
        overlap: Token overlap between chunks (defaults to config setting)
    
    Returns:
        List of text chunks
    """
    if chunk_size == None:
        chunk_size = settings.CHUNK_SIZE
    if overlap == None:
        overlap = settings.CHUNK_OVERLAP
    
    encoding = tiktoken.encoding_for_model(settings.LLM_MODEL) #Gets the tokenizer for gpt-4o-mini
    tokens = encoding.encode(content) # Convert text to tokens

    # Handle empty or very short content
    if len(tokens) == 0:
        return []
    if len(tokens) <= chunk_size:
        return [content]  # Already small enough, no need to chunk
    
    chunks = [] #chunks will store all the text chunks
    start = 0 #start is our position in the token list

    while start < len(tokens):  #loops until we've processed all tokens
        # Get chunk tokens range
        end = min(start + chunk_size ,len(tokens))
        chunk_tokens = tokens[start:end]
        
        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens)  #convert tokens back to text
        chunks.append(chunk_text)
        
        # Move start forward (accounting for overlap)
        start = start + chunk_size - overlap
        
        # Break if we've covered all tokens
        if end >= len(tokens):
            break
    
    return chunks

#calls OpenAI API to convert text chunks into vectors.
def generate_embeddings(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenAI API
    Processes in batches to handle API limits
    
    Args:
        texts: List of text chunks to embed
        batch_size: Number of chunks to embed per API call
    
    Returns:
        List of embedding vectors (each is a list of floats)
    """

    all_embeddings = []  # store all the embedding vectors

    for i in range(0,len(texts),batch_size):  # creates: 0, 100, 200, 300 : looping 100 texts at a time
        batch = texts[i:i + batch_size]

        try:
            response = client.embeddings.create(     #Sends batch of texts to OpenAI
                model = settings.EMBEDDING_MODEL,    #Model: text-embedding-3-small
                input= batch
            )

            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)  #extracts the vectors that have been embedded and add them to the list
            
            print(f" Generated embeddings for {len(batch)} chunks (batch {i//batch_size + 1})")  
        
        except Exception as e:
            print(f"Error generating embeddings for batch {i//batch_size + 1}: {e}")    #prints which batch failed
            raise  #so we dont index the dcument 
    
    return all_embeddings

#combines chunking and embedding into one simple function
def process_document(filename: str, content: str) -> List[Dict]:
    """
    Complete pipeline: chunk document and generate embeddings
    
    Args:
        filename: Name of the source file
        content: Document text content
    
    Returns:
        List of dicts ready for vector store, each with:
        - id: unique identifier
        - content: chunk text
        - embedding: vector
        - metadata: source info
    """
    print(f" Processing: {filename}")

    #Chunk the text
    chunks = chunk_text(content)
    print(f"Created {len(chunks)} chunks")  #Takes the full document text and splits it into 500-token chunks

    if len(chunks) == 0:
        print(f" No chunks created")
        return []
    
    #Generate embeddings
    embeddings = generate_embeddings(chunks) #Converts all chunks to vectors 
    
    #Prepare documents for indexing
    documents = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        documents.append({
            'id': f"{filename}_{idx}",
            'content': chunk,
            'embedding': embedding,
            'metadata': {
                'source_file': filename,
                'chunk_index': idx,
                'total_chunks': len(chunks)
            }
        })
    
    print(f"Processed {len(documents)} chunks\n")
    return documents
