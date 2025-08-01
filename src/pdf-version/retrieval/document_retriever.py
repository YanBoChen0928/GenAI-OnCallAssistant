"""Document retrieval strategies and functionality."""

from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from src.indexing.embedding_creator import create_text_embedding


def find_relevant_documents_top_k(query: str, model: SentenceTransformer, 
                                tag_embeddings: Dict, doc_tag_mapping: Dict, 
                                top_k: int = 3) -> List[str]:
    """Find top-k most relevant documents based on query similarity to tags."""
    query_embedding = create_text_embedding(model, query)
    
    # Calculate similarity between query and all tags
    tag_similarities = {}
    for tag, tag_embedding in tag_embeddings.items():
        similarity = np.dot(query_embedding, tag_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(tag_embedding)
        )
        tag_similarities[tag] = similarity
    
    # Find documents that contain the most similar tags
    doc_scores = {}
    for pdf_name, doc_info in doc_tag_mapping.items():
        doc_tags = doc_info['tags']
        
        # Calculate document score using max similarity for precise tag matching
        if doc_tags:
            similarities = [tag_similarities.get(tag, 0) for tag in doc_tags]
            # Use max similarity to find documents with best tag matches
            doc_score = max(similarities)
            doc_scores[pdf_name] = doc_score
    
    # Sort and return top-k documents
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    relevant_docs = [doc_name for doc_name, score in sorted_docs[:top_k]]
    
    print(f"🔍 Found {len(relevant_docs)} relevant documents for query: '{query}' (TOP-K)")
    for i, doc_name in enumerate(relevant_docs):
        score = doc_scores[doc_name]
        print(f"  {i+1}. {doc_name} (similarity: {score:.3f})")
    
    return relevant_docs


def find_relevant_documents_top_p(query: str, model: SentenceTransformer, 
                                tag_embeddings: Dict, doc_tag_mapping: Dict, 
                                top_p: float = 0.6, min_similarity: float = 0.5) -> List[str]:
    """Find documents using TOP-P (nucleus sampling) approach."""
    query_embedding = create_text_embedding(model, query)
    
    # Calculate similarity between query and all tags
    tag_similarities = {}
    for tag, tag_embedding in tag_embeddings.items():
        similarity = np.dot(query_embedding, tag_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(tag_embedding)
        )
        tag_similarities[tag] = similarity
    
    # Find documents that contain the most similar tags
    doc_scores = {}
    for pdf_name, doc_info in doc_tag_mapping.items():
        doc_tags = doc_info['tags']
        
        # Calculate document score using max similarity for precise tag matching
        if doc_tags:
            similarities = [tag_similarities.get(tag, 0) for tag in doc_tags]
            # Use max similarity to find documents with best tag matches
            doc_score = max(similarities)
            doc_scores[pdf_name] = doc_score
    
    # Filter out documents below minimum similarity threshold
    filtered_docs = {doc: score for doc, score in doc_scores.items() 
                    if score >= min_similarity}
    
    if not filtered_docs:
        print(f"⚠️ No documents found above similarity threshold {min_similarity}")
        return []
    
    # Sort documents by similarity score
    sorted_docs = sorted(filtered_docs.items(), key=lambda x: x[1], reverse=True)
    
    # Apply TOP-P selection
    total_score = sum(score for _, score in sorted_docs)
    cumulative_prob = 0.0
    selected_docs = []
    
    for doc_name, score in sorted_docs:
        prob = score / total_score
        cumulative_prob += prob
        selected_docs.append(doc_name)
        
        # Stop when we reach the TOP-P threshold
        if cumulative_prob >= top_p:
            break
    
    print(f"🔍 Found {len(selected_docs)} relevant documents for query: '{query}' (TOP-P={top_p})")
    print(f"📊 Cumulative probability: {cumulative_prob:.3f}")
    
    for i, doc_name in enumerate(selected_docs):
        score = doc_scores[doc_name]
        prob = score / total_score
        print(f"  {i+1}. {doc_name} (similarity: {score:.3f}, prob: {prob:.3f})")
    
    return selected_docs


def find_relevant_documents_threshold(query: str, model: SentenceTransformer, 
                                    tag_embeddings: Dict, doc_tag_mapping: Dict, 
                                    similarity_threshold: float = 0.5) -> List[str]:
    """Find all documents above a similarity threshold."""
    query_embedding = create_text_embedding(model, query)
    
    # Calculate similarity between query and all tags
    tag_similarities = {}
    for tag, tag_embedding in tag_embeddings.items():
        similarity = np.dot(query_embedding, tag_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(tag_embedding)
        )
        tag_similarities[tag] = similarity
    
    # Find documents that contain the most similar tags
    doc_scores = {}
    for pdf_name, doc_info in doc_tag_mapping.items():
        doc_tags = doc_info['tags']
        
        # Calculate document score using weighted average
        if doc_tags:
            similarities = [tag_similarities.get(tag, 0) for tag in doc_tags]
            avg_similarity = np.mean(similarities)
            max_similarity = max(similarities)
            # Weighted combination: 70% average (overall relevance) + 30% max (strongest match)
            doc_score = avg_similarity * 0.7 + max_similarity * 0.3
            if doc_score >= similarity_threshold:
                doc_scores[pdf_name] = doc_score
    
    # Sort by similarity score
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    relevant_docs = [doc_name for doc_name, score in sorted_docs]
    
    print(f"🔍 Found {len(relevant_docs)} relevant documents for query: '{query}' (threshold={similarity_threshold})")
    for i, doc_name in enumerate(relevant_docs):
        score = doc_scores[doc_name]
        print(f"  {i+1}. {doc_name} (similarity: {score:.3f})")
    
    return relevant_docs


def find_relevant_documents(query: str, model: SentenceTransformer, 
                          tag_embeddings: Dict, doc_tag_mapping: Dict, 
                          strategy: str = "top_k", **kwargs) -> List[str]:
    """Unified interface for finding relevant documents with different strategies."""
    if strategy == "top_k":
        top_k = kwargs.get("top_k", 3)
        return find_relevant_documents_top_k(query, model, tag_embeddings, doc_tag_mapping, top_k)
    
    elif strategy == "top_p":
        top_p = kwargs.get("top_p", 0.6)
        min_similarity = kwargs.get("min_similarity", 0.5)
        return find_relevant_documents_top_p(query, model, tag_embeddings, doc_tag_mapping, top_p, min_similarity)
    
    elif strategy == "threshold":
        similarity_threshold = kwargs.get("similarity_threshold", 0.5)
        return find_relevant_documents_threshold(query, model, tag_embeddings, doc_tag_mapping, similarity_threshold)
    
    else:
        raise ValueError(f"Unknown strategy: {strategy}. Use 'top_k', 'top_p', or 'threshold'")


def create_document_tag_mapping(document_index: Dict, tag_embeddings: Dict) -> Dict:
    """Create mapping between documents and their tag embeddings."""
    doc_tag_mapping = {}
    
    for pdf_name, doc_info in document_index.items():
        doc_tags = doc_info['all_tags']
        
        # Get embeddings for this document's tags
        doc_tag_embeddings = {}
        for tag in doc_tags:
            if tag in tag_embeddings:
                doc_tag_embeddings[tag] = tag_embeddings[tag]
        
        doc_tag_mapping[pdf_name] = {
            'tags': doc_tags,
            'tag_embeddings': doc_tag_embeddings,
            'symptoms': doc_info['symptoms'],
            'diagnoses': doc_info['diagnoses'],
            'treatments': doc_info.get('treatments', [])
        }
    
    return doc_tag_mapping