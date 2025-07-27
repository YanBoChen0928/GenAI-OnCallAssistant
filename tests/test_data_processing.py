"""
Test script for data_processing.py

This script tests the basic functionality without running the full pipeline
to ensure everything is working correctly before proceeding with embedding generation.
"""

import sys
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.resolve() / "src"))

from data_processing import DataProcessor
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_loading():
    """Test data loading functionality"""
    print("="*50)
    print("TESTING DATA LOADING")
    print("="*50)
    
    try:
        # Initialize processor with explicit base directory
        base_dir = Path(__file__).parent.parent.resolve()
        processor = DataProcessor(base_dir=str(base_dir))
        
        # Test data loading
        emergency_data, treatment_data = processor.load_filtered_data()
        
        print(f"✅ Emergency data loaded: {len(emergency_data)} records")
        print(f"✅ Treatment data loaded: {len(treatment_data)} records")
        
        # Check data structure
        print("\nEmergency data columns:", list(emergency_data.columns))
        print("Treatment data columns:", list(treatment_data.columns))
        
        # Show sample data
        if len(emergency_data) > 0:
            print(f"\nSample emergency matched keywords: {emergency_data['matched'].iloc[0]}")
        
        if len(treatment_data) > 0:
            print(f"Sample treatment matched keywords: {treatment_data['treatment_matched'].iloc[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def test_chunking():
    """Test chunking functionality"""
    print("\n" + "="*50)
    print("TESTING CHUNKING FUNCTIONALITY")
    print("="*50)
    
    try:
        # Initialize processor
        processor = DataProcessor()
        
        # Load data
        processor.load_filtered_data()
        
        # Test emergency chunking (just first few records)
        print("Testing emergency chunking...")
        emergency_chunks = []
        for idx, row in processor.emergency_data.head(3).iterrows():
            if pd.notna(row.get('clean_text')) and pd.notna(row.get('matched')):
                chunks = processor.create_keyword_centered_chunks(
                    text=row['clean_text'],
                    matched_keywords=row['matched'],
                    chunk_size=512,
                    doc_id=str(row.get('id', idx))
                )
                emergency_chunks.extend(chunks)
        
        print(f"✅ Generated {len(emergency_chunks)} emergency chunks from 3 records")
        
        # Test treatment chunking (just first few records)
        print("Testing treatment chunking...")
        treatment_chunks = []
        for idx, row in processor.treatment_data.head(3).iterrows():
            if (pd.notna(row.get('clean_text')) and 
                pd.notna(row.get('treatment_matched'))):
                chunks = processor.create_dual_keyword_chunks(
                    text=row['clean_text'],
                    emergency_keywords=row.get('matched', ''),
                    treatment_keywords=row['treatment_matched'],
                    chunk_size=512,
                    doc_id=str(row.get('id', idx))
                )
                treatment_chunks.extend(chunks)
        
        print(f"✅ Generated {len(treatment_chunks)} treatment chunks from 3 records")
        
        # Show sample chunk
        if emergency_chunks:
            sample_chunk = emergency_chunks[0]
            print(f"\nSample emergency chunk:")
            print(f"  Primary keyword: {sample_chunk['primary_keyword']}")
            print(f"  Text length: {len(sample_chunk['text'])}")
            print(f"  Text preview: {sample_chunk['text'][:100]}...")
        
        if treatment_chunks:
            sample_chunk = treatment_chunks[0]
            print(f"\nSample treatment chunk:")
            print(f"  Primary keyword: {sample_chunk['primary_keyword']}")
            print(f"  Emergency keywords: {sample_chunk['emergency_keywords']}")
            print(f"  Text length: {len(sample_chunk['text'])}")
            print(f"  Text preview: {sample_chunk['text'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Chunking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_loading():
    """Test if we can load the embedding model"""
    print("\n" + "="*50)
    print("TESTING MODEL LOADING")
    print("="*50)
    
    try:
        processor = DataProcessor()
        
        print("Loading NeuML/pubmedbert-base-embeddings...")
        model = processor.load_embedding_model()
        
        print(f"✅ Model loaded successfully: {processor.embedding_model_name}")
        print(f"✅ Model max sequence length: {model.max_seq_length}")
        
        # Test a simple encoding
        test_text = "Patient presents with chest pain and shortness of breath."
        embedding = model.encode([test_text])
        
        print(f"✅ Test embedding shape: {embedding.shape}")
        print(f"✅ Expected dimension: {processor.embedding_dim}")
        
        assert embedding.shape[1] == processor.embedding_dim, f"Dimension mismatch: {embedding.shape[1]} != {processor.embedding_dim}"
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Starting data processing tests...\n")
    
    # Import pandas here since it's used in chunking test
    import pandas as pd
    
    tests = [
        test_data_loading,
        test_chunking,
        test_model_loading
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i}. {test.__name__}: {status}")
    
    all_passed = all(results)
    
    if all_passed:
        print("\n🎉 All tests passed! Ready to proceed with full pipeline.")
        print("\nTo run the full data processing pipeline:")
        print("cd FinalProject && python src/data_processing.py")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main() 