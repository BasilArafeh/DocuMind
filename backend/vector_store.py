"""
DocuMind Vector Store
Wrapper for ChromaDB to store and query document embeddings,
Search for similar chunks when user asks a question
"""
from openai import OpenAI
from config import settings
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict #Labels telling us what data looks like
from config import get_settings


settings = get_settings()

class VectorStore:
    """Manages document storage and retrieval using ChromaDB"""

    def __init__(self, persist_directory: str = None,collection_name: str = None):
        """
        Initialize ChromaDB with persistence.
        
        Args:
            persist_directory: Where to save the database (defaults to config)
        """
        if persist_directory is None:    #if user doesn't specify, use ./chroma_data from config
            persist_directory = settings.CHROMA_PERSIST_DIR
        if collection_name is None:
           collection_name = settings.CHROMA_COLLECTION_NAME

        # Store collection name
        self.collection_name = collection_name

         # Initialize ChromaDB client object
        self.client = chromadb.PersistentClient(  #creates a database that saves to disk(survives restarts)
            path=persist_directory, #path = directory where SQLite database files are stored
            settings=ChromaSettings(anonymized_telemetry=False)
    )
    
    # Get or create collection
        self.collection = self.client.get_or_create_collection(  #creates new collection first time, later uses existing collections
           name=self.collection_name,
           metadata={"hnsw:space": "cosine"} #use gnsw for fast search, cosine similarity for matching text embeddings
    )
    
        print(f"Vector initialized at: {persist_directory}")

    def add_documents(self, documents: List[Dict]) -> int:
        """Add documents to the vector store."""
        if len(documents) == 0:
            return 0
        
        ids = [doc['id'] for doc in documents]
        embeddings = [doc['embedding'] for doc in documents]
        contents = [doc['content'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        
        #Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )
        
        print(f"Added {len(documents)} chunks to vector store")
        return len(documents)

#converts users question to embedding, comparing the vector to all stored chunks vectors and return top 5 k similar
    def query(self, query_text: str, n_results: int = 5) -> dict:
        """
        Query the vector store with text.
    
        Args:
        query_text: The question/query as text
        n_results: Number of results to return
        
        Returns:
        Dictionary with 'documents' and 'metadatas' keys
        """
    
    
        # Create embedding for the query text
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=query_text
        )
        query_embedding = response.data[0].embedding
    
        # Query ChromaDB with the embedding
        results = self.collection.query(
           query_embeddings=[query_embedding],
           n_results=n_results,
           include=['documents', 'metadatas', 'distances']
        )
    
    # Return in format main.py expects
        return {
        'documents': results['documents'][0] if results['documents'] else [],
        'metadatas': results['metadatas'][0] if results['metadatas'] else [],
        'distances': results['distances'][0] if results['distances'] else []
        }

    def get_stats(self) -> Dict:
      """
      Get statistics about the indexed documents.
    
      Returns:
        Dict with total_chunks, unique_documents, source_files
      """
      count = self.collection.count() #Gives us count on how many chunks we have stored

      if count > 0:
        # Get all items to find unique sources
        all_items = self.collection.get(include=['metadatas']) #gives us all the items in the db only metadata we acc need
        unique_sources = set(                  # as set is a collection the automatically removes duplicates
            meta.get('source_file', 'unknown')
            for meta in all_items['metadatas']
        )
        return {
            'total_chunks': count,
            'unique_documents': len(unique_sources),  #counts how many unique file names we found
            'source_files': sorted(list(unique_sources)) #takes our set and converts it to a list, sorts it alphabetically, and includes that sorted list
        }
    
    #if chunks <0(db is empty)
      return {
        'total_chunks': 0,
        'unique_documents': 0,
        'source_files': []
      }
    
    #function that takes file_name we want to delete
    def delete_document(self, source_file: str) -> bool:
        """
        Delete all chunks from a specific source file.
    
        Args:
           source_file: The filename to delete (e.g., 'ml_notes.pdf')
    
        Returns:
            True if successful, False if file not found or error occurred
        """
        try:
           # Get all chunk IDs that belong to this source file
            results = self.collection.get(
                where={"source_file": source_file}
            )
        
            if results['ids']:
               # Delete all those chunks
               self.collection.delete(ids=results['ids'])
               return True
        
         # No chunks found with that source file
            return False
        except Exception as e:
            print(f"Error deleting document {source_file}: {e}")
            return False
        
    def clear(self) -> bool:
        """
        Delete all documents and their embeddings from the vector store
    
        Returns:
          True if successful
        """
        try:
            self.client.delete_collection(name=self.collection_name)  #

            self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
            return True
        except Exception as e:
            print(f"Error clearing vector store: {e}")
            return False

          






    
    
