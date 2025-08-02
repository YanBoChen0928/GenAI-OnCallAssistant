"""Document indexing and chunking functionality."""

import os
from typing import List, Dict
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from data.pdf_processing import extract_pdf_content_enhanced


def split_text_into_chunks(text: str, chunk_size: int = 256, chunk_overlap: int = 25) -> List[Dict]:
    """Split text into sentence-based chunks with token control.
    
    Args:
        text: Input text to split.
        chunk_size: Maximum size of each chunk in tokens.
        chunk_overlap: Number of overlapping tokens between chunks.
        
    Returns:
        List of chunk dictionaries with metadata.
    """
    if not text.strip():
        return []
    
    # Use LlamaIndex SentenceSplitter for sentence-aware, token-based chunking
    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        paragraph_separator="\n\n",
        secondary_chunking_regex="[^.!?]+[.!?]"  # Split on sentences
    )
    
    # Create a Document object for the splitter
    document = Document(text=text)
    
    # Split the document into nodes
    nodes = splitter.get_nodes_from_documents([document])
    
    # Convert nodes to our chunk format
    chunks = []
    for i, node in enumerate(nodes):
        chunk_text = node.get_content()
        if chunk_text.strip():
            chunks.append({
                'text': chunk_text,
                'chunk_id': i,
                'token_count': len(chunk_text.split()),  # Approximate token count
                'node_id': node.node_id,
                'start_char': getattr(node, 'start_char_idx', 0),
                'end_char': getattr(node, 'end_char_idx', len(chunk_text))
            })
    
    return chunks


def build_document_index(annotations: List[Dict], assets_dir: str = "assets", 
                        chunk_size: int = 256, chunk_overlap: int = 25) -> Dict:
    """Build a comprehensive document index with sentence-based chunked content and tags.
    
    Args:
        annotations: List of annotation dictionaries.
        assets_dir: Directory containing PDF files.
        chunk_size: Maximum size of each chunk in tokens.
        chunk_overlap: Number of overlapping tokens between chunks.
        
    Returns:
        Dictionary containing document index with chunks and metadata.
    """
    document_index = {}
    
    for item in annotations:
        pdf_name = item['pdf']
        pdf_path = os.path.join(assets_dir, pdf_name)
        
        if not os.path.exists(pdf_path):
            print(f"⚠️ Skipping missing file: {pdf_name}")
            continue
            
        print(f"🔄 Indexing document: {pdf_name}")
        
        # Extract full document content
        documents = extract_pdf_content_enhanced(pdf_path)
        full_text = "\n\n".join([doc.text for doc in documents])
        
        # Split into chunks
        chunks = split_text_into_chunks(full_text, chunk_size, chunk_overlap)
        
        # Build comprehensive document record
        document_index[pdf_name] = {
            'full_content': full_text,
            'chunks': chunks,
            'symptoms': item.get('symptoms', []),
            'diagnoses': item.get('diagnoses', []),
            'treatments': item.get('treatments', []),
            'all_tags': item.get('symptoms', []) + item.get('diagnoses', []) + item.get('treatments', [])
        }
        
        print(f"  📄 Split into {len(chunks)} chunks")
    
    print(f"✅ Built index for {len(document_index)} documents")
    return document_index