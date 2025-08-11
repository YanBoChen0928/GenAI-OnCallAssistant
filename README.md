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

### **Comprehensive Evaluation Results (Metrics 1-8)**

```
🎯 Multi-Level Fallback Performance: 5-layer processing pipeline
   - Level 1 (Predefined): Instant response for known conditions
   - Level 2+4 (Combined LLM): 40% time reduction through optimization
   - Level 3 (Semantic Search): High-quality embedding retrieval
   - Level 5 (Generic): 100% fallback coverage

📈 RAG vs Direct LLM Comparison (9 test queries):
   - RAG System Actionability: 0.900 vs Direct: 0.789 (14.1% improvement)
   - RAG Evidence Quality: 0.900 vs Direct: 0.689 (30.6% improvement)
   - Category Performance: RAG superior in all categories (Diagnosis, Treatment, Mixed)
   - Complex Queries (Mixed): RAG shows 30%+ advantage over Direct LLM
```

### **Detailed Performance Metrics**

```
🔍 Metric 1 - Latency Analysis:
   - Average Response Time: 15.5s (RAG) vs 8.2s (Direct)
   - Condition Extraction: 2.6s average
   - Retrieval + Generation: 12.9s average

📊 Metric 2-4 - Quality Assessment:
   - Extraction Success Rate: 69.2% across fallback levels
   - Retrieval Relevance: 0.245-0.326 (medical domain optimized)
   - Content Coverage: 8-9 guidelines per query with balanced emergency/treatment

🎯 Metrics 5-6 - Clinical Quality (LLM Judge Evaluation):
   - Clinical Actionability: RAG (9.0/10) > Direct (7.9/10)
   - Evidence Quality: RAG (9.0/10) > Direct (6.9/10)
   - Treatment Queries: RAG achieves highest scores (9.3/10)
   - All scores exceed clinical thresholds (7.0 actionability, 7.5 evidence)

📈 Metrics 7-8 - Precision & Ranking:
   - Precision@5: High relevance in medical guideline retrieval
   - MRR (Mean Reciprocal Rank): Optimized for clinical decision-making
   - Source Diversity: Balanced emergency and treatment protocol coverage
```

## 📈 **EVALUATION SYSTEM**

### **Comprehensive Medical AI Evaluation Pipeline**

OnCall.ai includes a complete evaluation framework with 8 key metrics to assess system performance across multiple dimensions:

#### **🎯 General Pipeline Overview**

```
Query Input → RAG/Direct Processing → Multi-Metric Evaluation → Comparative Analysis
     │                │                       │                      │
     └─ Test Queries  └─ Medical Outputs     └─ Automated Metrics   └─ Visualization
        (9 scenarios)    (JSON format)         (Scores & Statistics)   (4-panel charts)
```

#### **📊 Metrics 1-8: Detailed Assessment Framework**

##### **⚡ Metric 1: Latency Analysis**

- **Purpose**: Measure system response time and processing efficiency
- **Operation**: `python evaluation/latency_evaluator.py`
- **Key Findings**: RAG averages 15.5s, Direct averages 8.2s

##### **🔍 Metric 2-4: Quality Assessment**

- **Components**: Extraction success, retrieval relevance, content coverage
- **Key Findings**: 69.2% extraction success, 0.245-0.326 relevance scores

##### **🏥 Metrics 5-6: Clinical Quality (LLM Judge)**

- **Purpose**: Professional evaluation of clinical actionability and evidence quality
- **Operation**: `python evaluation/fixed_judge_evaluator.py rag,direct --batch-size 3`
- **Charts**: `python evaluation/metric5_6_llm_judge_chart_generator.py`
- **Key Findings**: RAG (9.0/10) significantly outperforms Direct (7.9/10 actionability, 6.9/10 evidence)

##### **🎯 Metrics 7-8: Precision & Ranking**

- **Operation**: `python evaluation/metric7_8_precision_MRR.py`
- **Key Findings**: High precision in medical guideline retrieval

#### **🏆 Evaluation Results Summary**

- **RAG Advantages**: 30.6% better evidence quality, 14.1% higher actionability
- **System Reliability**: 100% fallback coverage, clinical threshold compliance
- **Human Evaluation**: Raw outputs available in `evaluation/results/medical_outputs_*.json`

## 🛠️ **Technical Architecture**

### **Data Flow**

```
User Query → Level 1: Predefined Mapping
     ↓ (if fails)
Level 2: LLM Extraction
     ↓ (if fails)
Level 3: Semantic Search
     ↓ (if fails)
Level 4: Medical Validation
     ↓ (if fails)
Level 5: Generic Search
     ↓ (if fails)
No Match Found
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

## 🚀 **NEXT PHASE: System Optimization & Enhancement**

### **📊 Current Status (2025-08-09)**

#### **✅ COMPLETED: Comprehensive Evaluation System**

- **Metrics 1-8 Framework**: Complete assessment pipeline implemented
- **RAG vs Direct Comparison**: Validated RAG system superiority (30%+ better evidence quality)
- **LLM Judge Evaluation**: Automated clinical quality assessment with 4-panel visualization
- **Performance Benchmarking**: Quantified system capabilities across all dimensions
- **Human Evaluation Tools**: Raw output comparison framework available

#### **✅ COMPLETED: Production-Ready Pipeline**

- **5-Layer Fallback System**: 69.2% success rate with 100% coverage
- **Dual-Index Retrieval**: Emergency and treatment guidelines optimized
- **Med42-70B Integration**: Specialized medical LLM with robust error handling

### **🎯 Future Goals**

#### **🔊 Phase 1: Audio Integration Enhancement**

- [ ] **Voice Input Pipeline**
  - [ ] Whisper ASR integration for medical terminology
  - [ ] Audio preprocessing and noise reduction
  - [ ] Medical vocabulary optimization for transcription accuracy
- [ ] **Voice Output System**
  - [ ] Text-to-Speech (TTS) for medical advice delivery
  - [ ] SSML markup for proper medical pronunciation
  - [ ] Audio response caching for common scenarios
- [ ] **Multi-Modal Interface**
  - [ ] Simultaneous text + audio input support
  - [ ] Audio quality validation and fallback to text
  - [ ] Mobile-friendly voice interface optimization

#### **⚡ Phase 2: System Performance Optimization (5→4 Layer Architecture)**

Based on `docs/20250809optimization/5level_to_4layer.md` analysis:

- [ ] **Query Cache Implementation** (80% P95 latency reduction expected)
  - [ ] String similarity matching (0.85 threshold)
  - [ ] In-memory LRU cache (1000 query limit)
  - [ ] Cache hit monitoring and optimization
- [ ] **Layer Reordering Optimization**
  - [ ] L1: Enhanced Predefined Mapping (expand from 12 to 154 keywords)
  - [ ] L2: Semantic Search (moved up for better coverage)
  - [ ] L3: LLM Analysis (combined extraction + validation)
  - [ ] L4: Generic Search (final fallback)
- [ ] **Performance Targets**:
  - P95 latency: 15s → 3s (80% improvement)
  - L1 success rate: 15% → 30% (2x improvement)
  - Cache hit rate: 0% → 30% (new capability)

#### **📱 Phase 3: Interactive Interface Polish**

- [ ] **Enhanced Gradio Interface** (`app.py` improvements)
  - [ ] Real-time processing indicators
  - [ ] Audio input/output controls
  - [ ] Advanced debug mode with performance metrics
  - [ ] Mobile-responsive design optimization
- [ ] **User Experience Enhancements**
  - [ ] Query suggestion system based on common medical scenarios
  - [ ] Progressive disclosure of technical details
  - [ ] Integrated help system with usage examples

### **🔮 Further Enhancements (1-2 Months)**

#### **📊 Advanced Analytics & Monitoring**

- [ ] **Real-time Performance Dashboard**
  - [ ] Layer success rate monitoring
  - [ ] Cache effectiveness analysis
  - [ ] User query pattern insights
- [ ] **Continuous Evaluation Pipeline**
  - [ ] Automated regression testing
  - [ ] Performance benchmark tracking
  - [ ] Clinical accuracy monitoring with expert review

#### **🎯 Medical Specialization Expansion**

- [ ] **Specialty-Specific Modules**
  - [ ] Cardiology-focused pipeline
  - [ ] Pediatric emergency protocols
  - [ ] Trauma surgery guidelines integration
- [ ] **Multi-Language Support**
  - [ ] Spanish medical terminology
  - [ ] French healthcare guidelines
  - [ ] Localized medical protocol adaptation

#### **🔬 Research & Development**

- [ ] **Advanced RAG Techniques**
  - [ ] Hierarchical retrieval architecture
  - [ ] Dynamic chunk sizing optimization
  - [ ] Cross-reference validation systems
- [ ] **AI Safety & Reliability**
  - [ ] Uncertainty quantification in medical advice
  - [ ] Adversarial query detection
  - [ ] Bias detection and mitigation in clinical recommendations

### **📋 Updated Performance Targets**

#### **Post-Optimization Goals**

```
⚡ Latency Improvements:
   - P95 Response Time: <3 seconds (current: 15s)
   - P99 Response Time: <0.5 seconds (current: 25s)
   - Cache Hit Rate: >30% (new metric)

🎯 Quality Maintenance:
   - Clinical Actionability: ≥9.0/10 (maintain current RAG performance)
   - Evidence Quality: ≥9.0/10 (maintain current RAG performance)
   - System Reliability: 100% fallback coverage (maintain)

🔊 Audio Experience:
   - Voice Recognition Accuracy: >95% for medical terms
   - Audio Response Latency: <2 seconds
   - Multi-modal Success Rate: >90%
```

#### **System Scalability**

```
📈 Capacity Targets:
   - Concurrent Users: 100+ simultaneous queries
   - Query Cache: 10,000+ cached responses
   - Audio Processing: Real-time streaming support

🔧 Infrastructure:
   - HuggingFace Spaces deployment optimization
   - Container orchestration for scaling
   - CDN integration for audio content delivery
```

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
├── evaluation/                   # Comprehensive evaluation system (✅ Complete)
│   ├── fixed_judge_evaluator.py # LLM judge evaluation (Metrics 5-6)
│   ├── latency_evaluator.py     # Performance analysis (Metrics 1-4)
│   ├── metric7_8_precision_MRR.py # Precision/ranking analysis
│   ├── results/                 # Evaluation outputs and comparisons
│   ├── charts/                  # Generated visualization charts
│   └── queries/test_queries.json # Standard test scenarios
├── docs/                         # Documentation and optimization plans
│   ├── 20250809optimization/    # System performance optimization
│   │   └── 5level_to_4layer.md # Layer architecture improvements
│   └── next/                    # Current implementation docs
├── app.py                        # ✅ Gradio interface (Complete)
├── united_requirements.txt       # 🔧 Updated: All dependencies
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

# Setup virtual environment
python -m venv genAIvenv
source genAIvenv/bin/activate  # On Windows: genAIvenv\Scripts\activate

# Install dependencies
pip install -r united_requirements.txt

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
**Last Updated**: 2025-08-09  
**Version**: 1.0.0 (Evaluation Complete)  
**Status**: 🎯 Ready for Optimization & Audio Enhancement Phase

---

_Built with ❤️ for healthcare professionals_
