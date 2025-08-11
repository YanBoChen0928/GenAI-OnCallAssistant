"""Customization System Cloud Configuration"""

import os
from pathlib import Path
from huggingface_hub import hf_hub_download
import logging

logger = logging.getLogger(__name__)

class CustomizationCloudLoader:
    """Customization-specific cloud data loader"""
    
    def __init__(self):
        self.dataset_repo = "ybchen928/oncall-guide-ai-models"
        self.use_cloud = os.getenv('USE_CLOUD_DATA', 'true').lower() == 'true'
    
    def get_processing_file_path(self, relative_path: str) -> str:
        """Get processing file path for Customization Pipeline"""
        if self.use_cloud:
            return hf_hub_download(
                repo_id=self.dataset_repo,
                filename=f"customization_data/processing/{relative_path}",
                repo_type="dataset"
            )
        else:
            # Local development mode - correct path to processing folder
            base_path = Path(__file__).parent.parent.parent / "customization" / "processing"
            return str(base_path / relative_path)
    
    def preload_all_processing_files(self) -> tuple:
        """Preload all processing files and return directory paths"""
        if self.use_cloud:
            # Download all required files
            files_to_download = [
                "embeddings/document_index.json",
                "embeddings/tag_embeddings.json", 
                "embeddings/document_tag_mapping.json",
                "embeddings/chunk_embeddings.json",
                "indices/chunk_mappings.json",
                "indices/tag_mappings.json",
                "indices/annoy_metadata.json",
                "indices/chunk_embeddings.ann",
                "indices/tag_embeddings.ann",
                "mapping.json"
            ]
            
            # Download each file to ensure they're all cached
            for file_path in files_to_download:
                try:
                    self.get_processing_file_path(file_path)
                    logger.info(f"Downloaded: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to download {file_path}: {e}")
            
            # Get directory paths from downloaded files
            embeddings_dir = Path(self.get_processing_file_path("embeddings/document_index.json")).parent
            indices_dir = Path(self.get_processing_file_path("indices/chunk_mappings.json")).parent
            
            return str(embeddings_dir), str(indices_dir)
        else:
            # Local development mode
            base_path = Path(__file__).parent.parent.parent / "customization" / "processing"
            return str(base_path / "embeddings"), str(base_path / "indices")

# Global instance
customization_loader = CustomizationCloudLoader()
