"""Medical RAG Pipeline module (Functional Programming)."""

from .medical_rag_pipeline import (
    generate_with_ollama,
    retrieve_medical_context,
    evaluate_context_quality,
    create_medical_prompt,
    generate_medical_response,
    answer_medical_query,
    load_rag_data,
    quick_medical_query
)

__all__ = [
    'generate_with_ollama',
    'retrieve_medical_context', 
    'evaluate_context_quality',
    'create_medical_prompt',
    'generate_medical_response',
    'answer_medical_query',
    'load_rag_data',
    'quick_medical_query'
]