"""Complete Medical RAG Pipeline integrating retrieval system with Meditron-7B (Functional Programming)."""

import json
import requests
import numpy as np
from typing import Dict, List, Optional, Tuple
from sentence_transformers import SentenceTransformer

# Import existing retrieval components
from custom_retrieval.document_retriever import find_relevant_documents
from custom_retrieval.chunk_retriever import find_relevant_chunks, get_chunks_for_rag
from models.embedding_models import load_biomedbert_model


def generate_with_ollama(prompt: str, 
                        model: str = "meditron:7b",
                        base_url: str = "http://localhost:11434",
                        temperature: float = 0.1, 
                        max_tokens: int = 300) -> Dict:
    """Generate response using Ollama model.
    
    Args:
        prompt: Input prompt for the model
        model: Ollama model name
        base_url: Ollama server URL
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Dictionary with response or error
    """
    url = f"{base_url}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "top_p": 0.9,
            "top_k": 40
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"LLM request failed: {str(e)}"}


def retrieve_medical_context(query: str,
                           embedding_model: SentenceTransformer,
                           tag_embeddings: Dict,
                           chunk_embeddings: Dict,
                           doc_tag_mapping: Dict,
                           doc_strategy: str = "top_p",
                           chunk_strategy: str = "top_p",
                           max_chunks: int = 5) -> Dict:
    """
    Retrieve relevant medical context for query using two-stage retrieval.
    
    Args:
        query: Medical question/query
        embedding_model: BGE Large Medical model
        tag_embeddings: Pre-computed tag embeddings
        chunk_embeddings: Pre-computed chunk embeddings
        doc_tag_mapping: Document to tag mapping
        doc_strategy: Document retrieval strategy
        chunk_strategy: Chunk retrieval strategy
        max_chunks: Maximum chunks to retrieve
        
    Returns:
        Dictionary with retrieval results and metadata
    """
    print(f"🔍 Retrieving context for: '{query}'")
    
    # Stage 1: Document-level retrieval
    print("📄 Stage 1: Document retrieval...")
    relevant_docs = find_relevant_documents(
        query, embedding_model, tag_embeddings, doc_tag_mapping,
        strategy=doc_strategy, top_p=0.6, min_similarity=0.5
    )
    
    if not relevant_docs:
        print("⚠️ No relevant documents found")
        return {
            "has_context": False,
            "relevant_documents": [],
            "relevant_chunks": [],
            "rag_chunks": [],
            "context_text": "",
            "retrieval_metadata": {
                "total_docs": 0,
                "total_chunks": 0,
                "context_length": 0
            }
        }
    
    # Stage 2: Chunk-level retrieval
    print("📝 Stage 2: Chunk retrieval...")
    relevant_chunks = find_relevant_chunks(
        query, embedding_model, relevant_docs, chunk_embeddings,
        strategy=chunk_strategy, top_p=0.6, min_similarity=0.3, 
        similarity_metric="dot_product"
    )
    
    if not relevant_chunks:
        print("⚠️ No relevant chunks found")
        return {
            "has_context": False,
            "relevant_documents": relevant_docs,
            "relevant_chunks": [],
            "rag_chunks": [],
            "context_text": "",
            "retrieval_metadata": {
                "total_docs": len(relevant_docs),
                "total_chunks": 0,
                "context_length": 0
            }
        }
    
    # Stage 3: Prepare RAG context
    print("🎯 Stage 3: Preparing RAG context...")
    rag_chunks = get_chunks_for_rag(relevant_chunks, max_chunks)
    context_text = "\n\n".join(rag_chunks)
    
    # Calculate retrieval statistics
    avg_similarity = np.mean([chunk['similarity'] for chunk in relevant_chunks])
    max_similarity = max([chunk['similarity'] for chunk in relevant_chunks])
    
    print(f"✅ Context prepared: {len(rag_chunks)} chunks, avg_sim={avg_similarity:.3f}")
    
    return {
        "has_context": True,
        "relevant_documents": relevant_docs,
        "relevant_chunks": relevant_chunks,
        "rag_chunks": rag_chunks,
        "context_text": context_text,
        "retrieval_metadata": {
            "total_docs": len(relevant_docs),
            "total_chunks": len(relevant_chunks),
            "chunks_for_rag": len(rag_chunks),
            "context_length": len(context_text),
            "avg_similarity": float(avg_similarity),
            "max_similarity": float(max_similarity)
        }
    }


def evaluate_context_quality(context_result: Dict, query: str) -> Dict:
    """
    Evaluate if retrieved context is sufficient to answer the query.
    
    Args:
        context_result: Result from retrieve_medical_context()
        query: Original query
        
    Returns:
        Quality assessment dictionary
    """
    if not context_result["has_context"]:
        return {
            "is_sufficient": False,
            "confidence": 0.0,
            "reason": "No relevant medical documents found in database"
        }
    
    metadata = context_result["retrieval_metadata"]
    
    # Quality heuristics
    min_similarity_threshold = 0.4
    min_chunks_threshold = 2
    min_context_length = 200
    
    # Check similarity scores
    avg_sim = metadata["avg_similarity"]
    max_sim = metadata["max_similarity"]
    
    # Check quantity
    chunk_count = metadata["chunks_for_rag"]
    context_length = metadata["context_length"]
    
    # Determine if context is sufficient
    quality_checks = {
        "high_similarity": max_sim >= min_similarity_threshold,
        "sufficient_chunks": chunk_count >= min_chunks_threshold,
        "sufficient_length": context_length >= min_context_length,
        "decent_avg_similarity": avg_sim >= 0.3
    }
    
    passed_checks = sum(quality_checks.values())
    confidence = passed_checks / len(quality_checks)
    
    is_sufficient = passed_checks >= 3  # At least 3/4 checks must pass
    
    if not is_sufficient:
        if not quality_checks["high_similarity"]:
            reason = f"Low similarity to medical documents (max: {max_sim:.3f})"
        elif not quality_checks["sufficient_chunks"]:
            reason = f"Insufficient relevant content found ({chunk_count} chunks)"
        else:
            reason = "Retrieved content may not adequately address the query"
    else:
        reason = "Context appears sufficient for medical response"
    
    return {
        "is_sufficient": is_sufficient,
        "confidence": confidence,
        "reason": reason,
        "quality_checks": quality_checks,
        "similarity_stats": {
            "avg_similarity": avg_sim,
            "max_similarity": max_sim
        }
    }


def create_medical_prompt(query: str, context: str, context_quality: Dict) -> str:
    """
    Create a medical prompt with proper instructions and context.
    
    Args:
        query: User's medical question
        context: Retrieved medical context
        context_quality: Context quality assessment
        
    Returns:
        Formatted prompt for medical LLM
    """
    # Base medical prompt with professional identity
    base_prompt = """You are a medical AI assistant. Your role is to provide accurate medical information based strictly on the provided medical literature context.

IMPORTANT GUIDELINES:
1. Base your answers ONLY on the provided medical context
2. If the context doesn't contain sufficient information to answer the question, clearly state: "Based on the available medical literature in my database, I cannot provide a complete answer to this question."
3. Always cite that your response is "based on the provided medical literature"
4. Do not make assumptions or provide information not present in the context
5. For serious medical conditions, always recommend consulting healthcare professionals
6. Be precise and use appropriate medical terminology

"""
    
    if context_quality["is_sufficient"]:
        # High-confidence response with context
        prompt = f"""{base_prompt}

MEDICAL LITERATURE CONTEXT:
{context}

QUESTION: {query}

MEDICAL RESPONSE (based on the provided medical literature):"""
    
    else:
        # Low-confidence response with limited context
        prompt = f"""{base_prompt}

LIMITED MEDICAL CONTEXT AVAILABLE:
{context if context else "No directly relevant medical literature found."}

QUESTION: {query}

MEDICAL RESPONSE: Based on the available medical literature in my database, I have limited information to fully address this question. {context_quality["reason"]}

However, here is what I can provide based on the available context:"""
    
    return prompt


def generate_medical_response(prompt: str, model: str = "meditron:7b") -> Dict:
    """
    Generate medical response using Meditron-7B.
    
    Args:
        prompt: Formatted medical prompt
        model: Ollama model name
        
    Returns:
        LLM response dictionary
    """
    print("🧠 Generating medical response...")
    
    # Use low temperature for medical accuracy
    result = generate_with_ollama(
        prompt, 
        model=model,
        temperature=0.1,  # Very low for medical precision
        max_tokens=400
    )
    
    if "error" in result:
        return {
            "success": False,
            "response": "I apologize, but I'm currently unable to process medical queries due to a technical issue. Please consult a healthcare professional for medical advice.",
            "error": result["error"]
        }
    
    response_text = result.get("response", "").strip()
    
    # Basic response validation
    if len(response_text) < 20:
        return {
            "success": False,
            "response": "I was unable to generate a meaningful response. Please rephrase your medical question or consult a healthcare professional.",
            "error": "Generated response too short"
        }
    
    return {
        "success": True,
        "response": response_text,
        "generation_metadata": {
            "model": model,
            "response_length": len(response_text)
        }
    }


def answer_medical_query(query: str,
                        embedding_model: SentenceTransformer,
                        tag_embeddings: Dict,
                        chunk_embeddings: Dict,
                        doc_tag_mapping: Dict,
                        document_index: Dict,
                        model: str = "meditron:7b",
                        **kwargs) -> Dict:
    """
    Complete medical RAG pipeline: retrieve context and generate answer.
    
    Args:
        query: Medical question
        embedding_model: BGE Large Medical model
        tag_embeddings: Pre-computed tag embeddings
        chunk_embeddings: Pre-computed chunk embeddings
        doc_tag_mapping: Document to tag mapping
        document_index: Complete document index
        model: Ollama model name
        **kwargs: Additional parameters for retrieval and generation
        
    Returns:
        Complete response dictionary with metadata
    """
    print("\n" + "="*60)
    print(f"🏥 Medical RAG Query: '{query}'")
    print("="*60)
    
    # Step 1: Retrieve medical context
    context_result = retrieve_medical_context(
        query, embedding_model, tag_embeddings, chunk_embeddings, 
        doc_tag_mapping, **kwargs
    )
    
    # Step 2: Evaluate context quality
    context_quality = evaluate_context_quality(context_result, query)
    
    print(f"📊 Context Quality: {context_quality['confidence']:.1%} confidence")
    print(f"💭 Assessment: {context_quality['reason']}")
    
    # Step 3: Create medical prompt
    medical_prompt = create_medical_prompt(
        query, context_result["context_text"], context_quality
    )
    
    # Step 4: Generate medical response
    response_result = generate_medical_response(medical_prompt, model)
    
    # Step 5: Compile complete result
    complete_result = {
        "query": query,
        "answer": response_result["response"],
        "success": response_result["success"],
        "context_quality": context_quality,
        "retrieval_metadata": context_result["retrieval_metadata"],
        "sources": {
            "documents": context_result["relevant_documents"],
            "chunk_count": len(context_result["rag_chunks"])
        }
    }
    
    # Add error information if present
    if "error" in response_result:
        complete_result["error"] = response_result["error"]
    
    print(f"\n✅ Response generated successfully: {len(response_result['response'])} characters")
    return complete_result


def load_rag_data(tag_embeddings_path: str = None,
                  chunk_embeddings_path: str = None, 
                  doc_tag_mapping_path: str = None,
                  document_index_path: str = None) -> Tuple[SentenceTransformer, Dict, Dict, Dict, Dict]:
    """
    Load all RAG data needed for medical question answering.
    
    Args:
        tag_embeddings_path: Path to tag embeddings
        chunk_embeddings_path: Path to chunk embeddings
        doc_tag_mapping_path: Path to document tag mapping
        document_index_path: Path to document index
        
    Returns:
        Tuple of (embedding_model, tag_embeddings, chunk_embeddings, doc_tag_mapping, document_index)
    """
    print("🔄 Loading Medical RAG Data...")
    
    # Set default paths if not provided
    if tag_embeddings_path is None:
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent.parent
        embeddings_dir = root_dir / 'embeddings' / 'pdfembeddings'
        tag_embeddings_path = embeddings_dir / 'tag_embeddings.json'
    if chunk_embeddings_path is None:
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent.parent
        embeddings_dir = root_dir / 'embeddings' / 'pdfembeddings'
        chunk_embeddings_path = embeddings_dir / 'chunk_embeddings.json'
    if doc_tag_mapping_path is None:
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent.parent
        embeddings_dir = root_dir / 'embeddings' / 'pdfembeddings'
        doc_tag_mapping_path = embeddings_dir / 'document_tag_mapping.json'
    if document_index_path is None:
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent.parent
        embeddings_dir = root_dir / 'embeddings' / 'pdfembeddings'
        document_index_path = embeddings_dir / 'document_index.json'
    
    # Load embedding model
    print("📦 Loading BGE Large Medical embedding model...")
    embedding_model = load_biomedbert_model()
    
    # Load embeddings and indices
    print("📂 Loading embeddings and indices...")
    
    with open(tag_embeddings_path, 'r') as f:
        tag_embeddings = json.load(f)
        tag_embeddings = {tag: np.array(embedding) for tag, embedding in tag_embeddings.items()}
    
    with open(chunk_embeddings_path, 'r') as f:
        chunk_embeddings = json.load(f)
        for doc_name, chunks in chunk_embeddings.items():
            for chunk in chunks:
                chunk['embedding'] = np.array(chunk['embedding'])
    
    with open(doc_tag_mapping_path, 'r') as f:
        doc_tag_mapping = json.load(f)
    
    with open(document_index_path, 'r') as f:
        document_index = json.load(f)
    
    print("✅ Medical RAG data loaded successfully!")
    return embedding_model, tag_embeddings, chunk_embeddings, doc_tag_mapping, document_index


def quick_medical_query(query: str, max_chunks: int = 3) -> Dict:
    """
    Quick medical query with default settings.
    
    Args:
        query: Medical question
        max_chunks: Maximum chunks to retrieve
        
    Returns:
        Medical response dictionary
    """
    # Load data
    embedding_model, tag_embeddings, chunk_embeddings, doc_tag_mapping, document_index = load_rag_data()
    
    # Answer query
    return answer_medical_query(
        query, embedding_model, tag_embeddings, chunk_embeddings,
        doc_tag_mapping, document_index, max_chunks=max_chunks
    )