"""Data loading and PDF processing."""

from .loaders import load_annotations, filter_pdf_files

# Try to import PDF processing functions, but handle missing dependencies gracefully
try:
    from .pdf_processing import (
        extract_pdf_text, 
        extract_tables_from_pdf,
        extract_images_ocr_from_pdf,
        extract_pdf_content_enhanced
    )
    PDF_PROCESSING_AVAILABLE = True
    __all__ = [
        'load_annotations', 'filter_pdf_files',
        'extract_pdf_text', 'extract_tables_from_pdf', 
        'extract_images_ocr_from_pdf', 'extract_pdf_content_enhanced'
    ]
except ImportError as e:
    print(f"⚠️ PDF processing not available: {e}")
    print("📝 Only working with existing embeddings")
    PDF_PROCESSING_AVAILABLE = False
    __all__ = ['load_annotations', 'filter_pdf_files']