"""
Basic embedding and index validation tests
"""
# 2025-07-28
import sys
from pathlib import Path
#

import numpy as np
from annoy import AnnoyIndex
import pytest

print("\n=== Phase 1: Initializing Test Environment ===")
# add src to python path
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent
sys.path.append(str(project_root / "src"))

print(f"• Current directory: {current_dir}")
print(f"• Project root: {project_root}")
print(f"• Python path: {sys.path}")

from data_processing import DataProcessor #type: ignore


class TestEmbeddingAndIndex:
    def setup_class(self):
        """初始化測試類"""
        print("\n=== Phase 2: Setting up TestEmbeddingAndIndex ===")
        self.base_dir = Path(__file__).parent.parent.resolve()
        print(f"• Base directory: {self.base_dir}")
        self.processor = DataProcessor(base_dir=str(self.base_dir))
        print("• DataProcessor initialized")

    def test_embedding_dimensions(self):
        print("\n=== Phase 3: Testing Embedding Dimensions ===")
        print("• Loading emergency embeddings...")
        # load emergency embeddings
        emb = np.load(self.processor.models_dir / "embeddings" / "emergency_embeddings.npy")
        expected_dim = self.processor.embedding_dim
        
        print(f"• Loaded embedding shape: {emb.shape}")
        print(f"• Expected dimension: {expected_dim}")
        
        assert emb.ndim == 2, f"Expected 2D array, got {emb.ndim}D"
        assert emb.shape[1] == expected_dim, (
            f"Expected embedding dimension {expected_dim}, got {emb.shape[1]}"
        )
        print("✅ Embedding dimensions test passed")

    def test_annoy_search(self):
        print("\n=== Phase 4: Testing Annoy Search ===")
        print("• Loading embeddings...")
        # load embeddings
        emb = np.load(self.processor.models_dir / "embeddings" / "emergency_embeddings.npy")
        print(f"• Loaded embeddings shape: {emb.shape}")
        
        print("• Loading Annoy index...")
        # load Annoy index
        idx = AnnoyIndex(self.processor.embedding_dim, 'angular')
        index_path = self.processor.models_dir / "indices" / "annoy" / "emergency_index.ann"
        print(f"• Index path: {index_path}")
        idx.load(str(index_path))
        
        print("• Performing sample query...")
        # perform a sample query
        query_vec = emb[0]
        ids, distances = idx.get_nns_by_vector(query_vec, 5, include_distances=True)
        
        print(f"• Search results:")
        print(f"  - Found IDs: {ids}")
        print(f"  - Distances: {[f'{d:.4f}' for d in distances]}")
        
        assert len(ids) == 5, f"Expected 5 results, got {len(ids)}"
        assert all(0 <= d <= 2 for d in distances), "Invalid distance values"
        print("✅ Annoy search test passed")

def main():
    """Run tests manually"""
    print("\n" + "="*50)
    print("Starting Embedding and Index Tests")
    print("="*50)
    
    test = TestEmbeddingAndIndex()
    test.setup_class()  # 手動初始化
    
    try:
        test.test_embedding_dimensions()
        test.test_annoy_search()
        print("\n" + "="*50)
        print("🎉 All tests completed successfully!")
        print("="*50)
        
    except Exception as e:
        print("\n" + "="*50)
        print("❌ Tests failed!")
        print(f"Error: {str(e)}")
        print("="*50)

if __name__ == "__main__":
    main()