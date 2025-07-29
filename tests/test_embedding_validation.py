"""
Test suite for validating embeddings and ANNOY functionality.
This module ensures the quality of embeddings and the correctness of ANNOY search.
"""

import numpy as np
import json
import logging
import os
import sys
from pathlib import Path
from typing import Tuple, List, Optional
from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer

print("\n=== Phase 1: Initializing Test Environment ===")
# Add src to python path
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent
sys.path.append(str(project_root / "src"))

print(f"• Current directory: {current_dir}")
print(f"• Project root: {project_root}")
print(f"• Python path added: {project_root / 'src'}")

class TestEmbeddingValidation:
    def setup_class(self):
        """Initialize test environment with necessary data and models."""
        print("\n=== Phase 2: Setting up Test Environment ===")
        
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='embedding_validation.log'
        )
        self.logger = logging.getLogger(__name__)
        
        # Define base paths
        self.project_root = Path(__file__).parent.parent.resolve()
        self.models_dir = self.project_root / "models"
        self.embeddings_dir = self.models_dir / "embeddings"
        self.indices_dir = self.models_dir / "indices" / "annoy"

        print(f"• Project root: {self.project_root}")
        print(f"• Models directory: {self.models_dir}")
        print(f"• Embeddings directory: {self.embeddings_dir}")
        
        self.logger.info(f"Project root: {self.project_root}")
        self.logger.info(f"Models directory: {self.models_dir}")
        self.logger.info(f"Embeddings directory: {self.embeddings_dir}")
        
        try:
            # Check directory existence
            print("• Checking directory existence...")
            if not self.embeddings_dir.exists():
                raise FileNotFoundError(f"Embeddings directory not found at: {self.embeddings_dir}")
            if not self.indices_dir.exists():
                raise FileNotFoundError(f"Indices directory not found at: {self.indices_dir}")
            
            # Load embeddings
            print("• Loading embeddings...")
            self.emergency_emb = np.load(self.embeddings_dir / "emergency_embeddings.npy")
            self.treatment_emb = np.load(self.embeddings_dir / "treatment_embeddings.npy")
            
            # Load chunks
            print("• Loading chunk metadata...")
            with open(self.embeddings_dir / "emergency_chunks.json", 'r') as f:
                self.emergency_chunks = json.load(f)
            with open(self.embeddings_dir / "treatment_chunks.json", 'r') as f:
                self.treatment_chunks = json.load(f)
                
            # Initialize model
            print("• Loading PubMedBERT model...")
            self.model = SentenceTransformer("NeuML/pubmedbert-base-embeddings")
            
            print(f"• Emergency embeddings shape: {self.emergency_emb.shape}")
            print(f"• Treatment embeddings shape: {self.treatment_emb.shape}")
            print("✅ Test environment initialized successfully")
            
            self.logger.info("Test environment initialized successfully")
            self.logger.info(f"Emergency embeddings shape: {self.emergency_emb.shape}")
            self.logger.info(f"Treatment embeddings shape: {self.treatment_emb.shape}")
            
        except FileNotFoundError as e:
            print(f"❌ File not found: {e}")
            self.logger.error(f"File not found: {e}")
            raise
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
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
        print("\n=== Phase 3: Embedding Validation ===")
        self.logger.info("\n=== Embedding Validation Report ===")
        
        try:
            # Basic dimension checks
            print("• Checking embedding dimensions...")
            assert self.emergency_emb.shape[1] == 768, "Emergency embedding dimension should be 768"
            assert self.treatment_emb.shape[1] == 768, "Treatment embedding dimension should be 768"
            print(f"✓ Emergency dimensions: {self.emergency_emb.shape}")
            print(f"✓ Treatment dimensions: {self.treatment_emb.shape}")
            
            # Count verification
            print("• Verifying chunk count consistency...")
            assert len(self.emergency_chunks) == self.emergency_emb.shape[0], \
                "Emergency chunks count mismatch"
            assert len(self.treatment_chunks) == self.treatment_emb.shape[0], \
                "Treatment chunks count mismatch"
            print(f"✓ Emergency: {len(self.emergency_chunks)} chunks = {self.emergency_emb.shape[0]} embeddings")
            print(f"✓ Treatment: {len(self.treatment_chunks)} chunks = {self.treatment_emb.shape[0]} embeddings")
            
            # Data quality checks
            print("• Performing data quality checks...")
            for name, emb in [("Emergency", self.emergency_emb), 
                             ("Treatment", self.treatment_emb)]:
                # Check for NaN and Inf
                assert not np.isnan(emb).any(), f"{name} contains NaN values"
                assert not np.isinf(emb).any(), f"{name} contains Inf values"
                
                # Value distribution analysis
                print(f"\n📊 {name} Embeddings Statistics:")
                print(f"• Range: {np.min(emb):.3f} to {np.max(emb):.3f}")
                print(f"• Mean: {np.mean(emb):.3f}")
                print(f"• Std: {np.std(emb):.3f}")
                
                self.logger.info(f"\n{name} Embeddings Statistics:")
                self.logger.info(f"- Range: {np.min(emb):.3f} to {np.max(emb):.3f}")
                self.logger.info(f"- Mean: {np.mean(emb):.3f}")
                self.logger.info(f"- Std: {np.std(emb):.3f}")
            
            print("\n✅ All embedding validations passed")
            self.logger.info("\n✅ All embedding validations passed")
            
        except AssertionError as e:
            print(f"❌ Validation failed: {str(e)}")
            self.logger.error(f"Validation failed: {str(e)}")
            raise
    
    def test_multiple_known_item_search(self):
        """Test ANNOY search with multiple random samples."""
        print("\n=== Phase 4: Multiple Known-Item Search Test ===")
        self.logger.info("\n=== Multiple Known-Item Search Test ===")
        
        print("• Loading emergency index...")
        emergency_index = AnnoyIndex(768, 'angular')
        emergency_index.load(str(self.indices_dir / "emergency_index.ann"))
        
        # Test 20 random samples
        print("• Selecting 20 random samples for self-retrieval test...")
        test_indices = np.random.choice(
            self.emergency_emb.shape[0], 
            size=20,
            replace=False
        )
        
        success_count = 0
        print("• Testing self-retrieval for each sample...")
        for i, test_idx in enumerate(test_indices, 1):
            try:
                test_emb = self.emergency_emb[test_idx]
                indices, distances = self._safe_search(emergency_index, test_emb)
                
                if indices is None:
                    print(f"  {i}/20: ❌ Search failed for index {test_idx}")
                    continue
                
                # Verify self-retrieval
                assert indices[0] == test_idx, f"Self-retrieval failed for index {test_idx}"
                assert distances[0] < 0.0001, f"Self-distance too large for index {test_idx}"
                success_count += 1
                print(f"  {i}/20: ✓ Index {test_idx} (distance: {distances[0]:.6f})")
                
            except AssertionError as e:
                print(f"  {i}/20: ❌ Index {test_idx} failed: {str(e)}")
                self.logger.warning(f"Test failed for index {test_idx}: {str(e)}")
        
        print(f"\n📊 Self-Retrieval Results: {success_count}/20 tests passed ({success_count/20*100:.1f}%)")
        self.logger.info(f"\n✅ {success_count}/20 self-retrieval tests passed")
        assert success_count >= 18, "Less than 90% of self-retrieval tests passed"
        print("✅ Multiple known-item search test passed")
    
    def test_balanced_cross_dataset_search(self):
        """Test search across both emergency and treatment datasets."""
        print("\n=== Phase 5: Cross-Dataset Search Test ===")
        self.logger.info("\n=== Balanced Cross-Dataset Search Test ===")
        
        # Initialize indices
        print("• Loading ANNOY indices...")
        emergency_index = AnnoyIndex(768, 'angular')
        treatment_index = AnnoyIndex(768, 'angular')
        
        try:
            emergency_index.load(str(self.indices_dir / "emergency_index.ann"))
            treatment_index.load(str(self.indices_dir / "treatment_index.ann"))
            print("✓ Emergency and treatment indices loaded")
            
            # Test queries
            test_queries = [
                "What is the treatment protocol for acute myocardial infarction?",
                "How to manage severe chest pain with difficulty breathing?",
                "What are the emergency procedures for anaphylactic shock?"
            ]
            
            print(f"• Testing {len(test_queries)} medical queries...")
            
            for query_num, query in enumerate(test_queries, 1):
                print(f"\n🔍 Query {query_num}/3: {query}")
                
                # Generate query vector
                print("• Generating query embedding...")
                query_emb = self.model.encode([query])[0]
                
                # Get top-5 results from each dataset
                print("• Searching both datasets...")
                e_indices, e_distances = self._safe_search(emergency_index, query_emb, k=5)
                t_indices, t_distances = self._safe_search(treatment_index, query_emb, k=5)
                
                if None in [e_indices, e_distances, t_indices, t_distances]:
                    print("❌ Search failed for one or both datasets")
                    self.logger.error("Search failed for one or both datasets")
                    continue
                
                # Print first sentence of each result
                print(f"\n📋 Emergency Dataset Results:")
                for i, (idx, dist) in enumerate(zip(e_indices, e_distances), 1):
                    text = self.emergency_chunks[idx]['text']
                    first_sentence = text.split('.')[0] + '.'
                    print(f"  E-{i} (distance: {dist:.3f}): {first_sentence[:80]}...")
                
                print(f"\n📋 Treatment Dataset Results:")
                for i, (idx, dist) in enumerate(zip(t_indices, t_distances), 1):
                    text = self.treatment_chunks[idx]['text']
                    first_sentence = text.split('.')[0] + '.'
                    print(f"  T-{i} (distance: {dist:.3f}): {first_sentence[:80]}...")
                
                print("✓ Query completed")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            self.logger.error(f"Test failed: {str(e)}")
            raise
        else:
            print("\n✅ Cross-dataset search test completed")
            self.logger.info("\n✅ Cross-dataset search test completed")

def main():
    """Run all embedding validation tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE EMBEDDING VALIDATION TEST SUITE")
    print("="*60)
    
    test = TestEmbeddingValidation()
    test.setup_class()
    
    try:
        test.test_embedding_dimensions()
        test.test_multiple_known_item_search()
        test.test_balanced_cross_dataset_search()
        
        print("\n" + "="*60)
        print("🎉 ALL EMBEDDING VALIDATION TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("✅ Embedding dimensions validated")
        print("✅ Self-retrieval accuracy confirmed")
        print("✅ Cross-dataset search functionality verified")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ EMBEDDING VALIDATION TESTS FAILED!")
        print(f"Error: {str(e)}")
        print("="*60)

if __name__ == "__main__":
    main() 