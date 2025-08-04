#!/usr/bin/env python3
"""Customization Pipeline - Hospital-Specific Document Retrieval

This module provides the interface for hospital-specific document processing and retrieval.
"""

import sys
from pathlib import Path
from typing import List, Dict

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import necessary modules
from models.embedding_models import load_biomedbert_model
from data.loaders import load_annotations
from indexing.document_indexer import build_document_index
from indexing.embedding_creator import create_tag_embeddings, create_chunk_embeddings
from indexing.storage import save_document_system, load_document_system_with_annoy
from custom_retrieval.document_retriever import create_document_tag_mapping
from custom_retrieval.chunk_retriever import find_relevant_chunks_with_fallback


def build_customization_embeddings():
    """Build embeddings for the hospital-specific documents in the docs folder."""
    print("🏥 Building hospital-specific embeddings...")
    
    # Paths
    base_path = Path(__file__).parent
    docs_path = base_path / "docs"
    processing_path = base_path / "processing"
    
    # Load model and annotations
    embedding_model = load_biomedbert_model()
    annotations = load_annotations(file_path=str(processing_path / "mapping.json"))
    
    if not annotations:
        print("❌ Unable to load annotation data")
        return False
    
    # Build document index with chunks
    print("📄 Processing documents...")
    document_index = build_document_index(
        annotations, 
        assets_dir=str(docs_path),
        chunk_size=256, 
        chunk_overlap=25
    )
    
    # Create embeddings
    print("🔢 Creating embeddings...")
    tag_embeddings = create_tag_embeddings(embedding_model, document_index)
    doc_tag_mapping = create_document_tag_mapping(document_index, tag_embeddings)
    chunk_embeddings = create_chunk_embeddings(embedding_model, document_index)
    
    # Save everything
    print("💾 Saving to processing folder...")
    save_document_system(
        document_index,
        tag_embeddings,
        doc_tag_mapping,
        chunk_embeddings,
        output_dir=str(processing_path / "embeddings"),
        build_annoy_indices=True
    )
    
    print("✅ Embeddings built successfully!")
    return True


def retrieve_document_chunks(query: str, top_k: int = 5, llm_client=None) -> List[Dict]:
    """Retrieve relevant document chunks using two-stage ANNOY retrieval.
    
    Stage 1: Find relevant documents using tag embeddings (medical concepts)
    Stage 2: Find relevant chunks within those documents using chunk embeddings
    
    Args:
        query: The search query
        top_k: Number of chunks to retrieve
        llm_client: Optional LLM client for keyword extraction
        
    Returns:
        List of dictionaries containing chunk information
    """
    # Load model and existing embeddings
    embedding_model = load_biomedbert_model()
    
    # Load from processing folder
    processing_path = Path(__file__).parent / "processing"
    
    # Load the saved system with ANNOY indices
    document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings, annoy_manager = \
        load_document_system_with_annoy(
            input_dir=str(processing_path / "embeddings"),
            annoy_dir=str(processing_path / "indices")
        )
    
    if annoy_manager is None:
        print("❌ Failed to load ANNOY manager")
        return []
    
    # Extract medical keywords for better matching
    search_query = query
    if llm_client:
        try:
            print(f"🔍 Extracting medical keywords from: '{query}'")
            keywords = llm_client.extract_medical_keywords_for_customization(query)
            if keywords:
                search_query = " ".join(keywords)
                print(f"✅ Using keywords for search: '{search_query}'")
            else:
                print("ℹ️ No keywords extracted, using original query")
        except Exception as e:
            print(f"⚠️ Keyword extraction failed, using original query: {e}")
    else:
        print("ℹ️ No LLM client provided, using original query")
    
    # Create query embedding using processed search query
    query_embedding = embedding_model.encode(search_query)
    
    # Stage 1: Find relevant documents using tag ANNOY index
    print(f"🔍 Stage 1: Finding relevant documents for query: '{query}'")
    relevant_tags, tag_distances = annoy_manager.search_tags(
        query_embedding=query_embedding,
        n_neighbors=20,  # Get more tags to find diverse documents
        include_distances=True
    )
    
    # Get documents that contain these relevant tags
    relevant_docs = set()
    for tag in relevant_tags[:10]:  # Use top 10 tags
        for doc_name, doc_info in doc_tag_mapping.items():
            if tag in doc_info['tags']:
                relevant_docs.add(doc_name)
    
    relevant_docs = list(relevant_docs)
    print(f"✅ Found {len(relevant_docs)} relevant documents based on medical tags")
    
    if not relevant_docs:
        print("❌ No relevant documents found")
        return []
    
    # Stage 2: Find relevant chunks within these documents using proper threshold filtering
    print(f"🔍 Stage 2: Finding relevant chunks within {len(relevant_docs)} documents")
    
    # Use the proper chunk retrieval function with Top-P + minimum similarity filtering
    try:
        filtered_chunks = find_relevant_chunks_with_fallback(
            query=search_query,  # Use the processed search query (with keywords if available)
            model=embedding_model,
            relevant_docs=relevant_docs,
            chunk_embeddings=chunk_embeddings,
            annoy_manager=annoy_manager,  # Pass the ANNOY manager for accelerated search
            strategy="top_p",
            top_p=0.6,  # Top-P threshold: only include chunks that make up 60% of probability mass
            min_similarity=0.3,  # Minimum 30% similarity threshold
            similarity_metric="angular"  # Use angular similarity for consistency with ANNOY
        )
        
        if not filtered_chunks:
            print("❌ No chunks found above similarity threshold (30%)")
            return []
        
        print(f"✅ Retrieved {len(filtered_chunks)} high-quality chunks (Top-P=0.6, min_sim=0.3)")
        
        # Format results to match expected output format
        results = []
        for chunk in filtered_chunks:
            results.append({
                'document': chunk['document'],
                'chunk_text': chunk['text'],
                'score': chunk['similarity'],  # This is already a similarity score (0-1)
                'metadata': {
                    'chunk_id': chunk['chunk_id'],
                    'start_char': chunk.get('start_char', 0),
                    'end_char': chunk.get('end_char', 0)
                }
            })
        
        print(f"📊 Quality summary:")
        for i, result in enumerate(results[:3]):  # Show top 3
            print(f"  {i+1}. {result['document']} (similarity: {result['score']:.3f})")
            print(f"     Preview: {result['chunk_text'][:100]}...")
        
    except Exception as e:
        print(f"❌ Error in chunk filtering: {e}")
        print("🔄 Falling back to direct ANNOY search without filtering...")
        
        # Fallback: Direct ANNOY search (original behavior)
        chunks, chunk_distances = annoy_manager.search_chunks_in_documents(
            query_embedding=query_embedding,
            document_names=relevant_docs,
            n_neighbors=top_k,
            include_distances=True
        )
        
        # Convert ANNOY distances to cosine similarities 
        from indexing.annoy_manager import convert_angular_distance_to_cosine_similarity
        
        # Format results
        results = []
        for chunk, distance in zip(chunks, chunk_distances):
            # Convert angular distance to cosine similarity
            similarity = convert_angular_distance_to_cosine_similarity(distance)
            
            # Apply minimum similarity threshold even in fallback
            if similarity >= 0.25:  # 25% minimum threshold for fallback
                results.append({
                    'document': chunk['document'],
                    'chunk_text': chunk['text'],
                    'score': similarity,
                    'metadata': {
                        'chunk_id': chunk['chunk_id'],
                        'start_char': chunk.get('start_char', 0),
                        'end_char': chunk.get('end_char', 0)
                    }
                })
        
        if not results:
            print("❌ No chunks found above minimum similarity threshold (25%)")
            return []
        
        print(f"✅ Fallback: Retrieved {len(results)} chunks above 25% similarity")
    return results