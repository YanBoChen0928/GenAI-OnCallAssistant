#!/usr/bin/env python3
"""
Quick script to generate new embeddings with sentence-based chunking
"""

import sys
from pathlib import Path

# Add pdf-version directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from demos.demo_runner import build_medical_rag_system

def main():
    print("🚀 Starting to build medical RAG system with new sentence-based chunking...")
    print("📋 Configuration:")
    print("   - Chunk size: 256 tokens")
    print("   - Chunk overlap: 25 tokens (10%)")
    print("   - Method: SentenceSplitter")
    print("   - Enhanced tag embeddings: ✅")
    print("   - Chunk embeddings: ✅")
    print("")
    
    try:
        result = build_medical_rag_system(enable_chunk_embeddings=True)
        
        if result[0] is not None:
            print("✅ Successfully built medical RAG system!")
            print("📁 Generated files:")
            print("   - document_index.json")
            print("   - tag_embeddings.json") 
            print("   - document_tag_mapping.json")
            print("   - chunk_embeddings.json")
        else:
            print("❌ Failed to build system")
            
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()