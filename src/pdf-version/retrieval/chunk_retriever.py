"""Chunk-level retrieval functionality."""

from typing import List, Dict, Callable
import numpy as np
from sentence_transformers import SentenceTransformer
from src.indexing.embedding_creator import create_text_embedding


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def dot_product_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate dot product similarity for normalized vectors."""
    # For normalized vectors (like BGE embeddings), dot product = cosine similarity
    # This is computationally more efficient than cosine similarity
    return np.dot(vec1, vec2)


# Similarity function registry
SIMILARITY_FUNCTIONS = {
    "cosine": cosine_similarity,
    "dot_product": dot_product_similarity
}


def find_relevant_chunks_top_k(query: str, model: SentenceTransformer, 
                              relevant_docs: List[str], chunk_embeddings: Dict, 
                              top_chunks_per_doc: int = 3, 
                              similarity_metric: str = "cosine") -> List[Dict]:
    """Find most relevant chunks using Top-K strategy (original method)."""
    query_embedding = create_text_embedding(model, query)
    
    all_relevant_chunks = []
    
    for doc_name in relevant_docs:
        if doc_name not in chunk_embeddings:
            continue
            
        doc_chunks = chunk_embeddings[doc_name]
        chunk_similarities = []
        
        # Get similarity function
        similarity_func = SIMILARITY_FUNCTIONS.get(similarity_metric, cosine_similarity)
        
        # Calculate similarity for each chunk in this document
        for chunk_info in doc_chunks:
            chunk_embedding = chunk_info['embedding']
            similarity = similarity_func(query_embedding, chunk_embedding)
            
            chunk_similarities.append({
                'document': doc_name,
                'chunk_id': chunk_info['chunk_id'],
                'text': chunk_info['text'],
                'start_char': chunk_info.get('start_char', 0),
                'end_char': chunk_info.get('end_char', len(chunk_info['text'])),
                'token_count': chunk_info.get('token_count', len(chunk_info['text'].split())),
                'similarity': similarity
            })
        
        # Get top chunks from this document
        chunk_similarities.sort(key=lambda x: x['similarity'], reverse=True)
        top_chunks = chunk_similarities[:top_chunks_per_doc]
        all_relevant_chunks.extend(top_chunks)
    
    # Sort all chunks by similarity
    all_relevant_chunks.sort(key=lambda x: x['similarity'], reverse=True)
    
    print(f"🔍 Found {len(all_relevant_chunks)} relevant chunks (Top-K)")
    for i, chunk in enumerate(all_relevant_chunks[:5]):  # Show top 5
        print(f"  {i+1}. {chunk['document']} (chunk {chunk['chunk_id']}, similarity: {chunk['similarity']:.3f})")
        print(f"     Preview: {chunk['text'][:100]}...")
    
    return all_relevant_chunks


def find_relevant_chunks_top_p(query: str, model: SentenceTransformer,
                              relevant_docs: List[str], chunk_embeddings: Dict,
                              top_p: float = 0.6, min_similarity: float = 0.3,
                              similarity_metric: str = "cosine") -> List[Dict]:
    """Find most relevant chunks using Top-P strategy for better quality control."""
    query_embedding = create_text_embedding(model, query)
    
    # Collect all chunks from all relevant documents
    all_chunk_similarities = []
    
    for doc_name in relevant_docs:
        if doc_name not in chunk_embeddings:
            continue
            
        doc_chunks = chunk_embeddings[doc_name]
        
        # Get similarity function
        similarity_func = SIMILARITY_FUNCTIONS.get(similarity_metric, cosine_similarity)
        
        # Calculate similarity for each chunk in this document
        for chunk_info in doc_chunks:
            chunk_embedding = chunk_info['embedding']
            similarity = similarity_func(query_embedding, chunk_embedding)
            
            # Only include chunks above minimum similarity threshold
            if similarity >= min_similarity:
                all_chunk_similarities.append({
                    'document': doc_name,
                    'chunk_id': chunk_info['chunk_id'],
                    'text': chunk_info['text'],
                    'start_char': chunk_info.get('start_char', 0),
                    'end_char': chunk_info.get('end_char', len(chunk_info['text'])),
                    'token_count': chunk_info.get('token_count', len(chunk_info['text'].split())),
                    'similarity': similarity
                })
    
    if not all_chunk_similarities:
        print(f"⚠️ No chunks found above similarity threshold {min_similarity}")
        return []
    
    # Sort by similarity
    all_chunk_similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Apply Top-P selection
    total_score = sum(chunk['similarity'] for chunk in all_chunk_similarities)
    cumulative_prob = 0.0
    selected_chunks = []
    
    for chunk in all_chunk_similarities:
        prob = chunk['similarity'] / total_score
        cumulative_prob += prob
        selected_chunks.append(chunk)
        
        # Stop when we reach the Top-P threshold
        if cumulative_prob >= top_p:
            break
    
    print(f"🔍 Found {len(selected_chunks)} relevant chunks (Top-P={top_p})")
    print(f"📊 Filtered from {len(all_chunk_similarities)} chunks above threshold")
    print(f"📊 Cumulative probability: {cumulative_prob:.3f}")
    
    for i, chunk in enumerate(selected_chunks[:5]):  # Show top 5
        print(f"  {i+1}. {chunk['document']} (chunk {chunk['chunk_id']}, similarity: {chunk['similarity']:.3f})")
        print(f"     Preview: {chunk['text'][:100]}...")
    
    return selected_chunks


def find_relevant_chunks(query: str, model: SentenceTransformer, 
                        relevant_docs: List[str], chunk_embeddings: Dict,
                        strategy: str = "top_p", **kwargs) -> List[Dict]:
    """Unified interface for chunk retrieval with different strategies."""
    
    similarity_metric = kwargs.get("similarity_metric", "cosine")
    
    if strategy == "top_k":
        top_chunks_per_doc = kwargs.get("top_chunks_per_doc", 3)
        return find_relevant_chunks_top_k(query, model, relevant_docs, chunk_embeddings, 
                                        top_chunks_per_doc, similarity_metric)
    
    elif strategy == "top_p":
        top_p = kwargs.get("top_p", 0.6)
        min_similarity = kwargs.get("min_similarity", 0.3)
        return find_relevant_chunks_top_p(query, model, relevant_docs, chunk_embeddings, 
                                        top_p, min_similarity, similarity_metric)
    
    else:
        raise ValueError(f"Unknown strategy: {strategy}. Use 'top_k' or 'top_p'")


def get_documents_for_rag(relevant_docs: List[str], document_index: Dict) -> List[str]:
    """Get full content of relevant documents for RAG processing."""
    rag_documents = []
    
    for doc_name in relevant_docs:
        if doc_name in document_index:
            content = document_index[doc_name].get('full_content', document_index[doc_name].get('content', ''))
            if content.strip():
                rag_documents.append(content)
    
    print(f"📄 Retrieved {len(rag_documents)} documents for RAG")
    return rag_documents


def get_chunks_for_rag(relevant_chunks: List[Dict], max_chunks: int = 10) -> List[str]:
    """Get the most relevant chunks for RAG processing."""
    # Take top chunks and format them with context
    selected_chunks = relevant_chunks[:max_chunks]
    
    rag_chunks = []
    for chunk in selected_chunks:
        formatted_chunk = f"[Document: {chunk['document']}, Chunk {chunk['chunk_id']}]\n{chunk['text']}"
        rag_chunks.append(formatted_chunk)
    
    print(f"📄 Retrieved {len(rag_chunks)} chunks for RAG")
    return rag_chunks