"""
Test script for data_processing.py

This script tests the basic functionality without running the full pipeline
to ensure everything is working correctly before proceeding with embedding generation.
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.resolve() / "src"))

from data_processing import DataProcessor #type: ignore
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
# Silence urllib3 logging
logging.getLogger('urllib3').setLevel(logging.WARNING)

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
                    chunk_size=256,  # Updated to use 256 tokens
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
                    chunk_size=256,  # Updated to use 256 tokens
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
            print(f"  Emergency keywords: {sample_chunk.get('emergency_keywords', '')}")
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

def test_token_chunking():
    """Test token-based chunking functionality"""
    try:
        processor = DataProcessor()
        
        test_text = "Patient presents with acute chest pain radiating to left arm. Initial ECG shows ST elevation."
        test_keywords = "chest pain|ST elevation"
        
        chunks = processor.create_keyword_centered_chunks(
            text=test_text,
            matched_keywords=test_keywords
        )
        
        print(f"\nToken chunking test:")
        print(f"✓ Generated {len(chunks)} chunks")
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            print(f"  Primary keyword: {chunk['primary_keyword']}")
            print(f"  Content: {chunk['text']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Token chunking test failed: {e}")
        return False

def test_dual_keyword_chunks():
    """Test the enhanced dual keyword chunking functionality with token-based approach"""
    print("\n" + "="*50)
    print("TESTING DUAL KEYWORD CHUNKING")
    print("="*50)
    
    try:
        processor = DataProcessor()
        processor.load_embedding_model()  # Need tokenizer for token count verification
        
        # Test case 1: Both emergency and treatment keywords
        print("\nTest Case 1: Both Keywords")
        text = "Patient with acute MI requires immediate IV treatment. Additional chest pain symptoms require aspirin administration."
        emergency_kws = "MI|chest pain"
        treatment_kws = "IV|aspirin"
        
        chunks = processor.create_dual_keyword_chunks(
            text=text,
            emergency_keywords=emergency_kws,
            treatment_keywords=treatment_kws,
            chunk_size=256
        )
        
        # Verify chunk properties
        for i, chunk in enumerate(chunks):
            print(f"\nChunk {i+1}:")
            # Verify source type
            source_type = chunk.get('source_type')
            assert source_type in ['emergency', 'treatment'], f"Invalid source_type: {source_type}"
            print(f"• Source type: {source_type}")
            
            # Verify metadata for treatment chunks
            if source_type == 'treatment':
                contains_em = chunk.get('contains_emergency_kws', [])
                contains_tr = chunk.get('contains_treatment_kws', [])
                match_type = chunk.get('match_type')
                print(f"• Contains Emergency: {contains_em}")
                print(f"• Contains Treatment: {contains_tr}")
                print(f"• Match Type: {match_type}")
                assert match_type in ['both', 'emergency_only', 'treatment_only', 'none'], \
                    f"Invalid match_type: {match_type}"
            
            # Verify token count
            tokens = processor.tokenizer.tokenize(chunk['text'])
            token_count = len(tokens)
            print(f"• Token count: {token_count}")
            # Allow for overlap
            assert token_count <= 384, f"Chunk too large: {token_count} tokens"
            
            # Print text preview
            print(f"• Text preview: {chunk['text'][:100]}...")
        
        # Test case 2: Emergency keywords only
        print("\nTest Case 2: Emergency Only")
        text = "Patient presents with severe chest pain and dyspnea."
        emergency_kws = "chest pain"
        treatment_kws = ""
        
        chunks = processor.create_dual_keyword_chunks(
            text=text,
            emergency_keywords=emergency_kws,
            treatment_keywords=treatment_kws,
            chunk_size=256
        )
        
        assert len(chunks) > 0, "No chunks generated for emergency-only case"
        print(f"✓ Generated {len(chunks)} chunks")
        
        # Test case 3: Treatment keywords only
        print("\nTest Case 3: Treatment Only")
        text = "Administer IV fluids and monitor response."
        emergency_kws = ""
        treatment_kws = "IV"
        
        chunks = processor.create_dual_keyword_chunks(
            text=text,
            emergency_keywords=emergency_kws,
            treatment_keywords=treatment_kws,
            chunk_size=256
        )
        
        assert len(chunks) > 0, "No chunks generated for treatment-only case"
        print(f"✓ Generated {len(chunks)} chunks")
        
        print("\n✅ All dual keyword chunking tests passed")
        return True
        
    except Exception as e:
        print(f"\n❌ Dual keyword chunking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Starting data processing tests...\n")
    
    tests = [
        test_data_loading,
        test_chunking,
        test_model_loading,
        test_token_chunking,
        test_dual_keyword_chunks  # Added new test
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