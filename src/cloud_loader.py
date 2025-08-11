"""Cloud Data Loader - Downloads model data from HuggingFace Dataset"""

import os
from pathlib import Path
from huggingface_hub import hf_hub_download
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CloudDataLoader:
    """HuggingFace Dataset data loader"""
    
    def __init__(self):
        self.dataset_repo = "ybchen928/oncall-guide-ai-models"
        self.use_cloud = os.getenv('USE_CLOUD_DATA', 'true').lower() == 'true'
    
    def get_model_file_path(self, filename: str) -> str:
        """Get model file path for General Pipeline"""
        if self.use_cloud:
            return hf_hub_download(
                repo_id=self.dataset_repo,
                filename=filename,
                repo_type="dataset"
            )
        else:
            # Local development mode
            return str(Path(__file__).parent.parent / filename)
    
    def get_customization_file_path(self, filename: str) -> str:
        """Get customization data file path for Customization Pipeline"""
        if self.use_cloud:
            return hf_hub_download(
                repo_id=self.dataset_repo,
                filename=f"customization_data/{filename}",
                repo_type="dataset"
            )
        else:
            # Local development mode - correct path to processing folder
            return str(Path(__file__).parent.parent / "customization" / "processing" / filename)

# Global instance
cloud_loader = CloudDataLoader()
