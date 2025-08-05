# Hospital Customization System - Tag Structure & Keyword Analysis

## Executive Summary

The hospital customization system implements a sophisticated two-stage retrieval architecture with **21 medical PDFs**, **134 unique medical tags**, and **4,764 text chunks** processed through BGE-Large-Medical embeddings and ANNOY indices.

## System Architecture

### Core Components
- **Embedding Model**: BGE-Large-Medical (1024 dimensions)
- **Search Method**: Two-stage ANNOY retrieval with angular similarity
- **Document Processing**: 256-character chunks with 25-character overlap
- **Tag Structure**: 134 medical concepts (symptoms + diagnoses + treatments)

### Processing Pipeline
1. **Stage 1**: Tag-based document filtering using medical concept embeddings
2. **Stage 2**: Chunk-level retrieval within relevant documents
3. **Filtering**: Top-P (0.6) + minimum similarity (0.25) thresholds

## Tag Structure Analysis

### Keyword Distribution
| Category | Count | Examples |
|----------|-------|----------|
| **Symptoms** | 45 tags | palpitations, dyspnea, syncope, chest pain |
| **Diagnoses** | 44 tags | meningitis, acute coronary syndrome, heart failure |
| **Ambiguous/Mixed** | 45 tags | Complex medical terms spanning categories |

### Frequency Patterns
- **High Frequency (3+ occurrences)**: palpitations, dyspnea, syncope
- **Medium Frequency (2 occurrences)**: chest pain, emotional distress, fever, meningitis
- **Low Frequency (1 occurrence)**: 121 specific medical terms

## Document Coverage Analysis

### Top Documents by Content Volume
1. **Chest Pain Guidelines** (1,053 chunks) - Comprehensive cardiac evaluation
2. **Atrial Fibrillation Guidelines** (1,047 chunks) - Complete arrhythmia management  
3. **Stroke Management** (703 chunks) - Acute neurological emergencies
4. **Wilson's Disease** (415 chunks) - Specialized genetic condition
5. **Hereditary Angioedema** (272 chunks) - Rare immune disorder

### Dual Coverage (Symptoms + Diagnoses)
All 21 PDFs contain both symptom and diagnosis keywords, with top documents having:
- **Spinal Cord Emergencies**: 5 symptoms, 7 diagnoses (12 total)
- **Dizziness Approach**: 4 symptoms, 8 diagnoses (12 total)
- **Headache Management**: 3 symptoms, 6 diagnoses (9 total)

## Recommended Test Query Strategy

### 1. Broad Query Testing (High-Frequency Keywords)
```
• "palpitations" - Expected: 3 documents
• "dyspnea" - Expected: 3 documents  
• "syncope" - Expected: 3 documents
• "meningitis" - Expected: 2 documents
• "acute coronary syndrome" - Expected: 2 documents
```

### 2. Medium Specificity Testing
```
• "chest pain" - Expected: 2 documents
• "heart failure" - Expected: 2 documents
• "fever" - Expected: 2 documents
```

### 3. Specific Query Testing (Low-Frequency)
```
• "back pain" - Expected: 1 document (Spinal Cord Emergencies)
• "spinal cord compression" - Expected: 1 document
• "vertebral fracture" - Expected: 1 document
```

### 4. Combined Query Testing
```
• "palpitations chest pain" - Expected: Multiple documents
• "dyspnea heart failure" - Expected: Cardiac-focused results
• "fever meningitis" - Expected: Infection-focused results
```

### 5. Semantic Similarity Testing
```
• "emergency cardiac arrest" - Tests semantic matching beyond exact keywords
• "patient presenting with acute symptoms" - Tests broad medical query handling
• "rare genetic disorder" - Tests specialized condition retrieval
```

## System Performance Characteristics

### Expected Behavior
- **Stage 1 Filtering**: Should identify 5-20 relevant tags per query
- **Document Selection**: Should narrow to 2-8 relevant documents
- **Stage 2 Retrieval**: Should return 3-10 high-quality chunks
- **Similarity Thresholds**: 25% minimum, Top-P filtering at 60%

### Quality Indicators
- **High Precision**: Specific queries should return 1-2 documents
- **Good Recall**: Broad queries should find all relevant documents  
- **Semantic Matching**: Related terms should retrieve appropriate content
- **Fallback Robustness**: System should handle edge cases gracefully

## Key Insights for Testing

### 1. Frequency-Based Test Coverage
- Use high-frequency terms to test broad retrieval capabilities
- Use medium-frequency terms to validate balanced precision/recall
- Use low-frequency terms to test specific document targeting

### 2. Medical Domain Validation
- BGE-Large-Medical embeddings should excel at medical concept similarity
- System should handle medical terminology variations and synonyms
- Diagnostic reasoning chains should be retrievable through symptom queries

### 3. Two-Stage Architecture Benefits
- Tag-based filtering reduces search space efficiently
- Chunk-level retrieval provides precise content extraction
- Fallback mechanisms ensure robustness for edge cases

## Recommendations for Query Testing

1. **Start with high-frequency keywords** to validate basic system functionality
2. **Test symptom→diagnosis pathways** using medically coherent combinations
3. **Validate edge cases** with non-exact but semantically related queries
4. **Monitor performance metrics** including precision, recall, and response times
5. **Test fallback behavior** when primary retrieval fails

This analysis provides a comprehensive foundation for understanding and testing the hospital customization system's tag structure and retrieval capabilities.