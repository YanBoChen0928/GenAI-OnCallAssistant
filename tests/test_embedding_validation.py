"""
Test suite for validating embeddings and ANNOY functionality.
This module ensures the quality of embeddings and the correctness of ANNOY search.
"""

import numpy as np
import json
import logging
import os
from pathlib import Path
from typing import Tuple, List, Optional
from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer

class TestEmbeddingValidation:
    def setup_class(self):
        """Initialize test environment with necessary data and models."""
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='embedding_validation.log'
        )
        self.logger = logging.getLogger(__name__)
        
        # Define base paths
        self.project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.models_dir = self.project_root / "models"
        self.embeddings_dir = self.models_dir / "embeddings"
        self.indices_dir = self.models_dir / "indices" / "annoy"

        self.logger.info(f"Project root: {self.project_root}")
        self.logger.info(f"Models directory: {self.models_dir}")
        self.logger.info(f"Embeddings directory: {self.embeddings_dir}")
        
        try:
            # Check directory existence
            if not self.embeddings_dir.exists():
                raise FileNotFoundError(f"Embeddings directory not found at: {self.embeddings_dir}")
            if not self.indices_dir.exists():
                raise FileNotFoundError(f"Indices directory not found at: {self.indices_dir}")
            
            # Load embeddings
            self.emergency_emb = np.load(self.embeddings_dir / "emergency_embeddings.npy")
            self.treatment_emb = np.load(self.embeddings_dir / "treatment_embeddings.npy")
            
            # Load chunks
            with open(self.embeddings_dir / "emergency_chunks.json", 'r') as f:
                self.emergency_chunks = json.load(f)
            with open(self.embeddings_dir / "treatment_chunks.json", 'r') as f:
                self.treatment_chunks = json.load(f)
                
            # Initialize model
            self.model = SentenceTransformer("NeuML/pubmedbert-base-embeddings")
            
            self.logger.info("Test environment initialized successfully")
            self.logger.info(f"Emergency embeddings shape: {self.emergency_emb.shape}")
            self.logger.info(f"Treatment embeddings shape: {self.treatment_emb.shape}")
            
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error during initialization: {e}")
            raise
    
    def _safe_search(
        self, 
        index: AnnoyIndex, 
        query_vector: np.ndarray, 
        k: int = 5
    ) -> Tuple[Optional[List[int]], Optional[List[float]]]:
        """Safe search wrapper with error handling"""
        try:
            indices, distances = index.get_nns_by_vector(
                query_vector, k, include_distances=True
            )
            self.logger.debug(f"Search successful: found {len(indices)} results")
            return indices, distances
            
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            return None, None
    
    def test_embedding_dimensions(self):
        """Test embedding dimensions and data quality."""
        self.logger.info("\n=== Embedding Validation Report ===")
        
        try:
            # Basic dimension checks
            assert self.emergency_emb.shape[1] == 768, "Emergency embedding dimension should be 768"
            assert self.treatment_emb.shape[1] == 768, "Treatment embedding dimension should be 768"
            
            # Count verification
            assert len(self.emergency_chunks) == self.emergency_emb.shape[0], \
                "Emergency chunks count mismatch"
            assert len(self.treatment_chunks) == self.treatment_emb.shape[0], \
                "Treatment chunks count mismatch"
            
            # Data quality checks
            for name, emb in [("Emergency", self.emergency_emb), 
                             ("Treatment", self.treatment_emb)]:
                # Check for NaN and Inf
                assert not np.isnan(emb).any(), f"{name} contains NaN values"
                assert not np.isinf(emb).any(), f"{name} contains Inf values"
                
                # Value distribution analysis
                self.logger.info(f"\n{name} Embeddings Statistics:")
                self.logger.info(f"- Range: {np.min(emb):.3f} to {np.max(emb):.3f}")
                self.logger.info(f"- Mean: {np.mean(emb):.3f}")
                self.logger.info(f"- Std: {np.std(emb):.3f}")
            
            self.logger.info("\n✅ All embedding validations passed")
            
        except AssertionError as e:
            self.logger.error(f"Validation failed: {str(e)}")
            raise
    
    def test_multiple_known_item_search(self):
        """Test ANNOY search with multiple random samples."""
        self.logger.info("\n=== Multiple Known-Item Search Test ===")
        
        emergency_index = AnnoyIndex(768, 'angular')
        emergency_index.load(str(self.indices_dir / "emergency_index.ann"))
        
        # Test 20 random samples
        test_indices = np.random.choice(
            self.emergency_emb.shape[0], 
            size=20,
            replace=False
        )
        
        success_count = 0
        for test_idx in test_indices:
            try:
                test_emb = self.emergency_emb[test_idx]
                indices, distances = self._safe_search(emergency_index, test_emb)
                
                if indices is None:
                    continue
                
                # Verify self-retrieval
                assert indices[0] == test_idx, f"Self-retrieval failed for index {test_idx}"
                assert distances[0] < 0.0001, f"Self-distance too large for index {test_idx}"
                success_count += 1
                
            except AssertionError as e:
                self.logger.warning(f"Test failed for index {test_idx}: {str(e)}")
        
        self.logger.info(f"\n✅ {success_count}/20 self-retrieval tests passed")
        assert success_count >= 18, "Less than 90% of self-retrieval tests passed"
    
    def test_balanced_cross_dataset_search(self):
        """Test search across both emergency and treatment datasets."""
        self.logger.info("\n=== Balanced Cross-Dataset Search Test ===")
        
        # Initialize indices
        emergency_index = AnnoyIndex(768, 'angular')
        treatment_index = AnnoyIndex(768, 'angular')
        
        try:
            emergency_index.load(str(self.indices_dir / "emergency_index.ann"))
            treatment_index.load(str(self.indices_dir / "treatment_index.ann"))
            
            # Test queries
            test_queries = [
                "What is the treatment protocol for acute myocardial infarction?",
                "How to manage severe chest pain with difficulty breathing?",
                "What are the emergency procedures for anaphylactic shock?"
            ]
            
            for query in test_queries:
                print(f"\n\n=== Query: {query} ===")
                
                # Generate query vector
                query_emb = self.model.encode([query])[0]
                
                # Get top-5 results from each dataset
                e_indices, e_distances = self._safe_search(emergency_index, query_emb, k=5)
                t_indices, t_distances = self._safe_search(treatment_index, query_emb, k=5)
                
                if None in [e_indices, e_distances, t_indices, t_distances]:
                    self.logger.error("Search failed for one or both datasets")
                    continue
                
                # Print first sentence of each result
                print("\nEmergency Dataset Results:")
                for i, (idx, dist) in enumerate(zip(e_indices, e_distances), 1):
                    text = self.emergency_chunks[idx]['text']
                    first_sentence = text.split('.')[0] + '.'
                    print(f"\nE-{i} (distance: {dist:.3f}):")
                    print(first_sentence)
                
                print("\nTreatment Dataset Results:")
                for i, (idx, dist) in enumerate(zip(t_indices, t_distances), 1):
                    text = self.treatment_chunks[idx]['text']
                    first_sentence = text.split('.')[0] + '.'
                    print(f"\nT-{i} (distance: {dist:.3f}):")
                    print(first_sentence)
            
        except Exception as e:
            self.logger.error(f"Test failed: {str(e)}")
            raise
        else:
            self.logger.info("\n✅ Cross-dataset search test completed")

if __name__ == "__main__":
    # Manual test execution
    test = TestEmbeddingValidation()
    test.setup_class()
    test.test_embedding_dimensions()
    test.test_multiple_known_item_search()
    test.test_balanced_cross_dataset_search() 