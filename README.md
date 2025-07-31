# OnCall.ai - Medical Emergency Assistant

A RAG-based medical assistant system that provides evidence-based clinical guidance for emergency medical situations using real medical guidelines and advanced language models.

## 🎯 Project Overview

OnCall.ai helps healthcare professionals by:
- Processing medical queries through multi-level validation
- Retrieving relevant medical guidelines from curated datasets
- Generating evidence-based clinical advice using specialized medical LLMs
- Providing transparent, traceable medical guidance

## ✅ Current Implementation Status

### **🎉 COMPLETED MODULES (2025-07-31)**

#### **1. Multi-Level Query Processing System**
- ✅ **UserPromptProcessor** (`src/user_prompt.py`)
  - Level 1: Predefined medical condition mapping (instant response)
  - Level 2: LLM-based condition extraction (Llama3-Med42-70B)
  - Level 3: Semantic search fallback
  - Level 4: Medical query validation (100% non-medical rejection)
  - Level 5: Generic medical search for rare conditions

#### **2. Dual-Index Retrieval System**
- ✅ **BasicRetrievalSystem** (`src/retrieval.py`)
  - Emergency medical guidelines index (emergency.ann)
  - Treatment protocols index (treatment.ann)
  - Vector-based similarity search using PubMedBERT embeddings
  - Intelligent deduplication and result ranking

#### **3. Medical Knowledge Base**
- ✅ **MedicalConditions** (`src/medical_conditions.py`)
  - Predefined condition-keyword mappings
  - Medical terminology validation
  - Extensible condition database

#### **4. LLM Integration**
- ✅ **Med42-70B Client** (`src/llm_clients.py`)
  - Specialized medical language model integration
  - Dual-layer rejection detection for non-medical queries
  - Robust error handling and timeout management

#### **5. Medical Advice Generation**
- ✅ **MedicalAdviceGenerator** (`src/generation.py`)
  - RAG-based prompt construction
  - Intention-aware chunk selection (treatment/diagnosis)
  - Confidence scoring and response formatting
  - Integration with Med42-70B for clinical advice generation

#### **6. Data Processing Pipeline**
- ✅ **Processed Medical Guidelines** (`src/data_processing.py`)
  - ~4000 medical guidelines from EPFL-LLM dataset
  - Emergency subset: ~2000-2500 records
  - Treatment subset: ~2000-2500 records
  - PubMedBERT embeddings (768 dimensions)
  - ANNOY vector indices for fast retrieval

## 📊 **System Performance (Validated)**

### **Test Results Summary**
```
🎯 Multi-Level Fallback Validation: 69.2% success rate
   - Level 1 (Predefined): 100% success (instant response)
   - Level 4a (Non-medical rejection): 100% success
   - Level 4b→5 (Rare medical): 100% success

📈 End-to-End Pipeline: 100% technical completion
   - Condition extraction: 2.6s average
   - Medical guideline retrieval: 0.3s average
   - Total pipeline: 15.5s average (including generation)
```

### **Quality Metrics**
```
🔍 Retrieval Performance:
   - Guidelines retrieved: 8-9 per query
   - Relevance scores: 0.245-0.326 (good for medical domain)
   - Emergency/Treatment balance: Correctly maintained
   
🧠 Generation Quality:
   - Confidence scores: 0.90 for successful generations
   - Evidence-based responses with specific guideline references
   - Appropriate medical caution and clinical judgment emphasis
```

## 🛠️ **Technical Architecture**

### **Data Flow**
```
User Query → Multi-Level Processing → Dual-Index Retrieval → RAG Generation
     ↓              ↓                      ↓                    ↓
  Validation    Condition Mapping    Guidelines Search    Medical Advice
```

### **Core Technologies**
- **Embeddings**: NeuML/pubmedbert-base-embeddings (768D)
- **Vector Search**: ANNOY indices with angular distance
- **LLM**: m42-health/Llama3-Med42-70B (medical specialist)
- **Dataset**: EPFL-LLM medical guidelines (~4000 documents)

### **Fallback Mechanism**
```
Level 1: Predefined Mapping (0.001s) → Success: Direct return
Level 2: LLM Extraction (8-15s) → Success: Condition mapping  
Level 3: Semantic Search (1-2s) → Success: Sliding window chunks
Level 4: Medical Validation (8-10s) → Fail: Return rejection
Level 5: Generic Search (1s) → Final: General medical guidance
```

## 🚀 **NEXT PHASE: Interactive Interface**

### **🎯 Immediate Goals (Next 1-2 Days)**

#### **Phase 1: Gradio Interface Development**
- [ ] **Create `app.py`** - Interactive web interface
  - [ ] Complete pipeline integration
  - [ ] Multi-output display (advice + guidelines + technical details)
  - [ ] Environment-controlled debug mode
  - [ ] User-friendly error handling

#### **Phase 2: Local Validation Testing**
- [ ] **Manual testing** with 20-30 realistic medical queries
  - [ ] Emergency scenarios (cardiac arrest, stroke, MI)
  - [ ] Diagnostic queries (chest pain, respiratory distress)
  - [ ] Treatment protocols (medication management, procedures)
  - [ ] Edge cases (rare conditions, complex symptoms)

#### **Phase 3: HuggingFace Spaces Deployment**
- [ ] **Create requirements.txt** for deployment
- [ ] **Deploy to HF Spaces** for public testing
- [ ] **Production mode configuration** (limited technical details)
- [ ] **Performance monitoring** and user feedback collection

### **🔮 Future Enhancements (Next 1-2 Weeks)**

#### **Audio Input Integration**
- [ ] **Whisper ASR integration** for voice queries
- [ ] **Audio preprocessing** and quality validation
- [ ] **Multi-modal interface** (text + audio input)

#### **Evaluation & Metrics**
- [ ] **Faithfulness scoring** implementation
- [ ] **Automated evaluation pipeline** 
- [ ] **Clinical validation** with medical professionals
- [ ] **Performance benchmarking** against target metrics

#### **Dataset Expansion (Future)**
- [ ] **Dataset B integration** (symptom/diagnosis subsets)
- [ ] **Multi-dataset RAG** architecture
- [ ] **Enhanced medical knowledge** coverage

## 📋 **Target Performance Metrics**

### **Response Quality**
- [ ] Physician satisfaction: ≥ 4/5
- [ ] RAG content coverage: ≥ 80%
- [ ] Retrieval precision (P@5): ≥ 0.7
- [ ] Medical advice faithfulness: ≥ 0.8

### **System Performance**  
- [ ] Total response latency: ≤ 30 seconds
- [ ] Condition extraction: ≤ 5 seconds
- [ ] Guideline retrieval: ≤ 2 seconds
- [ ] Medical advice generation: ≤ 25 seconds

### **User Experience**
- [ ] Non-medical query rejection: 100%
- [ ] System availability: ≥ 99%
- [ ] Error handling: Graceful degradation
- [ ] Interface responsiveness: Immediate feedback

## 🏗️ **Project Structure**
```
OnCall.ai/
├── src/                          # Core modules (✅ Complete)
│   ├── user_prompt.py           # Multi-level query processing
│   ├── retrieval.py             # Dual-index vector search
│   ├── generation.py            # RAG-based advice generation
│   ├── llm_clients.py           # Med42-70B integration
│   ├── medical_conditions.py    # Medical knowledge configuration
│   └── data_processing.py       # Dataset preprocessing
├── models/                       # Pre-processed data (✅ Complete)
│   ├── embeddings/              # Vector embeddings and chunks
│   └── indices/                 # ANNOY vector indices
├── tests/                        # Validation tests (✅ Complete)
│   ├── test_multilevel_fallback_validation.py
│   ├── test_end_to_end_pipeline.py
│   └── test_userinput_userprompt_medical_*.py
├── docs/                         # Documentation and planning
│   ├── next/                    # Current implementation docs
│   └── next_gradio_evaluation/  # Interface planning
├── app.py                        # 🎯 NEXT: Gradio interface
├── requirements.txt              # 🎯 NEXT: Deployment dependencies
└── README.md                     # This file
```

## 🧪 **Testing Validation**

### **Completed Tests**
- ✅ **Multi-level fallback validation**: 13 test cases, 69.2% success
- ✅ **End-to-end pipeline testing**: 6 scenarios, 100% technical completion
- ✅ **Component integration**: All modules working together
- ✅ **Error handling**: Graceful degradation and user-friendly messages

### **Key Findings**
- **Predefined mapping**: Instant response for known conditions
- **LLM extraction**: Reliable for complex symptom descriptions  
- **Non-medical rejection**: Perfect accuracy with updated prompt engineering
- **Retrieval quality**: High-relevance medical guidelines (0.2-0.4 relevance scores)
- **Generation capability**: Evidence-based advice with proper medical caution

## 🤝 **Contributing & Development**

### **Environment Setup**
```bash
# Clone repository
git clone [repository-url]
cd OnCall.ai

# Setup virtual environment
python -m venv genAIvenv
source genAIvenv/bin/activate  # On Windows: genAIvenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/test_end_to_end_pipeline.py

# Start Gradio interface (coming soon)
python app.py
```

### **API Configuration**
```bash
# Set up HuggingFace token for LLM access
export HF_TOKEN=your_huggingface_token

# Enable debug mode for development
export ONCALL_DEBUG=true
```

## ⚠️ **Important Notes**

### **Medical Disclaimer**
This system is designed for **research and educational purposes only**. It should not replace professional medical consultation, diagnosis, or treatment. Always consult qualified healthcare providers for medical decisions.

### **Current Limitations**
- **API Dependencies**: Requires HuggingFace API access for LLM functionality
- **Dataset Scope**: Currently focused on emergency and treatment guidelines
- **Language Support**: English medical terminology only
- **Validation Stage**: System under active development and testing

## 📞 **Contact & Support**

**Development Team**: OnCall.ai Team  
**Last Updated**: 2025-07-31  
**Version**: 0.9.0 (Pre-release)  
**Status**: 🚧 Ready for Interactive Testing Phase

---

*Built with ❤️ for healthcare professionals*
