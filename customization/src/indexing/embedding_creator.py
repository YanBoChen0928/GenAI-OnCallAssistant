"""Embedding generation for tags and document chunks."""

from typing import Dict
import numpy as np
from sentence_transformers import SentenceTransformer


def create_text_embedding(model: SentenceTransformer, text: str) -> np.ndarray:
    """Create embedding for a single text.
    
    Args:
        model: SentenceTransformer model.
        text: Input text.
        
    Returns:
        Numpy array containing the embedding.
    """
    if not text.strip():
        return np.zeros(model.get_sentence_embedding_dimension())
    return model.encode([text])[0]


def create_tag_embeddings(model: SentenceTransformer, document_index: Dict) -> Dict:
    """Create enhanced embeddings for all unique tags with medical context.
    
    Args:
        model: SentenceTransformer model.
        document_index: Document index dictionary.
        
    Returns:
        Dictionary mapping tags to their embeddings.
    """
    all_tags = set()
    
    # Collect all unique tags
    for doc_info in document_index.values():
        all_tags.update(doc_info['all_tags'])
    
    print(f"🔄 Creating enhanced embeddings for {len(all_tags)} unique tags")
    
    tag_embeddings = {}
    for tag in all_tags:
        if tag.strip():
            # Original tag embedding
            base_embedding = create_text_embedding(model, tag)
            
            # Medical context variations
            contexts = [
                f"patient presents with {tag}",
                f"clinical manifestation of {tag}",
                f"emergency department patient has {tag}",
                f"medical condition: {tag}"
            ]
            
            # Generate context embeddings
            context_embeddings = []
            for ctx in contexts:
                ctx_emb = create_text_embedding(model, ctx)
                context_embeddings.append(ctx_emb)
            
            # Combine original + context embeddings (weighted average)
            all_embeddings = [base_embedding] + context_embeddings
            enhanced_embedding = np.mean(all_embeddings, axis=0)
            
            tag_embeddings[tag] = enhanced_embedding
    
    print(f"✅ Created {len(tag_embeddings)} enhanced tag embeddings with medical context")
    return tag_embeddings


def create_chunk_embeddings(model: SentenceTransformer, document_index: Dict) -> Dict:
    """Create embeddings for all document chunks.
    
    Args:
        model: SentenceTransformer model.
        document_index: Document index dictionary.
        
    Returns:
        Dictionary mapping document names to their chunk embeddings.
    """
    chunk_embeddings = {}
    total_chunks = 0
    
    print("🔄 Creating chunk embeddings...")
    
    for pdf_name, doc_info in document_index.items():
        chunks = doc_info['chunks']
        doc_chunk_embeddings = []
        
        for chunk in chunks:
            chunk_text = chunk['text']
            if chunk_text.strip():
                embedding = create_text_embedding(model, chunk_text)
                doc_chunk_embeddings.append({
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk_text,
                    'start_char': chunk.get('start_char', 0),
                    'end_char': chunk.get('end_char', len(chunk_text)),
                    'token_count': chunk.get('token_count', len(chunk_text.split())),
                    'embedding': embedding
                })
        
        chunk_embeddings[pdf_name] = doc_chunk_embeddings
        total_chunks += len(doc_chunk_embeddings)
        print(f"  📄 {pdf_name}: {len(doc_chunk_embeddings)} chunks")
    
    print(f"✅ Created embeddings for {total_chunks} chunks across all documents")
    return chunk_embeddings