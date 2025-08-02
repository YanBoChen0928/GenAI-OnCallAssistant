#!/usr/bin/env python3
"""Test script to verify the customization pipeline with ANNOY indices."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from customization_pipeline import retrieve_document_chunks


def test_pipeline():
    """Test the complete pipeline with different queries."""
    print("🧪 Testing Customization Pipeline with ANNOY Indices")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "chest pain and shortness of breath",
        "pregnancy bleeding emergency",
        "atrial fibrillation treatment",
        "fever of unknown origin",
        "dizziness diagnostic approach"
    ]
    
    for query in test_queries:
        print(f"\n📋 Query: '{query}'")
        print("-" * 60)
        
        try:
            # Retrieve chunks
            results = retrieve_document_chunks(query, top_k=3)
            
            if results:
                print(f"✅ Found {len(results)} relevant chunks:\n")
                
                for i, result in enumerate(results, 1):
                    print(f"Result {i}:")
                    print(f"  📄 Document: {result['document']}")
                    print(f"  📊 Score: {result['score']:.4f}")
                    print(f"  📝 Chunk ID: {result['metadata']['chunk_id']}")
                    print(f"  📖 Text Preview: {result['chunk_text'][:150]}...")
                    print()
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Pipeline test completed!")


def test_specific_medical_cases():
    """Test specific medical scenarios."""
    print("\n\n🏥 Testing Specific Medical Cases")
    print("=" * 60)
    
    medical_cases = {
        "Cardiac Emergency": "acute coronary syndrome ST elevation",
        "Neurological": "stroke symptoms thrombolysis window",
        "Respiratory": "pulmonary embolism Wells score",
        "Obstetric Emergency": "eclampsia magnesium sulfate",
        "Pediatric": "pediatric seizure management"
    }
    
    for case_type, query in medical_cases.items():
        print(f"\n🔍 {case_type}: '{query}'")
        print("-" * 60)
        
        results = retrieve_document_chunks(query, top_k=2)
        
        if results:
            for result in results:
                print(f"📄 {result['document']}")
                print(f"   Score: {result['score']:.4f}")
                print(f"   Relevant content found in chunk {result['metadata']['chunk_id']}")
        else:
            print("   No specific guidance found")


def test_performance():
    """Test retrieval performance."""
    import time
    
    print("\n\n⚡ Testing Retrieval Performance")
    print("=" * 60)
    
    queries = [
        "chest pain",
        "headache emergency",
        "fever neutropenia",
        "pneumonia antibiotics",
        "atrial fibrillation"
    ]
    
    total_time = 0
    for query in queries:
        start_time = time.time()
        results = retrieve_document_chunks(query, top_k=5)
        elapsed = time.time() - start_time
        total_time += elapsed
        
        print(f"Query: '{query}' - Retrieved {len(results)} chunks in {elapsed:.3f}s")
    
    avg_time = total_time / len(queries)
    print(f"\n📊 Average retrieval time: {avg_time:.3f}s per query")


if __name__ == "__main__":
    # Run all tests
    test_pipeline()
    test_specific_medical_cases()
    test_performance()