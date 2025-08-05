# Metric 5-6 LLM Judge Evaluator Manual

## Overview

The `metric5_6_llm_judge_evaluator.py` is a multi-system evaluation tool that uses Llama3-70B as a third-party judge to assess medical advice quality across different AI systems. It supports both single-system evaluation and multi-system comparison with a single LLM call for maximum consistency.

## Metrics Evaluated

**Metric 5: Clinical Actionability (臨床可操作性)**
- Scale: 1-10 (normalized to 0.0-1.0)
- Question: "Can healthcare providers immediately act on this advice?"
- Target: ≥7.0/10 for acceptable actionability

**Metric 6: Clinical Evidence Quality (臨床證據品質)**  
- Scale: 1-10 (normalized to 0.0-1.0)
- Question: "Is the advice evidence-based and follows medical standards?"
- Target: ≥7.5/10 for acceptable evidence quality

## System Architecture

### Multi-System Support
The evaluator supports flexible system combinations:
- **Single System**: `rag` or `direct`
- **Two-System Comparison**: `rag,direct` 
- **Future Extension**: `rag,direct,claude,gpt4` (any combination)

### Judge LLM
- **Model**: Llama3-70B-Instruct via Hugging Face API
- **Strategy**: Single batch call for all evaluations
- **Temperature**: 0.1 (low for consistent evaluation)
- **Max Tokens**: 2048 (sufficient for evaluation responses)

## Prerequisites

### 1. Environment Setup
```bash
# Ensure HF_TOKEN is set in your environment
export HF_TOKEN="your_huggingface_token"

# Or add to .env file
echo "HF_TOKEN=your_huggingface_token" >> .env
```

### 2. Required Data Files
Before running the judge evaluator, you must have medical outputs from your systems:

**For RAG System**:
```bash
python latency_evaluator.py single_test_query.txt
# Generates: results/medical_outputs_YYYYMMDD_HHMMSS.json
```

**For Direct LLM System**:
```bash
python direct_llm_evaluator.py single_test_query.txt  
# Generates: results/medical_outputs_direct_YYYYMMDD_HHMMSS.json
```

## Usage

### Command Line Interface

#### Single System Evaluation
```bash
# Evaluate RAG system only
python metric5_6_llm_judge_evaluator.py rag

# Evaluate Direct LLM system only  
python metric5_6_llm_judge_evaluator.py direct
```

#### Multi-System Comparison (Recommended)
```bash
# Compare RAG vs Direct systems
python metric5_6_llm_judge_evaluator.py rag,direct

# Future: Compare multiple systems
python metric5_6_llm_judge_evaluator.py rag,direct,claude
```

### Complete Workflow Example

```bash
# Step 1: Navigate to evaluation directory
cd /path/to/GenAI-OnCallAssistant/evaluation

# Step 2: Generate medical outputs from both systems
python latency_evaluator.py single_test_query.txt
python direct_llm_evaluator.py single_test_query.txt

# Step 3: Run comparative evaluation
python metric5_6_llm_judge_evaluator.py rag,direct
```

## Output Files

### Generated Files
- **Statistics**: `results/judge_evaluation_comparison_rag_vs_direct_YYYYMMDD_HHMMSS.json`
- **Detailed Results**: Stored in evaluator's internal results array

### File Structure
```json
{
  "comparison_metadata": {
    "systems_compared": ["rag", "direct"],
    "comparison_type": "multi_system",
    "timestamp": "2025-08-04T22:00:00"
  },
  "category_results": {
    "diagnosis": {
      "average_actionability": 0.850,
      "average_evidence": 0.780,
      "query_count": 1,
      "actionability_target_met": true,
      "evidence_target_met": true
    }
  },
  "overall_results": {
    "average_actionability": 0.850,
    "average_evidence": 0.780,
    "successful_evaluations": 2,
    "total_queries": 2,
    "actionability_target_met": true,
    "evidence_target_met": true
  }
}
```

## Evaluation Process

### 1. File Discovery
The evaluator automatically finds the latest medical output files:
- **RAG**: `medical_outputs_*.json`
- **Direct**: `medical_outputs_direct_*.json`
- **Custom**: `medical_outputs_{system}_*.json`

### 2. Prompt Generation
For multi-system comparison, the evaluator creates a structured prompt:
```
You are a medical expert evaluating and comparing AI systems...

SYSTEM 1 (RAG): Uses medical guidelines + LLM for evidence-based advice
SYSTEM 2 (Direct): Uses LLM only without external guidelines

QUERY 1 (DIAGNOSIS):
Patient Query: 60-year-old patient with hypertension history...

SYSTEM 1 Response: For a 60-year-old patient with...
SYSTEM 2 Response: Based on the symptoms described...

RESPONSE FORMAT:
Query 1 System 1: Actionability=X, Evidence=Y
Query 1 System 2: Actionability=X, Evidence=Y
```

### 3. LLM Judge Evaluation
- **Single API Call**: All systems evaluated in one request for consistency
- **Response Parsing**: Automatic extraction of numerical scores
- **Error Handling**: Graceful handling of parsing failures

### 4. Results Analysis
- **System-Specific Statistics**: Individual performance metrics
- **Comparative Analysis**: Direct system-to-system comparison
- **Target Compliance**: Automatic threshold checking

## Expected Output

### Console Output Example
```
🧠 OnCall.ai LLM Judge Evaluator - Metrics 5-6 Multi-System Evaluation

🧪 Multi-System Comparison: RAG vs DIRECT
📊 Found rag outputs: results/medical_outputs_20250804_215917.json
📊 Found direct outputs: results/medical_outputs_direct_20250804_220000.json
📊 Comparing 2 systems with 1 queries each
🎯 Metrics: 5 (Actionability) + 6 (Evidence Quality)
⚡ Strategy: Single comparison call for maximum consistency

🧠 Multi-system comparison: rag, direct
📊 Evaluating 1 queries across 2 systems...
📝 Comparison prompt created (2150 characters)
🔄 Calling judge LLM for multi-system comparison...
✅ Judge LLM completed comparison evaluation in 45.3s
📄 Response length: 145 characters
📊 RAG: 1 evaluations parsed
📊 DIRECT: 1 evaluations parsed

📊 === LLM JUDGE EVALUATION SUMMARY ===
Systems Compared: RAG vs DIRECT
Overall Performance:
   Average Actionability: 0.850 (8.5/10)
   Average Evidence Quality: 0.780 (7.8/10)
   Actionability Target (≥7.0): ✅ Met
   Evidence Target (≥7.5): ✅ Met

System Breakdown:
   RAG: Actionability=0.900, Evidence=0.850 [1 queries]
   DIRECT: Actionability=0.800, Evidence=0.710 [1 queries]

✅ LLM judge evaluation complete!
📊 Statistics: results/judge_evaluation_comparison_rag_vs_direct_20250804_220000.json
⚡ Efficiency: 2 evaluations in 1 LLM call
```

## Key Features

### 1. Scientific Comparison Design
- **Single Judge Call**: All systems evaluated simultaneously for consistency
- **Eliminates Temporal Bias**: Same judge, same context, same standards
- **Direct System Comparison**: Side-by-side evaluation format

### 2. Flexible Architecture  
- **Backward Compatible**: Single system evaluation still supported
- **Future Extensible**: Easy to add new systems (`claude`, `gpt4`, etc.)
- **Modular Design**: Clean separation of concerns

### 3. Robust Error Handling
- **File Validation**: Automatic detection of missing input files
- **Query Count Verification**: Warns if systems have different query counts
- **Graceful Degradation**: Continues operation despite partial failures

### 4. Comprehensive Reporting
- **System-Specific Metrics**: Individual performance analysis
- **Comparative Statistics**: Direct system-to-system comparison
- **Target Compliance**: Automatic benchmark checking
- **Detailed Metadata**: Full traceability of evaluation parameters

## Troubleshooting

### Common Issues

#### 1. Missing Input Files
```
❌ No medical outputs files found for rag system
💡 Please run evaluators first:
   python latency_evaluator.py single_test_query.txt
```
**Solution**: Run the prerequisite evaluators to generate medical outputs.

#### 2. HF_TOKEN Not Set
```
❌ HF_TOKEN is missing from environment variables
```
**Solution**: Set your Hugging Face token in environment or `.env` file.

#### 3. Query Count Mismatch
```
⚠️ Warning: Systems have different query counts: {'rag': 3, 'direct': 1}
```
**Solution**: Ensure both systems processed the same input file.

#### 4. LLM API Timeout
```
❌ Multi-system evaluation failed: timeout
```
**Solution**: Check internet connection and Hugging Face API status.

### Debug Tips

1. **Check File Existence**: Verify medical output files in `results/` directory
2. **Validate JSON Format**: Ensure input files are properly formatted
3. **Monitor API Usage**: Check Hugging Face account limits
4. **Review Logs**: Examine detailed logging output for specific errors

## Future Extensions

### Phase 2: Generic Multi-System Framework
```bash
# Configuration-driven system comparison
python metric5_6_llm_judge_evaluator.py --config comparison_config.json
```

### Phase 3: Unlimited System Support
```bash
# Dynamic system registration
python metric5_6_llm_judge_evaluator.py med42,claude,gpt4,palm,llama2
```

### Integration with Chart Generators
```bash
# Generate comparison visualizations
python metric5_6_llm_judge_chart_generator.py rag,direct
```

## Best Practices

1. **Consistent Test Data**: Use the same query file for all systems
2. **Sequential Execution**: Complete data collection before evaluation
3. **Batch Processing**: Use multi-system mode for scientific comparison
4. **Result Verification**: Review detailed statistics files for accuracy
5. **Performance Monitoring**: Track evaluation latency and API costs

## Scientific Validity

The multi-system comparison approach provides superior scientific validity compared to separate evaluations:

- **Eliminates Judge Variability**: Same judge evaluates all systems
- **Reduces Temporal Effects**: All evaluations in single time window  
- **Ensures Consistent Standards**: Identical evaluation criteria applied
- **Enables Direct Comparison**: Side-by-side system assessment
- **Maximizes Efficiency**: Single API call vs multiple separate calls

This design makes the evaluation results more reliable for research publications and system optimization decisions.
