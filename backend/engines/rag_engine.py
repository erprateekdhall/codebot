"""
RAG Engine - Retrieval Augmented Generation
Handles semantic code search using vector embeddings
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import logging
import asyncio
from functools import lru_cache

from config import settings
from models.schemas import CodeChunk

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Semantic code search using embeddings and vector database
    """
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize ChromaDB and embedding model"""
        try:
            logger.info("Initializing RAG Engine...")
            
            # Initialize embedding model
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.embedding_model = await asyncio.to_thread(
                SentenceTransformer,
                settings.EMBEDDING_MODEL
            )
            
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            
            self.initialized = True
            logger.info("✅ RAG Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Engine: {str(e)}")
            raise
    
    async def index_chunks(self, chunks: List[CodeChunk]):
        """
        Index code chunks into vector database
        """
        if not self.initialized:
            raise RuntimeError("RAG Engine not initialized")
        
        try:
            logger.info(f"Indexing {len(chunks)} code chunks...")
            
            documents = []
            metadatas = []
            ids = []
            embeddings = []
            
            # Process in batches
            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                
                for chunk in batch:
                    # Create searchable document
                    doc = self._create_document(chunk)
                    documents.append(doc)
                    
                    # Metadata
                    metadatas.append({
                        'filepath': chunk.filepath,
                        'type': chunk.type,
                        'name': chunk.name,
                        'start_line': chunk.start_line,
                        'end_line': chunk.end_line,
                        'language': chunk.language
                    })
                    
                    ids.append(chunk.chunk_id)
                
                # Generate embeddings for batch
                batch_docs = documents[i:i + batch_size]
                batch_embeddings = await asyncio.to_thread(
                    self.embedding_model.encode,
                    batch_docs,
                    show_progress_bar=False
                )
                embeddings.extend(batch_embeddings.tolist())
            
            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"✅ Indexed {len(chunks)} chunks successfully")
            
        except Exception as e:
            logger.error(f"Indexing failed: {str(e)}")
            raise
    
    def _create_document(self, chunk: CodeChunk) -> str:
        """Create searchable document from code chunk"""
        parts = [
            f"Type: {chunk.type}",
            f"Name: {chunk.name}",
            f"File: {chunk.filepath}",
        ]
        
        if chunk.methods:
            parts.append(f"Methods: {', '.join(chunk.methods)}")
        
        if chunk.imports:
            parts.append(f"Imports: {', '.join(chunk.imports)}")
        
        parts.append(f"Code:\n{chunk.code}")
        
        return "\n".join(parts)
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Semantic search for relevant code
        """
        if not self.initialized:
            raise RuntimeError("RAG Engine not initialized")
        
        try:
            # Generate query embedding
            query_embedding = await asyncio.to_thread(
                self.embedding_model.encode,
                [query],
                show_progress_bar=False
            )
            
            # Search ChromaDB
            where_filter = self._build_filter(filters) if filters else None
            
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'chunk_id': results['ids'][0][i],
                    'code': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'score': 1 - results['distances'][0][i]  # Convert distance to similarity
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    def _build_filter(self, filters: Dict) -> Dict:
        """Build ChromaDB where filter"""
        where_filter = {}
        
        if 'file_types' in filters and filters['file_types']:
            where_filter['language'] = {"$in": filters['file_types']}
        
        if 'type' in filters:
            where_filter['type'] = filters['type']
        
        return where_filter
    
    async def health_check(self) -> bool:
        """Check if RAG engine is healthy"""
        try:
            if not self.initialized:
                return False
            
            # Try a simple operation
            count = self.collection.count()
            logger.info(f"RAG health check: {count} chunks indexed")
            return True
            
        except Exception as e:
            logger.error(f"RAG health check failed: {str(e)}")
            return False
    
    async def close(self):
        """Cleanup resources"""
        logger.info("Closing RAG Engine...")
        self.initialized = False
