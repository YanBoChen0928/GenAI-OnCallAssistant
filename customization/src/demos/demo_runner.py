"""Demo and testing functionality."""

from typing import Optional

from models.embedding_models import load_biomedbert_model
from data.loaders import load_annotations
from indexing.document_indexer import build_document_index
from indexing.embedding_creator import create_tag_embeddings, create_chunk_embeddings
from indexing.storage import save_document_system, load_document_system, load_document_system_with_annoy
from custom_retrieval.document_retriever import (
    create_document_tag_mapping, find_relevant_documents, 
    find_relevant_documents_with_fallback
)
from custom_retrieval.chunk_retriever import (
    find_relevant_chunks, get_documents_for_rag, get_chunks_for_rag,
    find_relevant_chunks_with_fallback
)


def build_medical_rag_system(enable_chunk_embeddings: bool = True):
    """Build the complete medical RAG system with document-tag indexing."""
    print("🏥 OnCall AI - Medical RAG System Starting")
    print("=" * 60)

    # Load model and data
    embedding_model = load_biomedbert_model()
    annotations = load_annotations()

    if not annotations:
        print("❌ Unable to load annotation data, exiting")
        return None, None, None, None, None

    # Build document index with sentence-based chunking
    print("\n🔄 Building document index with sentence-based chunking...")
    document_index = build_document_index(annotations, chunk_size=256, chunk_overlap=25)

    # Create tag embeddings
    print("\n🔄 Creating tag embeddings...")
    tag_embeddings = create_tag_embeddings(embedding_model, document_index)

    # Create document-tag mapping
    print("\n🔄 Creating document-tag mapping...")
    doc_tag_mapping = create_document_tag_mapping(document_index, tag_embeddings)

    # Create chunk embeddings if enabled
    chunk_embeddings = None
    if enable_chunk_embeddings:
        print("\n🔄 Creating chunk embeddings...")
        chunk_embeddings = create_chunk_embeddings(embedding_model, document_index)

    # Save the system
    print("\n💾 Saving document system...")
    save_document_system(document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings)

    print("\n✅ Medical RAG system built successfully!")
    return embedding_model, document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings


def demo_rag_query(query: str = "chest pain and shortness of breath", 
                  strategy: str = "top_p", use_chunks: bool = True, **kwargs):
    """Demo RAG query functionality with different selection strategies."""
    print(f"\n🔍 Demo Query: '{query}' (Strategy: {strategy}, Use chunks: {use_chunks})")
    print("=" * 60)
    
    # Try to load existing system first
    load_result = load_document_system()
    if len(load_result) == 4:
        document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings = load_result
    else:
        document_index, tag_embeddings, doc_tag_mapping = load_result[:3]
        chunk_embeddings = None
    
    if document_index is None:
        print("📦 No saved system found, building new one...")
        build_result = build_medical_rag_system(enable_chunk_embeddings=use_chunks)
        if build_result[0] is None:
            return
        embedding_model, document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings = build_result
    else:
        embedding_model = load_biomedbert_model()
    
    # Find relevant documents using specified strategy
    relevant_docs = find_relevant_documents(
        query, embedding_model, tag_embeddings, doc_tag_mapping, 
        strategy=strategy, **kwargs
    )
    
    if use_chunks and chunk_embeddings:
        # Find relevant chunks within the selected documents
        print(f"\n🔍 Finding relevant chunks within selected documents...")
        relevant_chunks = find_relevant_chunks(
            query, embedding_model, relevant_docs, chunk_embeddings, top_chunks_per_doc=3
        )
        
        # Get chunks for RAG
        rag_content = get_chunks_for_rag(relevant_chunks, max_chunks=10)
        print(f"\n📋 Ready for RAG with {len(rag_content)} chunks")
        
    else:
        # Get full documents for RAG
        rag_content = get_documents_for_rag(relevant_docs, document_index)
        print(f"\n📋 Ready for RAG with {len(rag_content)} full documents")
    
    print("Next step: Feed this content to your LLM for answer generation")
    return rag_content


def demo_all_strategies(query: str = "chest pain and shortness of breath"):
    """Demo all selection strategies for comparison."""
    print(f"\n🔬 Comparing All Selection Strategies")
    print("=" * 80)
    
    # Load system
    document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings = load_document_system()
    if document_index is None:
        print("📦 Building system first...")
        embedding_model, document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings = build_medical_rag_system()
        if document_index is None:
            return
    else:
        embedding_model = load_biomedbert_model()
    
    strategies = [
        ("top_k", {"top_k": 3}),
        ("top_p", {"top_p": 0.8, "min_similarity": 0.3}),
        ("threshold", {"similarity_threshold": 0.5})
    ]
    
    results = {}
    for strategy, params in strategies:
        print(f"\n{'='*20} {strategy.upper()} Strategy {'='*20}")
        relevant_docs = find_relevant_documents(
            query, embedding_model, tag_embeddings, doc_tag_mapping,
            strategy=strategy, **params
        )
        results[strategy] = relevant_docs
    
    # Summary comparison
    print(f"\n📊 Strategy Comparison Summary:")
    print("-" * 50)
    for strategy, docs in results.items():
        print(f"{strategy:>10}: {len(docs)} documents selected")
    
    return results


def demo_rag_query_with_annoy(query: str = "chest pain and shortness of breath", 
                             strategy: str = "top_p", use_chunks: bool = True, **kwargs):
    """Demo RAG query functionality with ANNOY acceleration."""
    print(f"\n🚀 Demo ANNOY Query: '{query}' (Strategy: {strategy}, Use chunks: {use_chunks})")
    print("=" * 80)
    
    # Try to load existing system with ANNOY
    document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings, annoy_manager = load_document_system_with_annoy()
    
    if document_index is None:
        print("📦 No saved system found, building new one...")
        build_result = build_medical_rag_system(enable_chunk_embeddings=use_chunks)
        if build_result[0] is None:
            return
        embedding_model, document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings = build_result
        
        # Try to load ANNOY manager after building
        from indexing.storage import load_annoy_manager
        annoy_manager = load_annoy_manager()
    else:
        embedding_model = load_biomedbert_model()
    
    print(f"🔧 ANNOY Status: {'Available' if annoy_manager else 'Not available (using fallback)'}")
    
    # Find relevant documents using ANNOY-accelerated method with fallback
    print(f"\n🔍 Finding relevant documents...")
    import time
    start_time = time.time()
    
    relevant_docs = find_relevant_documents_with_fallback(
        query, embedding_model, tag_embeddings, doc_tag_mapping,
        annoy_manager=annoy_manager, strategy=strategy, **kwargs
    )
    
    doc_search_time = time.time() - start_time
    print(f"⏱️ Document search completed in {doc_search_time:.4f}s")
    
    if use_chunks and chunk_embeddings:
        # Find relevant chunks using ANNOY-accelerated method with fallback
        print(f"\n🔍 Finding relevant chunks within selected documents...")
        start_time = time.time()
        
        relevant_chunks = find_relevant_chunks_with_fallback(
            query, embedding_model, relevant_docs, chunk_embeddings,
            annoy_manager=annoy_manager, strategy=strategy, 
            top_chunks_per_doc=3, **kwargs
        )
        
        chunk_search_time = time.time() - start_time
        print(f"⏱️ Chunk search completed in {chunk_search_time:.4f}s")
        
        # Get chunks for RAG
        rag_content = get_chunks_for_rag(relevant_chunks, max_chunks=10)
        print(f"\n📋 Ready for RAG with {len(rag_content)} chunks")
        
        total_time = doc_search_time + chunk_search_time
        print(f"🏁 Total search time: {total_time:.4f}s")
        
    else:
        # Get full documents for RAG
        rag_content = get_documents_for_rag(relevant_docs, document_index)
        print(f"\n📋 Ready for RAG with {len(rag_content)} full documents")
        print(f"🏁 Total search time: {doc_search_time:.4f}s")
    
    return rag_content


def demo_performance_comparison(query: str = "chest pain and shortness of breath"):
    """Demo performance comparison between original and ANNOY methods."""
    print(f"\n⚡ Performance Comparison Demo")
    print("=" * 80)
    print(f"Query: '{query}'")
    
    # Load system with ANNOY
    document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings, annoy_manager = load_document_system_with_annoy()
    
    if document_index is None:
        print("❌ No saved system found")
        return
    
    embedding_model = load_biomedbert_model()
    strategy = "top_p"
    strategy_params = {"top_p": 0.8, "min_similarity": 0.3}
    
    print(f"\n📊 Testing document retrieval performance...")
    
    # Test original method
    import time
    start_time = time.time()
    original_docs = find_relevant_documents(
        query, embedding_model, tag_embeddings, doc_tag_mapping, 
        strategy=strategy, **strategy_params
    )
    original_time = time.time() - start_time
    
    # Test ANNOY method (with fallback)
    start_time = time.time()
    annoy_docs = find_relevant_documents_with_fallback(
        query, embedding_model, tag_embeddings, doc_tag_mapping,
        annoy_manager=annoy_manager, strategy=strategy, **strategy_params
    )
    annoy_time = time.time() - start_time
    
    # Results
    print(f"🔍 Original method: {len(original_docs)} docs in {original_time:.4f}s")
    print(f"🚀 ANNOY method: {len(annoy_docs)} docs in {annoy_time:.4f}s")
    
    if annoy_time > 0:
        speedup = original_time / annoy_time
        print(f"⚡ Speedup: {speedup:.2f}x")
    
    # Check result similarity
    if original_docs and annoy_docs:
        overlap = set(original_docs) & set(annoy_docs)
        print(f"📊 Result overlap: {len(overlap)}/{len(original_docs)} documents")
    
    # Test chunk retrieval if available
    if chunk_embeddings and len(original_docs) > 0:
        print(f"\n📊 Testing chunk retrieval performance...")
        relevant_docs = original_docs[:2]  # Test with first 2 documents
        
        # Original method
        start_time = time.time()
        original_chunks = find_relevant_chunks(
            query, embedding_model, relevant_docs, chunk_embeddings, 
            strategy=strategy, **strategy_params
        )
        original_chunk_time = time.time() - start_time
        
        # ANNOY method (with fallback)
        start_time = time.time()
        annoy_chunks = find_relevant_chunks_with_fallback(
            query, embedding_model, relevant_docs, chunk_embeddings,
            annoy_manager=annoy_manager, strategy=strategy, **strategy_params
        )
        annoy_chunk_time = time.time() - start_time
        
        print(f"🔍 Original chunks: {len(original_chunks)} chunks in {original_chunk_time:.4f}s")
        print(f"🚀 ANNOY chunks: {len(annoy_chunks)} chunks in {annoy_chunk_time:.4f}s")
        
        if annoy_chunk_time > 0:
            chunk_speedup = original_chunk_time / annoy_chunk_time
            print(f"⚡ Chunk speedup: {chunk_speedup:.2f}x")
    
    print(f"\n✅ Performance comparison completed!")