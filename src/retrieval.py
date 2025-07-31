"""
Basic Retrieval System for OnCall.ai

This module implements the core vector retrieval functionality:
- Basic vector search
- Source marking
- Unified output format
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BasicRetrievalSystem:
    """Basic vector retrieval system for medical documents"""
    
    def __init__(self, embedding_dim: int = 768):
        """
        Initialize the retrieval system
        
        Args:
            embedding_dim: Dimension of embeddings (default: 768 for PubMedBERT)
        """
        self.embedding_dim = embedding_dim
        self.embedding_model = None
        self.emergency_index = None
        self.treatment_index = None
        self.emergency_chunks = {}
        self.treatment_chunks = {}
        
        # Initialize system
        self._initialize_system()
        
    def _initialize_system(self) -> None:
        """Initialize embeddings, indices and chunks"""
        try:
            logger.info("Initializing retrieval system...")
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer("NeuML/pubmedbert-base-embeddings")
            logger.info("Embedding model loaded successfully")
            
            # Initialize Annoy indices
            self.emergency_index = AnnoyIndex(self.embedding_dim, 'angular')
            self.treatment_index = AnnoyIndex(self.embedding_dim, 'angular')
            
            # Load data
            current_file = Path(__file__)
            project_root = current_file.parent.parent  # from src to root
            base_path = project_root / "models"
            self._load_chunks(base_path)
            self._load_embeddings(base_path)
            self._build_or_load_indices(base_path)
            
            logger.info("Retrieval system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize retrieval system: {e}")
            raise
            
    def _load_chunks(self, base_path: Path) -> None:
        """Load chunk data from JSON files"""
        try:
            # Load emergency chunks
            with open(base_path / "embeddings" / "emergency_chunks.json", 'r') as f:
                self.emergency_chunks = json.load(f)
            
            # Load treatment chunks
            with open(base_path / "embeddings" / "treatment_chunks.json", 'r') as f:
                self.treatment_chunks = json.load(f)
                
            logger.info("Chunks loaded successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Chunk file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in chunk file: {e}")
            raise
            
    def _load_embeddings(self, base_path: Path) -> None:
        """Load pre-computed embeddings"""
        try:
            # Load emergency embeddings
            self.emergency_embeddings = np.load(
                base_path / "embeddings" / "emergency_embeddings.npy"
            )
            
            # Load treatment embeddings
            self.treatment_embeddings = np.load(
                base_path / "embeddings" / "treatment_embeddings.npy"
            )
            
            logger.info("Embeddings loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            raise
            
    def _build_or_load_indices(self, base_path: Path) -> None:
        """Build or load Annoy indices"""
        indices_path = base_path / "indices" / "annoy"
        emergency_index_path = indices_path / "emergency.ann"
        treatment_index_path = indices_path / "treatment.ann"
        
        try:
            # Emergency index
            if emergency_index_path.exists():
                self.emergency_index.load(str(emergency_index_path))
                logger.info("Loaded existing emergency index")
            else:
                self._build_index(
                    self.emergency_embeddings,
                    self.emergency_index,
                    emergency_index_path
                )
                logger.info("Built new emergency index")
            
            # Treatment index
            if treatment_index_path.exists():
                self.treatment_index.load(str(treatment_index_path))
                logger.info("Loaded existing treatment index")
            else:
                self._build_index(
                    self.treatment_embeddings,
                    self.treatment_index,
                    treatment_index_path
                )
                logger.info("Built new treatment index")
                
        except Exception as e:
            logger.error(f"Failed to build/load indices: {e}")
            raise
            
    def _build_index(self, embeddings: np.ndarray, index: AnnoyIndex, 
                    save_path: Path, n_trees: int = 15) -> None:
        """
        Build and save Annoy index
        
        Args:
            embeddings: Embedding vectors
            index: AnnoyIndex instance
            save_path: Path to save the index
            n_trees: Number of trees for Annoy index (default: 15)
        """
        try:
            for i, vec in enumerate(embeddings):
                index.add_item(i, vec)
            index.build(n_trees)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            index.save(str(save_path))
            
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            raise
            
    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Perform vector search on both indices
        
        Args:
            query: Search query
            top_k: Number of results to return from each index
            
        Returns:
            Dict containing search results and metadata
        """
        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Search both indices
            emergency_results = self._search_index(
                query_embedding,
                self.emergency_index,
                self.emergency_chunks,
                "emergency",
                top_k
            )
            
            treatment_results = self._search_index(
                query_embedding,
                self.treatment_index,
                self.treatment_chunks,
                "treatment",
                top_k
            )
            
            # Log individual index results
            logger.info(f"Search results: Emergency={len(emergency_results)}, Treatment={len(treatment_results)}")
            
            results = {
                "query": query,
                "emergency_results": emergency_results,
                "treatment_results": treatment_results,
                "total_results": len(emergency_results) + len(treatment_results)
            }
            
            # Post-process results
            processed_results = self.post_process_results(results)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
            
    def _search_index(self, query_embedding: np.ndarray, index: AnnoyIndex,
                     chunks: Dict, source_type: str, top_k: int) -> List[Dict]:
        """
        Search a single index and format results
        
        Args:
            query_embedding: Query vector
            index: AnnoyIndex to search
            chunks: Chunk data
            source_type: Type of source ("emergency" or "treatment")
            top_k: Number of results to return
            
        Returns:
            List of formatted results
        """
        # Get nearest neighbors
        indices, distances = index.get_nns_by_vector(
            query_embedding, top_k, include_distances=True
        )
        
        # Format results
        results = []
        for idx, distance in zip(indices, distances):
            chunk_data = chunks[idx]  # chunks is a list, use integer index directly
            result = {
                "type": source_type,  # Using 'type' to match metadata
                "chunk_id": idx,
                "distance": distance,
                "text": chunk_data.get("text", ""),
                "matched": chunk_data.get("matched", ""),
                "matched_treatment": chunk_data.get("matched_treatment", "")
            }
            results.append(result)
            
        return results
        
    def post_process_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process search results
        - Remove duplicates
        - Sort by distance
        - Add metadata enrichment
        
        Args:
            results: Raw search results
            
        Returns:
            Processed results
        """
        try:
            emergency_results = results["emergency_results"]
            treatment_results = results["treatment_results"]
            
            # Combine all results
            all_results = emergency_results + treatment_results
            
            # Remove duplicates based on exact text matching
            unique_results = self._remove_duplicates(all_results)
            
            # Sort by distance
            sorted_results = sorted(unique_results, key=lambda x: x["distance"])
            
            return {
                "query": results["query"],
                "processed_results": sorted_results,
                "total_results": len(sorted_results),
                "processing_info": {
                    "duplicates_removed": len(all_results) - len(unique_results)
                }
            }
            
        except Exception as e:
            logger.error(f"Post-processing failed: {e}")
            raise
            
    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """
        Remove duplicate results based on exact text matching
        
        Args:
            results: List of search results
            
        Returns:
            Deduplicated results with logging statistics
        """
        original_count = len(results)
        seen_texts = set()
        unique_results = []
        
        # Sort results by distance (ascending) to keep best matches
        sorted_results = sorted(results, key=lambda x: x["distance"])
        
        logger.info(f"Deduplication: Processing {original_count} results using text matching")
        
        for result in sorted_results:
            text = result["text"]
            if text not in seen_texts:
                seen_texts.add(text)
                unique_results.append(result)
            else:
                logger.debug(f"Skipping duplicate text: {text[:50]}...")
        
        final_count = len(unique_results)
        logger.info(f"Deduplication summary: {original_count} → {final_count} results (removed {original_count - final_count})")
        
        return unique_results 

    def search_sliding_window_chunks(self, query: str, top_k: int = 5, window_size: int = 256, overlap: int = 64) -> List[Dict[str, Any]]:
        """
        Perform semantic search using sliding window chunks
        
        Args:
            query: Search query
            top_k: Number of top results to return
            window_size: Size of sliding window chunks
            overlap: Overlap between sliding windows
        
        Returns:
            List of search results with sliding window chunks
        """
        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Combine emergency and treatment chunks
            all_chunks = self.emergency_chunks + self.treatment_chunks
            all_embeddings = np.vstack([self.emergency_embeddings, self.treatment_embeddings])
            
            # Compute cosine similarities
            similarities = [
                np.dot(query_embedding, chunk_emb) / 
                (np.linalg.norm(query_embedding) * np.linalg.norm(chunk_emb))
                for chunk_emb in all_embeddings
            ]
            
            # Sort results by similarity
            sorted_indices = np.argsort(similarities)[::-1]
            
            # Prepare results
            results = []
            for idx in sorted_indices[:top_k]:
                chunk = all_chunks[idx]
                result = {
                    'text': chunk.get('text', ''),
                    'distance': similarities[idx],
                    'type': 'emergency' if idx < len(self.emergency_chunks) else 'treatment'
                }
                results.append(result)
            
            logger.info(f"Sliding window search: Found {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Sliding window search failed: {e}")
            return [] 

    def search_generic_medical_content(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Perform generic medical content search
        
        Args:
            query: Search query
            top_k: Number of top results to return
        
        Returns:
            List of search results
        """
        try:
            # re-use search_sliding_window_chunks method
            return self.search_sliding_window_chunks(query, top_k=top_k)
        except Exception as e:
            logger.error(f"Generic medical content search error: {e}")
            return [] 