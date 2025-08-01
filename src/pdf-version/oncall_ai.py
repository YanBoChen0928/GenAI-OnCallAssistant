#!/usr/bin/env python3
"""OnCall AI - Medical RAG System (Backward Compatibility)

This file provides backward compatibility with the original rag.py interface.
Import everything from the new modular structure.
"""

import sys
from pathlib import Path

# Add pdf-version directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import all functions for backward compatibility
from models.embedding_models import load_biomedbert_model, load_meditron_model
from data.loaders import load_annotations, filter_pdf_files
from data.pdf_processing import (
    extract_pdf_text, extract_tables_from_pdf,
    extract_images_ocr_from_pdf, extract_pdf_content_enhanced
)
from indexing.document_indexer import build_document_index, split_text_into_chunks
from indexing.embedding_creator import create_text_embedding, create_tag_embeddings, create_chunk_embeddings
from indexing.storage import save_document_system, load_document_system
from retrieval.document_retriever import (
    find_relevant_documents_top_k, find_relevant_documents_top_p,
    find_relevant_documents_threshold, find_relevant_documents,
    create_document_tag_mapping
)
from retrieval.chunk_retriever import find_relevant_chunks, get_documents_for_rag, get_chunks_for_rag
from demos.demo_runner import build_medical_rag_system, demo_rag_query, demo_all_strategies

# Main function for backward compatibility
def main():
    """Main program entry compatible with original rag.py."""
    try:
        # Build the system with chunk embeddings
        build_medical_rag_system(enable_chunk_embeddings=True)
        
        # Demo chunk-based retrieval
        print("\n" + "="*80)
        print("🧩 CHUNK-BASED RETRIEVAL DEMO")
        print("="*80)
        demo_rag_query("chest pain and shortness of breath", 
                      strategy="top_p", use_chunks=True, top_p=0.8)
        
    except KeyboardInterrupt:
        print("\n\n👋 User interrupted, program exiting")
    except Exception as e:
        print(f"\n❌ Program execution error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()