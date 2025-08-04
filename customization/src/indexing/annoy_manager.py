"""ANNOY index management for PDF-based RAG system."""

import os
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import logging

try:
    from annoy import AnnoyIndex
except ImportError:
    raise ImportError("annoy package is required. Install with: pip install annoy")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnnoyIndexManager:
    """Manages ANNOY indices for fast vector similarity search."""
    
    def __init__(self, embedding_dim: int = 1024, metric: str = 'angular'):
        """
        Initialize ANNOY index manager.
        
        Args:
            embedding_dim: Dimension of embeddings (1024 for BGE Large Medical)
            metric: Distance metric ('angular' for cosine similarity, 'euclidean', 'manhattan', 'hamming', 'dot')
        """
        self.embedding_dim = embedding_dim
        self.metric = metric
        self.tag_index = None
        self.chunk_index = None
        self.tag_to_id_mapping = {}
        self.id_to_tag_mapping = {}
        self.chunk_to_id_mapping = {}
        self.id_to_chunk_mapping = {}
        
        logger.info(f"Initialized AnnoyIndexManager: dim={embedding_dim}, metric={metric}")
    
    def build_tag_index(self, tag_embeddings: Dict[str, np.ndarray], n_trees: int = 50) -> AnnoyIndex:
        """
        Build ANNOY index for tag embeddings.
        
        Args:
            tag_embeddings: Dictionary mapping tags to their embeddings
            n_trees: Number of trees (more trees = better precision, slower build)
            
        Returns:
            Built ANNOY index
        """
        logger.info(f"Building tag ANNOY index with {len(tag_embeddings)} tags...")
        
        # Create index
        self.tag_index = AnnoyIndex(self.embedding_dim, self.metric)
        
        # Create mappings
        self.tag_to_id_mapping = {}
        self.id_to_tag_mapping = {}
        
        # Add embeddings to index
        for tag_id, (tag, embedding) in enumerate(tag_embeddings.items()):
            self.tag_index.add_item(tag_id, embedding)
            self.tag_to_id_mapping[tag] = tag_id
            self.id_to_tag_mapping[tag_id] = tag
        
        # Build index
        logger.info(f"Building index with {n_trees} trees...")
        self.tag_index.build(n_trees)
        
        logger.info(f"✅ Tag ANNOY index built successfully: {len(tag_embeddings)} tags")
        return self.tag_index
    
    def build_chunk_index(self, chunk_embeddings: Dict[str, List[Dict]], n_trees: int = 50) -> AnnoyIndex:
        """
        Build ANNOY index for chunk embeddings.
        
        Args:
            chunk_embeddings: Dictionary mapping document names to lists of chunk dictionaries
            n_trees: Number of trees
            
        Returns:
            Built ANNOY index
        """
        # Count total chunks
        total_chunks = sum(len(chunks) for chunks in chunk_embeddings.values())
        logger.info(f"Building chunk ANNOY index with {total_chunks} chunks...")
        
        # Create index
        self.chunk_index = AnnoyIndex(self.embedding_dim, self.metric)
        
        # Create mappings
        self.chunk_to_id_mapping = {}
        self.id_to_chunk_mapping = {}
        
        chunk_id = 0
        for doc_name, chunks in chunk_embeddings.items():
            for chunk in chunks:
                # Create unique chunk identifier
                chunk_key = f"{doc_name}#{chunk['chunk_id']}"
                
                # Add to index
                self.chunk_index.add_item(chunk_id, chunk['embedding'])
                
                # Create mappings
                self.chunk_to_id_mapping[chunk_key] = chunk_id
                self.id_to_chunk_mapping[chunk_id] = {
                    'document': doc_name,
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk['text'],
                    'start_char': chunk.get('start_char', 0),
                    'end_char': chunk.get('end_char', len(chunk['text'])),
                    'token_count': chunk.get('token_count', len(chunk['text'].split())),
                    'chunk_key': chunk_key
                }
                
                chunk_id += 1
        
        # Build index
        logger.info(f"Building chunk index with {n_trees} trees...")
        self.chunk_index.build(n_trees)
        
        logger.info(f"✅ Chunk ANNOY index built successfully: {total_chunks} chunks")
        return self.chunk_index
    
    def save_indices(self, output_dir: Union[str, Path]):
        """
        Save ANNOY indices and mappings to disk.
        
        Args:
            output_dir: Directory to save indices
        """
        output_dir = Path(output_dir)
        # Save indices at the same level as embeddings, not inside embeddings
        indices_dir = output_dir.parent / 'indices'
        indices_dir.mkdir(exist_ok=True)
        
        # Save tag index
        if self.tag_index is not None:
            tag_index_path = indices_dir / 'tag_embeddings.ann'
            self.tag_index.save(str(tag_index_path))
            
            # Save tag mappings
            tag_mappings_path = indices_dir / 'tag_mappings.json'
            with open(tag_mappings_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'tag_to_id': self.tag_to_id_mapping,
                    'id_to_tag': self.id_to_tag_mapping
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Tag index saved: {tag_index_path}")
        
        # Save chunk index
        if self.chunk_index is not None:
            chunk_index_path = indices_dir / 'chunk_embeddings.ann'
            self.chunk_index.save(str(chunk_index_path))
            
            # Save chunk mappings
            chunk_mappings_path = indices_dir / 'chunk_mappings.json'
            with open(chunk_mappings_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'chunk_to_id': self.chunk_to_id_mapping,
                    'id_to_chunk': self.id_to_chunk_mapping
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Chunk index saved: {chunk_index_path}")
        
        # Save index metadata
        metadata_path = indices_dir / 'annoy_metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'embedding_dim': self.embedding_dim,
                'metric': self.metric,
                'tag_index_exists': self.tag_index is not None,
                'chunk_index_exists': self.chunk_index is not None,
                'num_tags': len(self.tag_to_id_mapping),
                'num_chunks': len(self.chunk_to_id_mapping)
            }, f, indent=2)
        
        logger.info(f"✅ ANNOY indices saved to: {indices_dir}")
    
    def load_indices(self, input_dir: Union[str, Path]) -> bool:
        """
        Load ANNOY indices and mappings from disk.
        
        Args:
            input_dir: Directory containing saved indices
            
        Returns:
            True if successfully loaded, False otherwise
        """
        input_dir = Path(input_dir)
        # Load indices from the same level as embeddings, not inside embeddings
        indices_dir = input_dir.parent / 'indices'
        
        if not indices_dir.exists():
            logger.warning(f"Indices directory not found: {indices_dir}")
            return False
        
        try:
            # Load metadata
            metadata_path = indices_dir / 'annoy_metadata.json'
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                self.embedding_dim = metadata['embedding_dim']
                self.metric = metadata['metric']
                logger.info(f"Loaded metadata: dim={self.embedding_dim}, metric={self.metric}")
            
            # Load tag index
            tag_index_path = indices_dir / 'tag_embeddings.ann'
            tag_mappings_path = indices_dir / 'tag_mappings.json'
            
            if tag_index_path.exists() and tag_mappings_path.exists():
                self.tag_index = AnnoyIndex(self.embedding_dim, self.metric)
                self.tag_index.load(str(tag_index_path))
                
                with open(tag_mappings_path, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
                    self.tag_to_id_mapping = mappings['tag_to_id']
                    self.id_to_tag_mapping = {int(k): v for k, v in mappings['id_to_tag'].items()}
                
                logger.info(f"✅ Tag index loaded: {len(self.tag_to_id_mapping)} tags")
            
            # Load chunk index
            chunk_index_path = indices_dir / 'chunk_embeddings.ann'
            chunk_mappings_path = indices_dir / 'chunk_mappings.json'
            
            if chunk_index_path.exists() and chunk_mappings_path.exists():
                self.chunk_index = AnnoyIndex(self.embedding_dim, self.metric)
                self.chunk_index.load(str(chunk_index_path))
                
                with open(chunk_mappings_path, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
                    self.chunk_to_id_mapping = mappings['chunk_to_id']
                    self.id_to_chunk_mapping = {int(k): v for k, v in mappings['id_to_chunk'].items()}
                
                logger.info(f"✅ Chunk index loaded: {len(self.chunk_to_id_mapping)} chunks")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load ANNOY indices: {e}")
            return False
    
    def search_tags(self, query_embedding: np.ndarray, n_neighbors: int = 10, 
                   include_distances: bool = True) -> Union[List[str], Tuple[List[str], List[float]]]:
        """
        Search for similar tags using ANNOY index.
        
        Args:
            query_embedding: Query embedding vector
            n_neighbors: Number of nearest neighbors to return
            include_distances: Whether to return distances
            
        Returns:
            List of tag names, or tuple of (tag_names, distances)
        """
        if self.tag_index is None:
            raise ValueError("Tag index not built or loaded")
        
        # Search using ANNOY
        if include_distances:
            neighbor_ids, distances = self.tag_index.get_nns_by_vector(
                query_embedding, n_neighbors, include_distances=True
            )
        else:
            neighbor_ids = self.tag_index.get_nns_by_vector(
                query_embedding, n_neighbors, include_distances=False
            )
        
        # Convert IDs to tag names
        tag_names = [self.id_to_tag_mapping[neighbor_id] for neighbor_id in neighbor_ids]
        
        if include_distances:
            return tag_names, distances
        else:
            return tag_names
    
    def search_chunks(self, query_embedding: np.ndarray, n_neighbors: int = 10,
                     include_distances: bool = True) -> Union[List[Dict], Tuple[List[Dict], List[float]]]:
        """
        Search for similar chunks using ANNOY index.
        
        Args:
            query_embedding: Query embedding vector
            n_neighbors: Number of nearest neighbors to return
            include_distances: Whether to return distances
            
        Returns:
            List of chunk dictionaries, or tuple of (chunks, distances)
        """
        if self.chunk_index is None:
            raise ValueError("Chunk index not built or loaded")
        
        # Search using ANNOY
        if include_distances:
            neighbor_ids, distances = self.chunk_index.get_nns_by_vector(
                query_embedding, n_neighbors, include_distances=True
            )
        else:
            neighbor_ids = self.chunk_index.get_nns_by_vector(
                query_embedding, n_neighbors, include_distances=False
            )
        
        # Convert IDs to chunk info
        chunks = [self.id_to_chunk_mapping[neighbor_id] for neighbor_id in neighbor_ids]
        
        if include_distances:
            return chunks, distances
        else:
            return chunks
    
    def search_chunks_in_documents(self, query_embedding: np.ndarray, 
                                  document_names: List[str], n_neighbors: int = 10,
                                  include_distances: bool = True) -> Union[List[Dict], Tuple[List[Dict], List[float]]]:
        """
        Search for similar chunks within specific documents.
        
        Args:
            query_embedding: Query embedding vector
            document_names: List of document names to search within
            n_neighbors: Number of nearest neighbors to return
            include_distances: Whether to return distances
            
        Returns:
            List of chunk dictionaries, or tuple of (chunks, distances)
        """
        if self.chunk_index is None:
            raise ValueError("Chunk index not built or loaded")
        
        # Get more candidates than needed since we'll filter by document
        search_candidates = min(n_neighbors * 5, len(self.id_to_chunk_mapping))
        
        # Search using ANNOY
        if include_distances:
            candidate_ids, distances = self.chunk_index.get_nns_by_vector(
                query_embedding, search_candidates, include_distances=True
            )
        else:
            candidate_ids = self.chunk_index.get_nns_by_vector(
                query_embedding, search_candidates, include_distances=False
            )
        
        # Filter by document names and take top n_neighbors
        filtered_chunks = []
        filtered_distances = [] if include_distances else None
        
        for i, candidate_id in enumerate(candidate_ids):
            chunk_info = self.id_to_chunk_mapping[candidate_id]
            if chunk_info['document'] in document_names:
                filtered_chunks.append(chunk_info)
                if include_distances:
                    filtered_distances.append(distances[i])
                
                if len(filtered_chunks) >= n_neighbors:
                    break
        
        if include_distances:
            return filtered_chunks, filtered_distances
        else:
            return filtered_chunks
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the loaded indices."""
        stats = {
            'embedding_dim': self.embedding_dim,
            'metric': self.metric,
            'tag_index_loaded': self.tag_index is not None,
            'chunk_index_loaded': self.chunk_index is not None,
            'num_tags': len(self.tag_to_id_mapping) if self.tag_index else 0,
            'num_chunks': len(self.chunk_to_id_mapping) if self.chunk_index else 0
        }
        return stats


def convert_angular_distance_to_cosine_similarity(angular_distance: float) -> float:
    """
    Convert ANNOY angular distance to cosine similarity.
    
    Args:
        angular_distance: Angular distance from ANNOY (Euclidean distance between normalized vectors)
        
    Returns:
        Cosine similarity (-1 to 1)
    """
    # ANNOY angular distance is the Euclidean distance between normalized vectors
    # For normalized vectors: ||u - v||² = ||u||² + ||v||² - 2⟨u,v⟩ = 2 - 2⟨u,v⟩
    # Therefore: cosine_similarity = ⟨u,v⟩ = 1 - (angular_distance² / 2)
    return 1 - (angular_distance ** 2 / 2)