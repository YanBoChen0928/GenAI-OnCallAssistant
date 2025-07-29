"""
Test suite for BasicRetrievalSystem
This module tests the core retrieval functionality including:
- System initialization
- Basic search functionality
- Deduplication logic
- Result formatting
"""

import sys
import os
from pathlib import Path
import logging

print("\n=== Phase 1: Initializing Test Environment ===")
# Add src to python path
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent
sys.path.append(str(project_root / "src"))

print(f"• Current directory: {current_dir}")
print(f"• Project root: {project_root}")
print(f"• Python path added: {project_root / 'src'}")

# Change working directory to project root for file access
os.chdir(project_root)
print(f"• Changed working directory to: {project_root}")

from retrieval import BasicRetrievalSystem #type: ignore

class TestRetrievalSystem:
    """Test suite for basic retrieval system functionality"""
    
    def setup_class(self):
        """Initialize test environment"""
        print("\n=== Phase 2: Setting up Test Environment ===")
        
        # Setup logging to capture our logs
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s:%(name)s:%(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('test_retrieval.log')
            ]
        )
        
        try:
            print("• Initializing BasicRetrievalSystem...")
            self.retrieval = BasicRetrievalSystem(embedding_dim=768)
            print("✅ Retrieval system initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize retrieval system: {e}")
            raise
    
    def test_system_initialization(self):
        """Test system initialization components"""
        print("\n=== Phase 3: System Initialization Test ===")
        
        print("• Checking embedding model...")
        assert self.retrieval.embedding_model is not None, "Embedding model not loaded"
        print("✓ Embedding model loaded")
        
        print("• Checking emergency index...")
        assert self.retrieval.emergency_index is not None, "Emergency index not loaded"
        print("✓ Emergency index loaded")
        
        print("• Checking treatment index...")
        assert self.retrieval.treatment_index is not None, "Treatment index not loaded"
        print("✓ Treatment index loaded")
        
        print("• Checking chunk data...")
        assert len(self.retrieval.emergency_chunks) > 0, "Emergency chunks not loaded"
        assert len(self.retrieval.treatment_chunks) > 0, "Treatment chunks not loaded"
        print(f"✓ Emergency chunks: {len(self.retrieval.emergency_chunks)}")
        print(f"✓ Treatment chunks: {len(self.retrieval.treatment_chunks)}")
        
        print("✅ System initialization test passed")
    
    def test_basic_search_functionality(self):
        """Test basic search functionality with medical queries"""
        print("\n=== Phase 4: Basic Search Functionality Test ===")
        
        test_queries = [
            "What is the treatment for acute myocardial infarction?",
            "How to manage chest pain in emergency?",
            "Acute stroke treatment protocol"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test Query {i}/3: {query}")
            
            try:
                results = self.retrieval.search(query)
                
                # Basic structure checks
                assert "query" in results, "Query not in results"
                assert "processed_results" in results, "Processed results not found"
                assert "total_results" in results, "Total results count missing"
                
                processed_results = results["processed_results"]
                print(f"• Results returned: {len(processed_results)}")
                
                # Check result format
                for j, result in enumerate(processed_results[:3], 1):  # Check first 3
                    assert "type" in result, f"Result {j} missing 'type' field"
                    assert "text" in result, f"Result {j} missing 'text' field"
                    assert "distance" in result, f"Result {j} missing 'distance' field"
                    assert "chunk_id" in result, f"Result {j} missing 'chunk_id' field"
                    
                    print(f"  R-{j} [{result['type']}] (distance: {result['distance']:.3f}): {result['text'][:60]}...")
                
                print(f"✓ Query {i} completed successfully")
                
            except Exception as e:
                print(f"❌ Query {i} failed: {e}")
                raise
        
        print("\n✅ Basic search functionality test passed")
    
    def test_deduplication_logic(self):
        """Test the new distance-based deduplication logic"""
        print("\n=== Phase 5: Deduplication Logic Test ===")
        
        # Create test data with similar distances
        test_results = [
            {"text": "Sample text 1", "distance": 0.1, "type": "emergency", "chunk_id": 1},
            {"text": "Sample text 2", "distance": 0.105, "type": "emergency", "chunk_id": 2},  # Should be considered duplicate
            {"text": "Sample text 3", "distance": 0.2, "type": "treatment", "chunk_id": 3},
            {"text": "Sample text 4", "distance": 0.3, "type": "treatment", "chunk_id": 4}
        ]
        
        print(f"• Original results: {len(test_results)}")
        for i, result in enumerate(test_results, 1):
            print(f"  Test-{i}: distance={result['distance']}, type={result['type']}")
        
        # Test deduplication
        unique_results = self.retrieval._remove_duplicates(test_results, distance_threshold=0.1)
        
        print(f"• After deduplication: {len(unique_results)}")
        for i, result in enumerate(unique_results, 1):
            print(f"  Kept-{i}: distance={result['distance']}, type={result['type']}")
        
        # Verify deduplication worked
        assert len(unique_results) < len(test_results), "Deduplication should remove some results"
        print("✓ Distance-based deduplication working correctly")
        
        print("✅ Deduplication logic test passed")
    
    def test_result_statistics(self):
        """Test result statistics and logging"""
        print("\n=== Phase 6: Result Statistics Test ===")
        
        query = "Emergency cardiac arrest management"
        print(f"• Testing with query: {query}")
        
        # Capture logs by running search
        results = self.retrieval.search(query)
        
        # Verify we get statistics
        assert "total_results" in results, "Total results missing"
        assert "processing_info" in results, "Processing info missing"
        
        total_results = results["total_results"]
        duplicates_removed = results["processing_info"]["duplicates_removed"]
        
        print(f"• Total results: {total_results}")
        print(f"• Duplicates removed: {duplicates_removed}")
        print("✓ Statistics logging working correctly")
        
        print("✅ Result statistics test passed")

def main():
    """Run all retrieval system tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE RETRIEVAL SYSTEM TEST SUITE")
    print("="*60)
    
    test = TestRetrievalSystem()
    
    try:
        test.setup_class()
        test.test_system_initialization()
        test.test_basic_search_functionality()
        test.test_deduplication_logic()
        test.test_result_statistics()
        
        print("\n" + "="*60)
        print("🎉 ALL RETRIEVAL SYSTEM TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("✅ System initialization validated")
        print("✅ Basic search functionality confirmed")
        print("✅ Distance-based deduplication working")
        print("✅ Result statistics and logging verified")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ RETRIEVAL SYSTEM TESTS FAILED!")
        print(f"Error: {str(e)}")
        print("="*60)
        raise

if __name__ == "__main__":
    main() 