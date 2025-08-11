---
title: OnCall.ai - Medical Emergency Assistant
emoji: 🏥
colorFrom: red
colorTo: blue
sdk: gradio
sdk_version: "5.38.0"
app_file: app.py
python_version: "3.11"
pinned: false
license: mit
tags:
  - medical
  - healthcare
  - RAG
  - emergency
  - clinical-guidance
  - gradio
---

# 🏥 OnCall.ai - Medical Emergency Assistant

A RAG-based medical assistant system that provides **evidence-based clinical guidance** for emergency medical situations using real medical guidelines and advanced language models.

## 🎯 What This App Does

OnCall.ai helps healthcare professionals by:
- **Processing medical queries** through multi-level validation system
- **Retrieving relevant medical guidelines** from curated emergency medicine datasets
- **Generating evidence-based clinical advice** using specialized medical LLMs (Llama3-Med42-70B)
- **Providing transparent, traceable medical guidance** with source attribution

## 🚀 How to Use

1. **Enter your medical query** in the text box (e.g., "Patient with chest pain and shortness of breath")
2. **Click Submit** to process your query through our RAG pipeline
3. **Review the response** which includes:
   - Clinical guidance based on medical guidelines
   - Evidence sources and reasoning
   - Confidence level and validation status

## ⚙️ Configuration

This app requires a **HuggingFace token** for accessing the medical language models.

### Environment Variables
- `HF_TOKEN`: Your HuggingFace API token (required for LLM access)
- `ONCALL_DEBUG`: Set to 'true' to enable debug mode (optional)

### To set up your HuggingFace token:
1. Get your token from [HuggingFace Settings](https://huggingface.co/settings/tokens)
2. In this Space, go to **Settings** → **Variables and Secrets**
3. Add `HF_TOKEN` with your token value

## 🏗️ System Architecture

### Multi-Level Query Processing Pipeline
1. **Level 1**: Predefined medical condition mapping (instant response)
2. **Level 2**: LLM-based condition extraction (Llama3-Med42-70B)
3. **Level 3**: Semantic search fallback
4. **Level 4**: Medical query validation (100% non-medical rejection)
5. **Level 5**: Generic medical search for rare conditions

### Dual-Index Retrieval System
- **Emergency Guidelines Index**: Fast retrieval for critical conditions
- **Treatment Protocols Index**: Comprehensive clinical procedures
- **Semantic Search**: Vector-based similarity matching using sentence transformers

## 📋 Technical Details

### Key Features
- **Complete RAG Pipeline**: Query → Condition Extraction → Retrieval → Generation
- **Multi-level fallback validation** for robust query processing
- **Evidence-based medical advice** with transparent source attribution
- **Gradio interface** for easy interaction
- **Environment-controlled debug mode** for development

### Models Used
- **Medical LLM**: Llama3-Med42-70B (specialized medical reasoning)
- **Embedding Model**: Sentence Transformers for semantic search
- **Retrieval**: Annoy index for fast approximate nearest neighbor search

### Dataset
- Curated medical guidelines and emergency protocols
- Treatment procedures and clinical decision trees
- Evidence-based medical knowledge base

## ⚠️ Important Disclaimers

🚨 **This tool is for educational and research purposes only.**

- **Not a substitute for professional medical advice**
- **Not for use in actual medical emergencies**
- **Always consult qualified healthcare professionals**
- **Verify all information with authoritative medical sources**

## 🔧 Development Information

### Project Structure
```
├── app.py              # Main Gradio application
├── src/                # Core modules
│   ├── user_prompt.py    # Query processing
│   ├── retrieval.py      # RAG retrieval system
│   ├── generation.py     # Medical advice generation
│   ├── llm_clients.py    # LLM interface
│   └── medical_conditions.py # Condition mapping
├── models/             # Pre-trained models and indices
│   ├── embeddings/       # Vector embeddings
│   └── indices/          # Search indices
└── requirements.txt    # Dependencies
```

### Version
- **Current Version**: 0.9.0
- **Last Updated**: 2025-07-31
- **Author**: OnCall.ai Team

---

**🔗 For technical details, issues, or contributions, please refer to the project documentation.**