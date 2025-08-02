#!/usr/bin/env python3
"""
Generate embeddings for hospital-specific documents
"""

from customization_pipeline import build_customization_embeddings

def main():
    print("🚀 Starting to build hospital-specific embeddings...")
    print("📋 Configuration:")
    print("   - Chunk size: 256 tokens")
    print("   - Chunk overlap: 25 tokens (10%)")
    print("   - Method: SentenceSplitter")
    print("   - Enhanced tag embeddings: ✅")
    print("   - Chunk embeddings: ✅")
    print("")
    
    try:
        success = build_customization_embeddings()
        
        if success:
            print("\n✅ Successfully built embeddings!")
            print("📁 Generated files in processing folder:")
            print("   - embeddings/document_index.json")
            print("   - embeddings/tag_embeddings.json") 
            print("   - embeddings/document_tag_mapping.json")
            print("   - embeddings/chunk_embeddings.json")
            print("   - indices/annoy_metadata.json")
            print("   - indices/*.ann files")
        else:
            print("\n❌ Failed to build embeddings")
            
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()