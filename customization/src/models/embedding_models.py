"""Embedding model loading and management."""

from typing import Optional
import torch
from sentence_transformers import SentenceTransformer, models


def load_biomedbert_model(device: Optional[str] = None) -> SentenceTransformer:
    """Load BGE Large Medical model optimized for medical domain embeddings.
    
    Args:
        device: Device to use ('cuda', 'mps', 'cpu'). Auto-detects if None.
        
    Returns:
        Loaded SentenceTransformer model.
    """
    if device is None:
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():  # Apple Silicon GPU
            device = "mps"
        else:
            device = "cpu"

    print(f"Using device: {device}")
    
    # Use BGE Large Medical which is optimized for medical domain
    try:
        model = SentenceTransformer('ls-da3m0ns/bge_large_medical')
        model = model.to(device)
        print("✅ Loaded BGE Large Medical model for medical embeddings")
        return model
    except Exception as e:
        print(f"❌ Failed to load BGE Large Medical: {e}")
        print("🔄 Falling back to manual construction...")
        
        # Fallback to manual construction if direct loading fails
        word_embedding_model = models.Transformer('ls-da3m0ns/bge_large_medical')
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
        model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
        model = model.to(device)
        return model


def load_meditron_model():
    """Load Meditron-7B model (placeholder for future implementation).
    
    Returns:
        None (not implemented yet).
    """
    # TODO: Implement Meditron-7B loading
    # from transformers import AutoTokenizer, AutoModelForCausalLM
    # tokenizer = AutoTokenizer.from_pretrained("epfl-llm/meditron-7b")
    # model = AutoModelForCausalLM.from_pretrained("epfl-llm/meditron-7b")
    print("Meditron-7B to be implemented")
    return None