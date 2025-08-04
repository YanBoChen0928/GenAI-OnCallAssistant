#!/usr/bin/env python3
"""
Generate mapping.json from combined_er_symptoms_diagnoses.csv
This script creates the mapping file needed for the customization pipeline.
"""

import csv
import json
import os
from pathlib import Path

def csv_to_mapping_json():
    """Convert CSV to mapping.json format"""
    
    # Define paths
    processing_dir = Path(__file__).parent
    customization_dir = processing_dir.parent
    csv_path = customization_dir / "docs" / "combined_er_symptoms_diagnoses.csv"
    output_path = processing_dir / "mapping.json"
    
    # Read CSV and convert to mapping format
    mappings = []
    
    with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:  # Handle BOM
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Skip empty rows
            if not row.get('PDF Abbreviation'):
                continue
                
            # Extract symptoms and diagnoses
            symptoms_raw = row['ER Symptom (Surface)'].strip()
            diagnoses_raw = row['Underlying Diagnosis (Core)'].strip()
            
            # Split symptoms by comma and clean
            symptoms = [s.strip() for s in symptoms_raw.split(',') if s.strip()]
            
            # Split diagnoses by comma and clean
            diagnoses = [d.strip() for d in diagnoses_raw.split(',') if d.strip()]
            
            # Create PDF filename based on abbreviation
            pdf_name = get_pdf_filename(row['PDF Abbreviation'])
            
            # Create mapping entry
            mapping = {
                "pdf": pdf_name,
                "symptoms": symptoms,
                "diagnoses": diagnoses
            }
            
            mappings.append(mapping)
    
    # Write to JSON file
    with open(output_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(mappings, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated mapping.json with {len(mappings)} entries")
    print(f"📄 Output saved to: {output_path}")
    
    # Verify all PDFs exist
    docs_dir = customization_dir / "docs"
    missing_pdfs = []
    
    for mapping in mappings:
        pdf_path = docs_dir / mapping['pdf']
        if not pdf_path.exists():
            missing_pdfs.append(mapping['pdf'])
    
    if missing_pdfs:
        print(f"\n⚠️ Warning: {len(missing_pdfs)} PDF files not found:")
        for pdf in missing_pdfs[:5]:  # Show first 5
            print(f"   - {pdf}")
        if len(missing_pdfs) > 5:
            print(f"   ... and {len(missing_pdfs) - 5} more")
    else:
        print("\n✅ All PDF files found in docs directory")
    
    return mappings

def get_pdf_filename(abbreviation):
    """Convert abbreviation to actual PDF filename based on files in docs directory"""
    
    # Mapping of abbreviations to actual PDF filenames
    pdf_mapping = {
        "SpinalCordEmergencies": "Recognizing Spinal Cord Emergencies.pdf",
        "DizzinessApproach": "*Dizziness - A Diagnostic Approach.pdf",
        "CodeHeadache": "*Code Headache - Development of a protocol for optimizing headache management in the emergency room.pdf",
        "EarlyAFTherapy": "Early Rhythm-Control Therapy in Patients with Atrial Fibrillation.pdf",
        "2024ESC_AF_Guidelines": "2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the European Association for Cardio-Thoracic Surgery.pdf",
        "PregnancyBleeding_ED": "What assessment, intervention and diagnostics should women with early pregnancy bleeding receive in the emergency department and when A scoping review and synthesis of evidence.pdf",
        "UGIB_Guideline": "acg_clinical_guideline__upper_gastrointestinal_and.14.pdf",
        "PulmonaryEmbolism": "Acute Pulmonary Embolism A Review.pdf",
        "CAP_Review": "Community-Acquired Pneumonia.pdf",
        "AcuteIschemicStroke_Guideline": "Guidelines for the Early Management of Patients With Acute Ischemic Stroke.pdf",
        "ChestPain_Guideline_2021": "2021 Guideline for the Evaluation and Diagnosis of Chest Pain.pdf",
        "FUO_Neutropenia_2024": "2024 update of the AGIHO guideline on diagnosis and empirical treatment of fever of unknown origin (FUO) in adult neutropenic patients with solid tumours and hematological malignancies.pdf",
        "Eclampsia_ER_Management": "*Management of eclampsia in the accident and emergency department.pdf",
        "UTI_Mazzulli": "Diagnosis and Management of simple and complicated urinary tract infections (UTIs).pdf",
        "Pediatric_Seizures_2016": "J Paediatrics Child Health - 2016 - Lawton - Seizures in the paediatric emergency department.pdf",
        "PregnancyLoss_Review": "A REVIEW OF THE MANAGEMENT OF LOSS OF PREGNANCY IN THE EMERGENCY DEPARTMENT.pdf",
        "FUO_Children": "Update on Fever of Unknown Origin in Children Focus on Etiologies and Clinical Apporach.pdf",
        # New entries based on actual files in docs directory
        "MyastheniaGravis": "[Transition of Japanese clinical guidelines for myasthenia gravis].pdf",
        "AcutePorphyrias": "AGA Clinical Practice Update on Diagnosis and Management of Acute Hepatic Porphyrias- Expert Review.pdf",
        "Botulism": "Clinical Guidelines for Diagnosis and Treatment of Botulism, 2021.pdf",
        "WilsonsDisease": "EASL-ERN Clinical Practice Guidelines on Wilsons disease.pdf",
        "HereditaryAngioedema": "The international WAO:EAACI guideline for the management of hereditary angioedema-The 2021 revision and update.pdf",
    }
    
    # Return mapped filename or create a generic one based on abbreviation
    return pdf_mapping.get(abbreviation, f"{abbreviation}.pdf")

if __name__ == "__main__":
    csv_to_mapping_json()