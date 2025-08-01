"""PDF content extraction and processing."""

import os
import io
from typing import List
import numpy as np
import pandas as pd

# PDF processing imports
import pdfplumber
import fitz  # PyMuPDF
import easyocr
from PIL import Image

# LlamaIndex imports
from llama_index.core import Document, SimpleDirectoryReader


def extract_pdf_text(pdf_path: str) -> str:
    """Extract plain text from PDF file.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        Extracted text content.
    """
    text_content = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
        return text_content
    except Exception as e:
        print(f"❌ PDF text extraction error {pdf_path}: {e}")
        return ""


def extract_tables_from_pdf(pdf_path: str) -> Document:
    """Extract tables from PDF and convert to markdown format.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        Document containing extracted table content.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_tables = []
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table_num, table in enumerate(tables):
                    if table:
                        # Convert to DataFrame then markdown
                        df = pd.DataFrame(table[1:], columns=table[0])
                        table_text = f"Page{page_num+1}Table{table_num+1}:\n{df.to_markdown(index=False)}"
                        all_tables.append(table_text)

            return Document(text="\n\n".join(all_tables))
    except Exception as e:
        print(f"⚠️ pdfplumber table extraction failed: {e}")
        return Document(text="")


def extract_images_ocr_from_pdf(pdf_path: str) -> Document:
    """Extract text from images in PDF using OCR.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        Document containing OCR-extracted text.
    """
    try:
        ocr_reader = easyocr.Reader(['en'], gpu=False)
        doc = fitz.open(pdf_path)

        image_texts = []
        total_images = 0

        for page_num, page in enumerate(doc):
            images = page.get_images(full=True)
            total_images += len(images)

            for img_index, img in enumerate(images):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    # Convert to PIL image and perform OCR
                    image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    ocr_result = ocr_reader.readtext(np.array(image_pil), detail=0)
                    ocr_text = "\n".join(ocr_result).strip()

                    if ocr_text:
                        image_texts.append(f"Page {page_num+1} image {img_index+1}:\n{ocr_text}")

                except Exception as e:
                    continue

        doc.close()

        all_ocr_text = "\n\n".join(image_texts)
        if image_texts:
            print(f"✅ Extracted text from {len(image_texts)}/{total_images} images")

        return Document(text=all_ocr_text)

    except Exception as e:
        print(f"⚠️ Image OCR extraction failed {pdf_path}: {e}")
        return Document(text="")


def extract_pdf_content_enhanced(pdf_path: str) -> List[Document]:
    """Enhanced PDF content extraction combining text, tables, and OCR.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        List of Document objects containing extracted content.
    """
    documents = []

    print(f"🔄 Processing PDF: {os.path.basename(pdf_path)}")

    # 1. Basic text extraction
    try:
        text_docs = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
        documents.extend(text_docs)
        print(f"✅ Extracted basic text content")
    except Exception as e:
        print(f"❌ Basic text extraction failed: {e}")

    # 2. Table extraction
    table_doc = extract_tables_from_pdf(pdf_path)
    if table_doc.text.strip():
        documents.append(table_doc)

    # 3. Image OCR extraction
    ocr_doc = extract_images_ocr_from_pdf(pdf_path)
    if ocr_doc.text.strip():
        documents.append(ocr_doc)

    print(f"✅ Created {len(documents)} document objects in total")
    return documents