"""Data persistence for document system."""

import json
import os
import logging
from typing import Dict, Optional, Tuple
import numpy as np
from .annoy_manager import AnnoyIndexManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_document_system(document_index: Dict, tag_embeddings: Dict, 
                        doc_tag_mapping: Dict, chunk_embeddings: Dict = None, 
                        output_dir: str = None, build_annoy_indices: bool = True):
    """Save the complete document indexing system.
    
    Args:
        document_index: Document index dictionary.
        tag_embeddings: Tag embeddings dictionary.
        doc_tag_mapping: Document-tag mapping dictionary.
        chunk_embeddings: Chunk embeddings dictionary (optional).
        output_dir: Output directory for saved files.
    """
    
    if output_dir is None:
        # Get project root directory
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent.parent
        output_dir = root_dir / 'embeddings' / 'pdfembeddings'
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save document index (content + metadata + chunks)
    doc_index_serializable = {}
    for doc_name, doc_info in document_index.items():
        doc_index_serializable[doc_name] = {
            'full_content': doc_info.get('full_content', doc_info.get('content', '')),
            'chunks': doc_info.get('chunks', []),
            'symptoms': doc_info['symptoms'],
            'diagnoses': doc_info['diagnoses'],
            'treatments': doc_info.get('treatments', []),
            'all_tags': doc_info['all_tags']
        }
    
    with open(os.path.join(output_dir, 'document_index.json'), 'w', encoding='utf-8') as f:
        json.dump(doc_index_serializable, f, indent=2, ensure_ascii=False)
    
    # Save tag embeddings
    tag_embeddings_serializable = {
        tag: embedding.tolist() for tag, embedding in tag_embeddings.items()
    }
    with open(os.path.join(output_dir, 'tag_embeddings.json'), 'w', encoding='utf-8') as f:
        json.dump(tag_embeddings_serializable, f, indent=2, ensure_ascii=False)
    
    # Save document-tag mapping
    doc_tag_serializable = {}
    for doc_name, doc_info in doc_tag_mapping.items():
        doc_tag_serializable[doc_name] = {
            'tags': doc_info['tags'],
            'symptoms': doc_info['symptoms'],
            'diagnoses': doc_info['diagnoses'],
            'treatments': doc_info['treatments'],
            'tag_embeddings': {
                tag: embedding.tolist() 
                for tag, embedding in doc_info['tag_embeddings'].items()
            }
        }
    
    with open(os.path.join(output_dir, 'document_tag_mapping.json'), 'w', encoding='utf-8') as f:
        json.dump(doc_tag_serializable, f, indent=2, ensure_ascii=False)
    
    # Save chunk embeddings if provided
    if chunk_embeddings:
        chunk_embeddings_serializable = {}
        for doc_name, chunks in chunk_embeddings.items():
            chunk_embeddings_serializable[doc_name] = []
            for chunk in chunks:
                chunk_embeddings_serializable[doc_name].append({
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk['text'],
                    'start_char': chunk.get('start_char', 0),
                    'end_char': chunk.get('end_char', len(chunk['text'])),
                    'token_count': chunk.get('token_count', len(chunk['text'].split())),
                    'embedding': chunk['embedding'].tolist()
                })
        
        with open(os.path.join(output_dir, 'chunk_embeddings.json'), 'w', encoding='utf-8') as f:
            json.dump(chunk_embeddings_serializable, f, indent=2, ensure_ascii=False)
    
    # Build and save ANNOY indices if requested
    if build_annoy_indices:
        logger.info("🔧 Building ANNOY indices for fast retrieval...")
        try:
            # Initialize ANNOY manager (assuming BGE Large Medical embedding dimension)
            annoy_manager = AnnoyIndexManager(embedding_dim=1024, metric='angular')
            
            # Build tag index
            logger.info("Building tag ANNOY index...")
            annoy_manager.build_tag_index(tag_embeddings, n_trees=50)
            
            # Build chunk index if chunk embeddings are provided
            if chunk_embeddings:
                logger.info("Building chunk ANNOY index...")
                annoy_manager.build_chunk_index(chunk_embeddings, n_trees=50)
            
            # Save indices
            logger.info("Saving ANNOY indices...")
            annoy_manager.save_indices(output_dir)
            
            logger.info("✅ ANNOY indices built and saved successfully")
        except Exception as e:
            logger.error(f"❌ Failed to build ANNOY indices: {e}")
            logger.warning("Continuing without ANNOY indices - will use original search methods")
    
    print("✅ Document system saved to files")


def load_document_system(input_dir: str = None) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict], Optional[Dict]]:
    """Load the complete document indexing system.
    
    Args:
        input_dir: Input directory containing saved files.
        
    Returns:
        Tuple of (document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings).
        Returns (None, None, None, None) if loading fails.
    """
    if input_dir is None:
        # Get project root directory
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent.parent
        input_dir = root_dir / 'embeddings' / 'pdfembeddings'
    
    try:
        # Load document index
        with open(os.path.join(input_dir, 'document_index.json'), 'r', encoding='utf-8') as f:
            document_index = json.load(f)
        
        # Load tag embeddings
        with open(os.path.join(input_dir, 'tag_embeddings.json'), 'r', encoding='utf-8') as f:
            tag_embeddings_data = json.load(f)
            tag_embeddings = {
                tag: np.array(embedding) 
                for tag, embedding in tag_embeddings_data.items()
            }
        
        # Load document-tag mapping
        with open(os.path.join(input_dir, 'document_tag_mapping.json'), 'r', encoding='utf-8') as f:
            doc_tag_data = json.load(f)
            doc_tag_mapping = {}
            for doc_name, doc_info in doc_tag_data.items():
                doc_tag_mapping[doc_name] = {
                    'tags': doc_info['tags'],
                    'symptoms': doc_info['symptoms'],
                    'diagnoses': doc_info['diagnoses'],
                    'treatments': doc_info['treatments'],
                    'tag_embeddings': {
                        tag: np.array(embedding)
                        for tag, embedding in doc_info['tag_embeddings'].items()
                    }
                }
        
        # Try to load chunk embeddings if they exist
        chunk_embeddings = None
        chunk_embeddings_path = os.path.join(input_dir, 'chunk_embeddings.json')
        if os.path.exists(chunk_embeddings_path):
            with open(chunk_embeddings_path, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
                chunk_embeddings = {}
                for doc_name, chunks in chunk_data.items():
                    chunk_embeddings[doc_name] = []
                    for chunk in chunks:
                        chunk_embeddings[doc_name].append({
                            'chunk_id': chunk['chunk_id'],
                            'text': chunk['text'],
                            'start_char': chunk.get('start_char', 0),
                            'end_char': chunk.get('end_char', len(chunk['text'])),
                            'token_count': chunk.get('token_count', len(chunk['text'].split())),
                            # Backward compatibility for old format
                            'start_word': chunk.get('start_word', 0),
                            'end_word': chunk.get('end_word', len(chunk['text'].split())),
                            'embedding': np.array(chunk['embedding'])
                        })
            print("✅ Chunk embeddings loaded")
        
        print("✅ Document system loaded successfully")
        return document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings
        
    except Exception as e:
        print(f"❌ Failed to load document system: {e}")
        return None, None, None, None


def load_annoy_manager(input_dir: str = None) -> Optional[AnnoyIndexManager]:
    """
    Load ANNOY index manager with pre-built indices.
    
    Args:
        input_dir: Input directory containing saved indices
        
    Returns:
        AnnoyIndexManager instance or None if loading fails
    """
    if input_dir is None:
        # Get project root directory
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent.parent
        input_dir = root_dir / 'embeddings' / 'pdfembeddings'
    
    try:
        # Initialize ANNOY manager
        annoy_manager = AnnoyIndexManager(embedding_dim=1024, metric='angular')
        
        # Try to load indices
        if annoy_manager.load_indices(input_dir):
            logger.info("✅ ANNOY indices loaded successfully")
            return annoy_manager
        else:
            logger.warning("⚠️ Failed to load ANNOY indices")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize ANNOY manager: {e}")
        return None


def load_document_system_with_annoy(input_dir: str = None, annoy_dir: str = None) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict], Optional[Dict], Optional[AnnoyIndexManager]]:
    """
    Load the complete document indexing system including ANNOY indices.
    
    Args:
        input_dir: Input directory containing saved files
        annoy_dir: Directory containing ANNOY indices (if different from input_dir)
        
    Returns:
        Tuple of (document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings, annoy_manager).
        Returns all None values if loading fails.
    """
    # Load the standard document system
    document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings = load_document_system(input_dir)
    
    if document_index is None:
        return None, None, None, None, None
    
    # Load ANNOY manager
    # Use annoy_dir if provided, otherwise use input_dir
    annoy_manager = load_annoy_manager(annoy_dir if annoy_dir else input_dir)
    
    return document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings, annoy_manager