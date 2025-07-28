"""
OnCall.ai Data Processing Module

This module handles:
1. Loading filtered medical guideline data
2. Creating intelligent chunks based on matched keywords
3. Generating embeddings using NeuML/pubmedbert-base-embeddings
4. Building ANNOY indices for vector search
5. Data quality validation

Author: OnCall.ai Team
Date: 2025-07-26
"""

# Required imports for core functionality
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Any
from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex
import logging
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # change between INFO and DEBUG level
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Explicitly define what should be exported
__all__ = ['DataProcessor']

class DataProcessor:
    """Main data processing class for OnCall.ai RAG system"""
    
    def __init__(self, base_dir: str = None):
        """
        Initialize DataProcessor
        
        Args:
            base_dir: Base directory path for the project
        """
        self.base_dir = Path(base_dir).resolve() if base_dir else Path(__file__).parent.parent.resolve()
        self.dataset_dir = (self.base_dir / "dataset" / "dataset").resolve()  # modify to actual dataset directory
        self.models_dir = (self.base_dir / "models").resolve()
        
        # Model configuration
        self.embedding_model_name = "NeuML/pubmedbert-base-embeddings"
        self.embedding_dim = 768  # PubMedBERT dimension
        self.chunk_size = 256    # Changed to tokens instead of characters
        self.chunk_overlap = 64  # Added overlap configuration
        
        # Initialize model and tokenizer (will be loaded when needed)
        self.embedding_model = None
        self.tokenizer = None
        
        # Data containers
        self.emergency_data = None
        self.treatment_data = None
        self.emergency_chunks = []
        self.treatment_chunks = []
        
        # Initialize indices
        self.emergency_index = None
        self.treatment_index = None
        
        logger.info(f"Initialized DataProcessor with:")
        logger.info(f"  Base directory: {self.base_dir}")
        logger.info(f"  Dataset directory: {self.dataset_dir}")
        logger.info(f"  Models directory: {self.models_dir}")
        logger.info(f"  Chunk size (tokens): {self.chunk_size}")
        logger.info(f"  Chunk overlap (tokens): {self.chunk_overlap}")
    
    def load_embedding_model(self):
        """Load the embedding model and initialize tokenizer"""
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.tokenizer = self.embedding_model.tokenizer
            logger.info("Embedding model and tokenizer loaded successfully")
        return self.embedding_model
    
    def load_filtered_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load pre-filtered emergency and treatment data
        
        Returns:
            Tuple of (emergency_data, treatment_data) DataFrames
        """
        logger.info("Loading filtered medical data...")
        
        # File paths
        emergency_path = (self.dataset_dir / "emergency" / "emergency_subset_opt.jsonl").resolve()
        treatment_path = (self.dataset_dir / "emergency_treatment" / "emergency_treatment_subset_opt.jsonl").resolve()
        
        logger.info(f"Looking for emergency data at: {emergency_path}")
        logger.info(f"Looking for treatment data at: {treatment_path}")
        
        # Validate file existence
        if not emergency_path.exists():
            raise FileNotFoundError(f"Emergency data not found: {emergency_path}")
        if not treatment_path.exists():
            raise FileNotFoundError(f"Treatment data not found: {treatment_path}")
        
        # Load data
        self.emergency_data = pd.read_json(str(emergency_path), lines=True)  # 使用 str() 确保路径正确处理
        self.treatment_data = pd.read_json(str(treatment_path), lines=True)
        
        logger.info(f"Loaded {len(self.emergency_data)} emergency records")
        logger.info(f"Loaded {len(self.treatment_data)} treatment records")
        
        return self.emergency_data, self.treatment_data
    
    def create_keyword_centered_chunks(self, text: str, matched_keywords: str, 
                                     chunk_size: int = None, doc_id: str = None) -> List[Dict[str, Any]]:
        """
        Create chunks centered around matched keywords using tokenizer
        
        Args:
            text: Input text
            matched_keywords: Pipe-separated keywords (e.g., "MI|chest pain|fever")
            chunk_size: Size of each chunk in tokens (defaults to self.chunk_size)
            doc_id: Document ID for tracking
            
        Returns:
            List of chunk dictionaries
        """
        if not matched_keywords or pd.isna(matched_keywords):
            return []
            
        # Load model if not loaded (to get tokenizer)
        if self.tokenizer is None:
            self.load_embedding_model()
            
        # Convert text and keywords to lowercase at the start
        text = text.lower()
        keywords = [kw.lower() for kw in matched_keywords.split("|")] if matched_keywords else []
        
        chunk_size = chunk_size or self.chunk_size
        chunks = []
        
        # Calculate character-to-token ratio using a sample around the first keyword
        if keywords:
            first_keyword = keywords[0]
            first_pos = text.find(first_keyword)
            if first_pos != -1:
                # Take a sample around the first keyword for ratio calculation
                sample_start = max(0, first_pos - 100)
                sample_end = min(len(text), first_pos + len(first_keyword) + 100)
                sample_text = text[sample_start:sample_end]
                sample_tokens = len(self.tokenizer.tokenize(sample_text))
                chars_per_token = len(sample_text) / sample_tokens if sample_tokens > 0 else 4.0
            else:
                chars_per_token = 4.0  # Fallback ratio
        else:
            chars_per_token = 4.0  # Default ratio
        
        # Process keywords
        for i, keyword in enumerate(keywords):
            # Find keyword position in text (already lowercase)
            keyword_pos = text.find(keyword)
            
            if keyword_pos != -1:
                # Get the keyword text (already lowercase)
                actual_keyword = text[keyword_pos:keyword_pos + len(keyword)]
                
                # Calculate rough window size using dynamic ratio
                # Cap the rough chunk target token size to prevent tokenizer warnings
                # Use 512 tokens as target (model's max limit)
                ROUGH_CHUNK_TARGET_TOKENS = 512
                char_window = int(ROUGH_CHUNK_TARGET_TOKENS * chars_per_token / 2)
                
                # Get rough chunk boundaries in characters
                rough_start = max(0, keyword_pos - char_window)
                rough_end = min(len(text), keyword_pos + len(keyword) + char_window)
                
                # Extract rough chunk for processing
                rough_chunk = text[rough_start:rough_end]
                
                # Find keyword's relative position in rough chunk
                rel_pos = rough_chunk.find(actual_keyword)
                if rel_pos == -1:
                    logger.debug(f"Could not locate keyword '{actual_keyword}' in rough chunk for doc {doc_id}")
                    continue
                
                # Calculate token position by tokenizing text before keyword
                text_before = rough_chunk[:rel_pos]
                tokens_before = self.tokenizer.tokenize(text_before)
                keyword_start_pos = len(tokens_before)
                
                # Tokenize necessary parts
                chunk_tokens = self.tokenizer.tokenize(rough_chunk)
                keyword_tokens = self.tokenizer.tokenize(actual_keyword)
                keyword_length = len(keyword_tokens)
                
                # Calculate final chunk boundaries in tokens
                tokens_each_side = (chunk_size - keyword_length) // 2
                chunk_start = max(0, keyword_start_pos - tokens_each_side)
                chunk_end = min(len(chunk_tokens), keyword_start_pos + keyword_length + tokens_each_side)
                
                # Add overlap if possible
                if chunk_start > 0:
                    chunk_start = max(0, chunk_start - self.chunk_overlap)
                if chunk_end < len(chunk_tokens):
                    chunk_end = min(len(chunk_tokens), chunk_end + self.chunk_overlap)
                
                # Extract final tokens and convert to text
                final_tokens = chunk_tokens[chunk_start:chunk_end]
                chunk_text = self.tokenizer.convert_tokens_to_string(final_tokens)
                
                # Verify keyword presence in final chunk
                if chunk_text and actual_keyword in chunk_text:
                    chunk_info = {
                        "text": chunk_text,
                        "primary_keyword": actual_keyword,
                        "all_matched_keywords": matched_keywords.lower(),
                        "token_count": len(final_tokens),
                        "chunk_id": f"{doc_id}_chunk_{i}" if doc_id else f"chunk_{i}",
                        "source_doc_id": doc_id
                    }
                    chunks.append(chunk_info)
                else:
                    logger.debug(f"Could not create chunk for keyword '{actual_keyword}' in doc {doc_id}")
        
        if chunks:
            logger.debug(f"Created {len(chunks)} chunks for document {doc_id or 'unknown'}")
        
        return chunks
    
    def create_dual_keyword_chunks(self, text: str, emergency_keywords: str, 
                                 treatment_keywords: str, chunk_size: int = 512, 
                                 doc_id: str = None) -> List[Dict[str, Any]]:
        """
        Create chunks for treatment data with both emergency and treatment keywords
        
        Args:
            text: Input text
            emergency_keywords: Emergency keywords
            treatment_keywords: Treatment keywords
            chunk_size: Size of each chunk
            doc_id: Document ID for tracking
            
        Returns:
            List of chunk dictionaries
        """
        if not treatment_keywords or pd.isna(treatment_keywords):
            return []
        
        chunks = []
        em_keywords = emergency_keywords.split("|") if emergency_keywords else []
        tr_keywords = treatment_keywords.split("|") if treatment_keywords else []
        
        # Process treatment keywords as primary (since this is treatment-focused data)
        for i, tr_keyword in enumerate(tr_keywords):
            tr_pos = text.lower().find(tr_keyword.lower())
            
            if tr_pos != -1:
                # Find closest emergency keyword for context
                closest_em_keyword = None
                closest_distance = float('inf')
                
                for em_keyword in em_keywords:
                    em_pos = text.lower().find(em_keyword.lower())
                    if em_pos != -1:
                        distance = abs(tr_pos - em_pos)
                        if distance < closest_distance and distance < chunk_size:
                            closest_distance = distance
                            closest_em_keyword = em_keyword
                
                # Calculate chunk boundaries
                if closest_em_keyword:
                    # Center between both keywords
                    em_pos = text.lower().find(closest_em_keyword.lower())
                    center = (tr_pos + em_pos) // 2
                else:
                    # Center on treatment keyword
                    center = tr_pos
                
                start = max(0, center - chunk_size // 2)
                end = min(len(text), center + chunk_size // 2)
                
                chunk_text = text[start:end].strip()
                
                if chunk_text:
                    chunk_info = {
                        "text": chunk_text,
                        "primary_keyword": tr_keyword,
                        "emergency_keywords": emergency_keywords,
                        "treatment_keywords": treatment_keywords,
                        "closest_emergency_keyword": closest_em_keyword,
                        "keyword_distance": closest_distance if closest_em_keyword else None,
                        "chunk_start": start,
                        "chunk_end": end,
                        "chunk_id": f"{doc_id}_treatment_chunk_{i}" if doc_id else f"treatment_chunk_{i}",
                        "source_doc_id": doc_id
                    }
                    chunks.append(chunk_info)
        
        return chunks
    
    def process_emergency_chunks(self) -> List[Dict[str, Any]]:
        """Process emergency data into chunks"""
        if self.emergency_data is None:
            raise ValueError("Emergency data not loaded. Call load_filtered_data() first.")
        
        all_chunks = []
        
        # Add progress bar with leave=False to avoid cluttering
        for idx, row in tqdm(self.emergency_data.iterrows(), 
                        total=len(self.emergency_data),
                        desc="Processing emergency documents",
                        unit="doc",
                        leave=False):
            if pd.notna(row.get('clean_text')) and pd.notna(row.get('matched')):
                chunks = self.create_keyword_centered_chunks(
                    text=row['clean_text'],
                    matched_keywords=row['matched'],
                    chunk_size=self.chunk_size,
                    doc_id=str(row.get('id', idx))
                )
                
                # Add metadata to each chunk
                for chunk in chunks:
                    chunk.update({
                        'source_type': 'emergency',
                        'source_title': row.get('title', ''),
                        'source_url': row.get('url', ''),
                        'has_emergency': row.get('has_emergency', True),
                        'doc_type': row.get('type', 'emergency')
                    })
                
                all_chunks.extend(chunks)
        
        self.emergency_chunks = all_chunks
        logger.info(f"Completed processing emergency data: {len(all_chunks)} chunks generated")
        return all_chunks
    
    def process_treatment_chunks(self) -> List[Dict[str, Any]]:
        """Process treatment data into chunks"""
        if self.treatment_data is None:
            raise ValueError("Treatment data not loaded. Call load_filtered_data() first.")
        
        all_chunks = []
        
        # Add progress bar with leave=False to avoid cluttering
        for idx, row in tqdm(self.treatment_data.iterrows(),
                        total=len(self.treatment_data),
                        desc="Processing treatment documents",
                        unit="doc",
                        leave=False):
            if (pd.notna(row.get('clean_text')) and 
                pd.notna(row.get('treatment_matched'))):
                
                chunks = self.create_dual_keyword_chunks(
                    text=row['clean_text'],
                    emergency_keywords=row.get('matched', ''),
                    treatment_keywords=row['treatment_matched'],
                    chunk_size=self.chunk_size,
                    doc_id=str(row.get('id', idx))
                )
                
                # Add metadata to each chunk
                for chunk in chunks:
                    chunk.update({
                        'source_type': 'treatment',
                        'source_title': row.get('title', ''),
                        'source_url': row.get('url', ''),
                        'has_emergency': row.get('has_emergency', True),
                        'has_treatment': row.get('has_treatment', True),
                        'doc_type': row.get('type', 'treatment')
                    })
                
                all_chunks.extend(chunks)
        
        self.treatment_chunks = all_chunks
        logger.info(f"Completed processing treatment data: {len(all_chunks)} chunks generated")
        return all_chunks
    
    def _get_chunk_hash(self, text: str) -> str:
        """Generate hash for chunk text to use as cache key"""
        import hashlib
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _load_embedding_cache(self, cache_file: str) -> dict:
        """Load embedding cache from file"""
        import pickle
        import os
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                logger.warning(f"Could not load cache file {cache_file}, starting fresh")
                return {}
        return {}

    def _save_embedding_cache(self, cache: dict, cache_file: str):
        """Save embedding cache to file"""
        import pickle
        import os
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'wb') as f:
            pickle.dump(cache, f)

    def generate_embeddings(self, chunks: List[Dict[str, Any]], 
                          chunk_type: str = "emergency") -> np.ndarray:
        """
        Generate embeddings for chunks with caching support
        
        Args:
            chunks: List of chunk dictionaries
            chunk_type: Type of chunks ("emergency" or "treatment")
            
        Returns:
            numpy array of embeddings
        """
        logger.info(f"Starting embedding generation for {len(chunks)} {chunk_type} chunks...")
        
        # Cache setup
        cache_dir = self.models_dir / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{chunk_type}_embeddings_cache.pkl"
        
        # Load existing cache
        cache = self._load_embedding_cache(str(cache_file))
        
        cached_embeddings = []
        to_embed = []
        
        # Check cache for each chunk
        for i, chunk in enumerate(chunks):
            chunk_hash = self._get_chunk_hash(chunk['text'])
            if chunk_hash in cache:
                cached_embeddings.append((i, cache[chunk_hash]))
            else:
                to_embed.append((i, chunk_hash, chunk['text']))
        
        logger.info(f"Cache status: {len(cached_embeddings)} cached, {len(to_embed)} new chunks to embed")
        
        # Generate embeddings for new chunks
        new_embeddings = []
        if to_embed:
            # Load model
            model = self.load_embedding_model()
            texts = [text for _, _, text in to_embed]
            
            # Generate embeddings in batches with clear progress
            batch_size = 32
            total_batches = (len(texts) + batch_size - 1) // batch_size
            
            logger.info(f"Processing {len(texts)} new {chunk_type} texts in {total_batches} batches...")
            
            for i in tqdm(range(0, len(texts), batch_size), 
                         desc=f"Embedding {chunk_type} subset",
                         total=total_batches,
                         unit="batch", 
                         leave=False):
                batch_texts = texts[i:i + batch_size]
                batch_emb = model.encode(
                    batch_texts,
                    show_progress_bar=False
                )
                new_embeddings.extend(batch_emb)
            
            # Update cache with new embeddings
            for (_, chunk_hash, _), emb in zip(to_embed, new_embeddings):
                cache[chunk_hash] = emb
            
            # Save updated cache
            self._save_embedding_cache(cache, str(cache_file))
            logger.info(f"Updated cache with {len(new_embeddings)} new embeddings")
        
        # Combine cached and new embeddings in correct order
        all_embeddings = [None] * len(chunks)
        
        # Place cached embeddings
        for idx, emb in cached_embeddings:
            all_embeddings[idx] = emb
        
        # Place new embeddings
        for (idx, _, _), emb in zip(to_embed, new_embeddings):
            all_embeddings[idx] = emb
        
        # Convert to numpy array
        result = np.vstack(all_embeddings)
        logger.info(f"Completed embedding generation: shape {result.shape}")
        
        return result
    
    def build_annoy_index(self, embeddings: np.ndarray, 
                         index_name: str, n_trees: int = 15) -> AnnoyIndex:
        """
        Build ANNOY index from embeddings
        
        Args:
            embeddings: Numpy array of embeddings
            index_name: Name for the index file
            n_trees: Number of trees for ANNOY index
            
        Returns:
            Built ANNOY index
        """
        logger.info(f"Building ANNOY index: {index_name}")
        
        # Create ANNOY index
        index = AnnoyIndex(self.embedding_dim, 'angular')  # angular = cosine similarity
        
        # Add vectors to index
        for i, embedding in enumerate(embeddings):
            index.add_item(i, embedding)
        
        # Build index
        index.build(n_trees)
        
        # Save index
        index_path = self.models_dir / "indices" / "annoy" / f"{index_name}.ann"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index.save(str(index_path))
        
        logger.info(f"ANNOY index saved to: {index_path}")
        return index
    
    def save_chunks_and_embeddings(self, chunks: List[Dict[str, Any]], 
                                 embeddings: np.ndarray, chunk_type: str):
        """
        Save chunks metadata and embeddings
        
        Args:
            chunks: List of chunk dictionaries
            embeddings: Numpy array of embeddings
            chunk_type: Type of chunks ("emergency" or "treatment")
        """
        logger.info(f"Saving {chunk_type} chunks and embeddings...")
        
        # Create output directories
        embeddings_dir = self.models_dir / "embeddings"
        embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        # Save chunks metadata
        chunks_file = embeddings_dir / f"{chunk_type}_chunks.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        # Save embeddings
        embeddings_file = embeddings_dir / f"{chunk_type}_embeddings.npy"
        np.save(embeddings_file, embeddings)
        
        logger.info(f"Saved {chunk_type} data:")
        logger.info(f"  - Chunks: {chunks_file}")
        logger.info(f"  - Embeddings: {embeddings_file}")
    
    def validate_data_quality(self) -> Dict[str, Any]:
        """
        Validate data quality and return statistics
        
        Returns:
            Dictionary with validation statistics
        """
        logger.info("Validating data quality...")
        
        validation_report = {
            "emergency_data": {},
            "treatment_data": {},
            "chunks": {},
            "embeddings": {}
        }
        
        # Emergency data validation
        if self.emergency_data is not None:
            validation_report["emergency_data"] = {
                "total_records": len(self.emergency_data),
                "records_with_text": self.emergency_data['clean_text'].notna().sum(),
                "records_with_keywords": self.emergency_data['matched'].notna().sum(),
                "avg_text_length": self.emergency_data['clean_text'].str.len().mean()
            }
        
        # Treatment data validation
        if self.treatment_data is not None:
            validation_report["treatment_data"] = {
                "total_records": len(self.treatment_data),
                "records_with_text": self.treatment_data['clean_text'].notna().sum(),
                "records_with_emergency_keywords": self.treatment_data['matched'].notna().sum(),
                "records_with_treatment_keywords": self.treatment_data['treatment_matched'].notna().sum(),
                "avg_text_length": self.treatment_data['clean_text'].str.len().mean()
            }
        
        # Chunks validation
        validation_report["chunks"] = {
            "emergency_chunks": len(self.emergency_chunks),
            "treatment_chunks": len(self.treatment_chunks),
            "total_chunks": len(self.emergency_chunks) + len(self.treatment_chunks)
        }
        
        if self.emergency_chunks:
            avg_chunk_length = np.mean([len(chunk['text']) for chunk in self.emergency_chunks])
            validation_report["chunks"]["avg_emergency_chunk_length"] = avg_chunk_length
        
        if self.treatment_chunks:
            avg_chunk_length = np.mean([len(chunk['text']) for chunk in self.treatment_chunks])
            validation_report["chunks"]["avg_treatment_chunk_length"] = avg_chunk_length
        
        # Check if embeddings exist
        embeddings_dir = self.models_dir / "embeddings"
        if embeddings_dir.exists():
            emergency_emb_file = embeddings_dir / "emergency_embeddings.npy"
            treatment_emb_file = embeddings_dir / "treatment_embeddings.npy"
            
            validation_report["embeddings"] = {
                "emergency_embeddings_exist": emergency_emb_file.exists(),
                "treatment_embeddings_exist": treatment_emb_file.exists()
            }
            
            if emergency_emb_file.exists():
                emb = np.load(emergency_emb_file)
                validation_report["embeddings"]["emergency_embeddings_shape"] = emb.shape
            
            if treatment_emb_file.exists():
                emb = np.load(treatment_emb_file)
                validation_report["embeddings"]["treatment_embeddings_shape"] = emb.shape
        
        # Save validation report
        report_file = self.models_dir / "data_validation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(validation_report, f, indent=2, default=str)
        
        logger.info(f"Validation report saved to: {report_file}")
        return validation_report
    
    def process_all_data(self) -> Dict[str, Any]:
        """
        Complete data processing pipeline
        
        Returns:
            Processing summary
        """
        logger.info("Starting complete data processing pipeline...")
        
        # Step 1: Load filtered data
        self.load_filtered_data()
        
        # Step 2: Process chunks
        emergency_chunks = self.process_emergency_chunks()
        treatment_chunks = self.process_treatment_chunks()
        
        # Step 3: Generate embeddings
        emergency_embeddings = self.generate_embeddings(emergency_chunks, "emergency")
        treatment_embeddings = self.generate_embeddings(treatment_chunks, "treatment")
        
        # Step 4: Build ANNOY indices
        self.emergency_index = self.build_annoy_index(emergency_embeddings, "emergency_index")
        self.treatment_index = self.build_annoy_index(treatment_embeddings, "treatment_index")
        
        # Step 5: Save data
        self.save_chunks_and_embeddings(emergency_chunks, emergency_embeddings, "emergency")
        self.save_chunks_and_embeddings(treatment_chunks, treatment_embeddings, "treatment")
        
        # Step 6: Validate data quality
        validation_report = self.validate_data_quality()
        
        # Summary
        summary = {
            "status": "completed",
            "emergency_chunks": len(emergency_chunks),
            "treatment_chunks": len(treatment_chunks),
            "emergency_embeddings_shape": emergency_embeddings.shape,
            "treatment_embeddings_shape": treatment_embeddings.shape,
            "indices_created": ["emergency_index.ann", "treatment_index.ann"],
            "validation_report": validation_report
        }
        
        logger.info("Data processing pipeline completed successfully!")
        logger.info(f"Summary: {summary}")
        
        return summary

def main():
    """Main function for testing the data processor"""
    # Initialize processor
    processor = DataProcessor()
    
    # Run complete pipeline
    summary = processor.process_all_data()
    
    print("\n" + "="*50)
    print("DATA PROCESSING COMPLETED")
    print("="*50)
    print(f"Emergency chunks: {summary['emergency_chunks']}")
    print(f"Treatment chunks: {summary['treatment_chunks']}")
    print(f"Emergency embeddings: {summary['emergency_embeddings_shape']}")
    print(f"Treatment embeddings: {summary['treatment_embeddings_shape']}")
    print(f"Indices created: {summary['indices_created']}")
    print("="*50)

if __name__ == "__main__":
    main() 