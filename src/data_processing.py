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

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Any
from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Main data processing class for OnCall.ai RAG system"""
    
    def __init__(self, base_dir: str = None):
        """
        Initialize DataProcessor
        
        Args:
            base_dir: Base directory path for the project
        """
        self.base_dir = Path(base_dir).resolve() if base_dir else Path(__file__).parent.parent.resolve()
        self.dataset_dir = (self.base_dir / "dataset" / "dataset").resolve()  # 修正为实际的数据目录
        self.models_dir = (self.base_dir / "models").resolve()
        
        # Model configuration
        self.embedding_model_name = "NeuML/pubmedbert-base-embeddings"
        self.embedding_dim = 768  # PubMedBERT dimension
        self.chunk_size = 512
        
        # Initialize model (will be loaded when needed)
        self.embedding_model = None
        
        # Data containers
        self.emergency_data = None
        self.treatment_data = None
        self.emergency_chunks = []
        self.treatment_chunks = []
        
        logger.info(f"Initialized DataProcessor with:")
        logger.info(f"  Base directory: {self.base_dir}")
        logger.info(f"  Dataset directory: {self.dataset_dir}")
        logger.info(f"  Models directory: {self.models_dir}")
    
    def load_embedding_model(self):
        """Load the embedding model"""
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info("Embedding model loaded successfully")
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
                                     chunk_size: int = 512, doc_id: str = None) -> List[Dict[str, Any]]:
        """
        Create chunks centered around matched keywords
        
        Args:
            text: Input text
            matched_keywords: Pipe-separated keywords (e.g., "MI|chest pain|fever")
            chunk_size: Size of each chunk
            doc_id: Document ID for tracking
            
        Returns:
            List of chunk dictionaries
        """
        if not matched_keywords or pd.isna(matched_keywords):
            return []
        
        chunks = []
        keywords = matched_keywords.split("|") if matched_keywords else []
        
        for i, keyword in enumerate(keywords):
            # Find keyword position in text (case insensitive)
            keyword_pos = text.lower().find(keyword.lower())
            
            if keyword_pos != -1:
                # Calculate chunk boundaries centered on keyword
                start = max(0, keyword_pos - chunk_size // 2)
                end = min(len(text), keyword_pos + chunk_size // 2)
                
                # Extract chunk text
                chunk_text = text[start:end].strip()
                
                if chunk_text:  # Only add non-empty chunks
                    chunk_info = {
                        "text": chunk_text,
                        "primary_keyword": keyword,
                        "all_matched_keywords": matched_keywords,
                        "keyword_position": keyword_pos,
                        "chunk_start": start,
                        "chunk_end": end,
                        "chunk_id": f"{doc_id}_chunk_{i}" if doc_id else f"chunk_{i}",
                        "source_doc_id": doc_id
                    }
                    chunks.append(chunk_info)
        
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
        logger.info("Processing emergency data into chunks...")
        
        if self.emergency_data is None:
            raise ValueError("Emergency data not loaded. Call load_filtered_data() first.")
        
        all_chunks = []
        
        for idx, row in self.emergency_data.iterrows():
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
        logger.info(f"Generated {len(all_chunks)} emergency chunks")
        return all_chunks
    
    def process_treatment_chunks(self) -> List[Dict[str, Any]]:
        """Process treatment data into chunks"""
        logger.info("Processing treatment data into chunks...")
        
        if self.treatment_data is None:
            raise ValueError("Treatment data not loaded. Call load_filtered_data() first.")
        
        all_chunks = []
        
        for idx, row in self.treatment_data.iterrows():
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
        logger.info(f"Generated {len(all_chunks)} treatment chunks")
        return all_chunks
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]], 
                          chunk_type: str = "emergency") -> np.ndarray:
        """
        Generate embeddings for chunks
        
        Args:
            chunks: List of chunk dictionaries
            chunk_type: Type of chunks ("emergency" or "treatment")
            
        Returns:
            numpy array of embeddings
        """
        logger.info(f"Generating embeddings for {len(chunks)} {chunk_type} chunks...")
        
        # Load model if not already loaded
        model = self.load_embedding_model()
        
        # Extract text from chunks
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings in batches
        batch_size = 32
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = model.encode(batch_texts, show_progress_bar=True)
            embeddings.append(batch_embeddings)
        
        # Concatenate all embeddings
        all_embeddings = np.vstack(embeddings)
        
        logger.info(f"Generated embeddings shape: {all_embeddings.shape}")
        return all_embeddings
    
    def build_annoy_index(self, embeddings: np.ndarray, 
                         index_name: str, n_trees: int = 10) -> AnnoyIndex:
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
        emergency_index = self.build_annoy_index(emergency_embeddings, "emergency_index")
        treatment_index = self.build_annoy_index(treatment_embeddings, "treatment_index")
        
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