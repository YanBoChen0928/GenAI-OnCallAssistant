# Hospital Customization Evaluation System

This directory contains a comprehensive evaluation framework for analyzing the performance of hospital customization in the OnCall.ai RAG system. The system provides detailed metrics, visualizations, and insights specifically focused on hospital-only retrieval performance.

## Overview

The Hospital Customization Evaluation System evaluates three key performance metrics:

- **Metric 1 (Latency)**: Total execution time and hospital customization overhead
- **Metric 3 (Relevance)**: Average similarity scores from hospital content
- **Metric 4 (Coverage)**: Keyword overlap between generated advice and hospital content

## System Components

### Core Modules (`modules/`)

#### 1. `metrics_calculator.py`
The `HospitalCustomizationMetrics` class calculates comprehensive performance metrics:

- **Latency Analysis**: Execution time breakdown, customization overhead percentage
- **Relevance Analysis**: Hospital content similarity scores, relevance distribution
- **Coverage Analysis**: Keyword overlap, advice completeness, medical concept coverage

Key Features:
- Modular metric calculation for each performance dimension
- Statistical analysis (mean, median, std dev, min/max)
- Query type breakdown (broad/medium/specific)
- Comprehensive medical keyword dictionary for coverage analysis

#### 2. `chart_generator.py`
The `HospitalCustomizationChartGenerator` class creates publication-ready visualizations:

- **Latency Charts**: Bar charts by query type, customization breakdown pie charts
- **Relevance Charts**: Scatter plots, hospital vs general comparison charts
- **Coverage Charts**: Coverage percentage bars, keyword overlap heatmaps
- **Comprehensive Dashboard**: Multi-panel overview with key insights

Key Features:
- High-resolution PNG output with consistent styling
- Interactive color schemes and professional formatting
- Comprehensive dashboard combining all metrics
- Automatic chart organization and file management

#### 3. `query_executor.py`
Enhanced query execution with hospital-specific focus:

- **Hospital Only Mode**: Executes queries using only hospital customization
- **Detailed Logging**: Comprehensive execution metadata and timing
- **Error Handling**: Robust error management with detailed reporting
- **Batch Processing**: Efficient handling of multiple queries

### Evaluation Scripts

#### 1. `hospital_customization_evaluator.py`
Main evaluation orchestrator that:
- Coordinates all evaluation components
- Executes 6 test queries in Hospital Only mode
- Calculates comprehensive metrics
- Generates visualization charts
- Saves detailed results and reports

#### 2. `test_hospital_customization_pipeline.py`
Standalone testing script that:
- Tests core modules without full system dependencies
- Uses sample data to validate functionality
- Generates test charts and metrics
- Verifies pipeline integrity

#### 3. `run_hospital_evaluation.py`
Simple runner script for easy evaluation execution:
- User-friendly interface for running evaluations
- Clear error messages and troubleshooting tips
- Result summary and next steps guidance

## Usage Instructions

### Quick Start

1. **Basic Evaluation**:
   ```bash
   python evaluation/run_hospital_evaluation.py
   ```

2. **Component Testing**:
   ```bash
   python evaluation/test_hospital_customization_pipeline.py
   ```

### Advanced Usage

#### Direct Module Usage

```python
from evaluation.modules.metrics_calculator import HospitalCustomizationMetrics
from evaluation.modules.chart_generator import HospitalCustomizationChartGenerator

# Calculate metrics
calculator = HospitalCustomizationMetrics()
metrics = calculator.calculate_comprehensive_metrics(query_results)

# Generate charts
chart_gen = HospitalCustomizationChartGenerator("output/charts")
chart_files = chart_gen.generate_latency_charts(metrics)
```

#### Custom Query Execution

```python
from evaluation.modules.query_executor import QueryExecutor

executor = QueryExecutor()
queries = executor.load_queries("evaluation/queries/test_queries.json")
results = executor.execute_batch(queries, retrieval_mode="Hospital Only")
```

### Prerequisites

1. **System Requirements**:
   - Python 3.8+
   - OnCall.ai RAG system properly configured
   - Hospital customization pipeline functional

2. **Dependencies**:
   - matplotlib, seaborn (for chart generation)
   - numpy (for statistical calculations)
   - Standard Python libraries (json, pathlib, datetime, etc.)

3. **Environment Setup**:
   ```bash
   source rag_env/bin/activate  # Activate virtual environment
   pip install matplotlib seaborn numpy  # Install visualization dependencies
   ```

## Output Structure

### Results Directory (`results/`)

After running an evaluation, the following files are generated:

```
results/
├── hospital_customization_evaluation_YYYYMMDD_HHMMSS.json  # Complete results
├── hospital_customization_summary_YYYYMMDD_HHMMSS.txt      # Human-readable summary
└── charts/
    ├── latency_by_query_type_YYYYMMDD_HHMMSS.png
    ├── customization_breakdown_YYYYMMDD_HHMMSS.png
    ├── relevance_scatter_plot_YYYYMMDD_HHMMSS.png
    ├── hospital_vs_general_comparison_YYYYMMDD_HHMMSS.png
    ├── coverage_percentage_YYYYMMDD_HHMMSS.png
    └── hospital_customization_dashboard_YYYYMMDD_HHMMSS.png
```

### Results File Structure

The comprehensive results JSON contains:

```json
{
  "evaluation_metadata": {
    "timestamp": "2025-08-05T15:30:00.000000",
    "evaluation_type": "hospital_customization",
    "retrieval_mode": "Hospital Only",
    "total_queries": 6,
    "successful_queries": 6
  },
  "query_execution_results": {
    "raw_results": [...],
    "execution_summary": {...}
  },
  "hospital_customization_metrics": {
    "metric_1_latency": {...},
    "metric_3_relevance": {...},
    "metric_4_coverage": {...},
    "summary": {...}
  },
  "visualization_charts": {...},
  "evaluation_insights": [...],
  "recommendations": [...]
}
```

## Key Metrics Explained

### Metric 1: Latency Analysis
- **Total Execution Time**: Complete query processing duration
- **Customization Time**: Time spent on hospital-specific processing
- **Customization Percentage**: Hospital processing as % of total time
- **Query Type Breakdown**: Performance by query specificity

### Metric 3: Relevance Analysis
- **Hospital Content Relevance**: Average similarity scores for hospital guidelines
- **Relevance Distribution**: Low/Medium/High relevance score breakdown
- **Hospital vs General**: Comparison between content types
- **Quality Assessment**: Overall relevance quality rating

### Metric 4: Coverage Analysis
- **Keyword Overlap**: Percentage of medical keywords covered in advice
- **Advice Completeness**: Structural completeness assessment
- **Medical Concept Coverage**: Coverage of key medical concepts
- **Coverage Patterns**: Analysis of coverage effectiveness

## Performance Benchmarks

### Latency Performance Levels
- **Excellent**: < 30 seconds average execution time
- **Good**: 30-60 seconds average execution time
- **Needs Improvement**: > 60 seconds average execution time

### Relevance Quality Levels
- **High**: > 0.7 average relevance score
- **Medium**: 0.4-0.7 average relevance score
- **Low**: < 0.4 average relevance score

### Coverage Effectiveness Levels
- **Comprehensive**: > 70% keyword coverage
- **Adequate**: 40-70% keyword coverage
- **Limited**: < 40% keyword coverage

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure virtual environment is activated
   - Install missing dependencies
   - Check Python path configuration

2. **OnCall.ai System Not Available**:
   - Use `test_hospital_customization_pipeline.py` for testing
   - Verify system initialization
   - Check configuration files

3. **Chart Generation Failures**:
   - Install matplotlib and seaborn
   - Check output directory permissions
   - Verify data format integrity

4. **Missing Hospital Guidelines**:
   - Verify customization pipeline is configured
   - Check hospital document processing
   - Ensure ANNOY indices are built

### Error Messages

- `ModuleNotFoundError: No module named 'gradio'`: Use test script instead of full system
- `Interface not initialized`: OnCall.ai system needs proper setup
- `No data available`: Check query execution results format
- `Chart generation failed`: Install visualization dependencies

## Extending the System

### Adding New Metrics

1. **Extend Metrics Calculator**:
   ```python
   def calculate_custom_metric(self, query_results):
       # Your custom metric calculation
       return custom_metrics
   ```

2. **Add Visualization**:
   ```python
   def generate_custom_chart(self, metrics, timestamp):
       # Your custom chart generation
       return chart_file_path
   ```

3. **Update Evaluator**:
   - Include new metric in comprehensive calculation
   - Add chart generation to pipeline
   - Update result structure

### Custom Query Sets

1. Create new query JSON file following the existing format
2. Modify evaluator to use custom queries:
   ```python
   queries = evaluator.load_test_queries("path/to/custom_queries.json")
   ```

### Integration with Other Systems

The evaluation system is designed to be modular and can be integrated with:
- Continuous integration pipelines
- Performance monitoring systems
- A/B testing frameworks
- Quality assurance workflows

## Best Practices

1. **Regular Evaluation**: Run evaluations after system changes
2. **Baseline Comparison**: Track performance changes over time
3. **Query Diversity**: Use diverse query sets for comprehensive testing
4. **Result Analysis**: Review both metrics and visualizations
5. **Action on Insights**: Use recommendations for system improvements

## Support and Maintenance

For issues, improvements, or questions:
1. Check the troubleshooting section above
2. Review error messages and logs
3. Test with the standalone pipeline tester
4. Consult the OnCall.ai system documentation

The evaluation system is designed to be self-contained and robust, providing comprehensive insights into hospital customization performance with minimal setup requirements.