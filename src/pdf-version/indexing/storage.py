"""Data persistence for document system."""

import json
import os
from typing import Dict, Optional, Tuple
import numpy as np


def save_document_system(document_index: Dict, tag_embeddings: Dict, 
                        doc_tag_mapping: Dict, chunk_embeddings: Dict = None, 
                        output_dir: str = "."):
    """Save the complete document indexing system.
    
    Args:
        document_index: Document index dictionary.
        tag_embeddings: Tag embeddings dictionary.
        doc_tag_mapping: Document-tag mapping dictionary.
        chunk_embeddings: Chunk embeddings dictionary (optional).
        output_dir: Output directory for saved files.
    """
    
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
    
    print("✅ Document system saved to files")


def load_document_system(input_dir: str = ".") -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict], Optional[Dict]]:
    """Load the complete document indexing system.
    
    Args:
        input_dir: Input directory containing saved files.
        
    Returns:
        Tuple of (document_index, tag_embeddings, doc_tag_mapping, chunk_embeddings).
        Returns (None, None, None, None) if loading fails.
    """
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