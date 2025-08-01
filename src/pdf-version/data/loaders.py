"""Data loading and annotation handling."""

import json
import os
from typing import List, Dict


def load_annotations(file_path: str = 'mapping.json') -> List[Dict]:
    """Load medical annotations from JSON file.
    
    Args:
        file_path: Path to the annotations JSON file.
        
    Returns:
        List of annotation dictionaries.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            annotations = json.load(f)
        print(f"Loaded #{len(annotations)} annotated data")
        
        return annotations
    except:
        print(f"failed to find file: {file_path}")
        return []


def filter_pdf_files(annotations: List[Dict], assets_dir: str = "assets") -> List[str]:
    """Filter and validate PDF files from annotations.
    
    Args:
        annotations: List of annotation dictionaries.
        assets_dir: Directory containing PDF files.
        
    Returns:
        List of valid PDF filenames.
    """
    pdf_files = []

    for item in annotations:
        filename = item['pdf']
        filepath = os.path.join(assets_dir, filename)

        if filename.endswith('.pdf') and os.path.exists(filepath):
            pdf_files.append(filename)
        else:
            print(f"⚠️ Skipping non-pdf and non-existing files: {filename}")

    return pdf_files