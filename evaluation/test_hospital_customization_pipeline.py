#!/usr/bin/env python3
"""
Test Script for Hospital Customization Evaluation Pipeline

This script tests the hospital customization evaluation components independently
to ensure they work correctly before running the full evaluation with the OnCall.ai system.

Author: OnCall.ai Evaluation Team
Date: 2025-08-05
Version: 1.0.0
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add module paths
sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / 'evaluation' / 'modules'))

# Import our modules directly to avoid dependency issues
from metrics_calculator import HospitalCustomizationMetrics
from chart_generator import HospitalCustomizationChartGenerator


def create_sample_query_results():
    """Create sample query results for testing."""
    return [
        {
            "query_id": "broad_1",
            "query_text": "I have been feeling tired and weak lately",
            "query_metadata": {
                "specificity": "broad",
                "category": "general"
            },
            "success": True,
            "timestamp": "2025-08-05T15:30:00.000000",
            "execution_time": {
                "total_seconds": 42.5,
                "start_time": "2025-08-05T15:30:00.000000",
                "end_time": "2025-08-05T15:30:42.500000"
            },
            "retrieval_mode": "Hospital Only",
            "response": {
                "medical_advice": "Based on the symptoms of fatigue and weakness, we recommend a comprehensive evaluation including blood work to check for anemia, thyroid dysfunction, and electrolyte imbalances. Treatment should focus on addressing underlying causes and supportive care including adequate hydration and rest.",
                "processing_steps": "🎯 Step 1: Processing medical query and extracting conditions...\n   ✅ Condition: fatigue and weakness\n   ⏱️ Processing Time: 25.2s\n\n🏥 Step 1.5: Checking hospital-specific guidelines...\n   📋 Found 12 hospital-specific guidelines\n   ⏱️ Customization time: 8.3s\n\n🔍 Step 3: Retrieving relevant medical guidelines...\n   📊 Found 6 relevant guidelines\n   ⏱️ Retrieval time: 1.2s\n\n🧠 Step 4: Generating evidence-based medical advice...\n   ⏱️ Generation time: 7.8s",
                "guidelines_display": "1. Hospital Guideline (Relevance: 85%)\n2. Hospital Guideline (Relevance: 78%)\n3. Hospital Guideline (Relevance: 72%)\n4. Emergency Guideline (Relevance: 65%)\n5. Treatment Guideline (Relevance: 58%)\n6. Hospital Guideline (Relevance: 52%)"
            },
            "pipeline_analysis": {
                "levels_executed": {
                    "levels_detected": ["condition_extraction", "hospital_customization", "guideline_retrieval", "advice_generation"],
                    "total_steps": 12
                },
                "retrieval_info": {
                    "guidelines_found": 6,
                    "hospital_guidelines": 4,
                    "emergency_guidelines": 1,
                    "treatment_guidelines": 1,
                    "confidence_scores": [0.85, 0.78, 0.72, 0.65, 0.58, 0.52]
                }
            }
        },
        {
            "query_id": "medium_1",
            "query_text": "67-year-old male with sudden onset severe headache and neck stiffness for 2 hours",
            "query_metadata": {
                "specificity": "medium",
                "category": "neurological"
            },
            "success": True,
            "timestamp": "2025-08-05T15:31:00.000000",
            "execution_time": {
                "total_seconds": 38.7,
                "start_time": "2025-08-05T15:31:00.000000",
                "end_time": "2025-08-05T15:31:38.700000"
            },
            "retrieval_mode": "Hospital Only",
            "response": {
                "medical_advice": "This presentation is highly concerning for subarachnoid hemorrhage. Immediate CT scan should be performed, followed by lumbar puncture if CT is negative. Blood pressure monitoring and neurological assessment are critical. Consider emergency neurosurgical consultation based on hospital protocols.",
                "processing_steps": "🎯 Step 1: Processing medical query and extracting conditions...\n   ✅ Condition: severe headache with neck stiffness\n   ⏱️ Processing Time: 22.1s\n\n🏥 Step 1.5: Checking hospital-specific guidelines...\n   📋 Found 8 hospital-specific guidelines\n   ⏱️ Customization time: 7.2s\n\n🔍 Step 3: Retrieving relevant medical guidelines...\n   📊 Found 5 relevant guidelines\n   ⏱️ Retrieval time: 0.8s\n\n🧠 Step 4: Generating evidence-based medical advice...\n   ⏱️ Generation time: 8.6s",
                "guidelines_display": "1. Hospital Guideline (Relevance: 92%)\n2. Hospital Guideline (Relevance: 88%)\n3. Emergency Guideline (Relevance: 83%)\n4. Hospital Guideline (Relevance: 79%)\n5. Treatment Guideline (Relevance: 74%)"
            },
            "pipeline_analysis": {
                "levels_executed": {
                    "levels_detected": ["condition_extraction", "hospital_customization", "guideline_retrieval", "advice_generation"],
                    "total_steps": 10
                },
                "retrieval_info": {
                    "guidelines_found": 5,
                    "hospital_guidelines": 3,
                    "emergency_guidelines": 1,
                    "treatment_guidelines": 1,
                    "confidence_scores": [0.92, 0.88, 0.83, 0.79, 0.74]
                }
            }
        },
        {
            "query_id": "specific_1",
            "query_text": "45-year-old diabetic patient presents with polyuria, polydipsia, fruity breath odor, blood glucose 450 mg/dL, and ketones in urine",
            "query_metadata": {
                "specificity": "specific",
                "category": "endocrine"
            },
            "success": True,
            "timestamp": "2025-08-05T15:32:00.000000",
            "execution_time": {
                "total_seconds": 55.3,
                "start_time": "2025-08-05T15:32:00.000000",
                "end_time": "2025-08-05T15:32:55.300000"
            },
            "retrieval_mode": "Hospital Only",
            "response": {
                "medical_advice": "This patient presents with diabetic ketoacidosis (DKA). Immediate treatment should include IV fluid resuscitation, insulin therapy, and electrolyte monitoring according to hospital DKA protocol. Monitor blood glucose, ketones, and arterial blood gases closely. Identify and treat precipitating factors.",
                "processing_steps": "🎯 Step 1: Processing medical query and extracting conditions...\n   ✅ Condition: diabetic ketoacidosis\n   ⏱️ Processing Time: 28.8s\n\n🏥 Step 1.5: Checking hospital-specific guidelines...\n   📋 Found 15 hospital-specific guidelines\n   ⏱️ Customization time: 12.1s\n\n🔍 Step 3: Retrieving relevant medical guidelines...\n   📊 Found 8 relevant guidelines\n   ⏱️ Retrieval time: 1.5s\n\n🧠 Step 4: Generating evidence-based medical advice...\n   ⏱️ Generation time: 12.9s",
                "guidelines_display": "1. Hospital Guideline (Relevance: 96%)\n2. Hospital Guideline (Relevance: 93%)\n3. Hospital Guideline (Relevance: 90%)\n4. Emergency Guideline (Relevance: 87%)\n5. Hospital Guideline (Relevance: 84%)\n6. Treatment Guideline (Relevance: 81%)\n7. Hospital Guideline (Relevance: 78%)\n8. Hospital Guideline (Relevance: 73%)"
            },
            "pipeline_analysis": {
                "levels_executed": {
                    "levels_detected": ["condition_extraction", "hospital_customization", "guideline_retrieval", "advice_generation"],
                    "total_steps": 14
                },
                "retrieval_info": {
                    "guidelines_found": 8,
                    "hospital_guidelines": 6,
                    "emergency_guidelines": 1,
                    "treatment_guidelines": 1,
                    "confidence_scores": [0.96, 0.93, 0.90, 0.87, 0.84, 0.81, 0.78, 0.73]
                }
            }
        }
    ]


def test_metrics_calculator():
    """Test the metrics calculator with sample data."""
    print("📊 Testing Hospital Customization Metrics Calculator...")
    
    try:
        # Initialize calculator
        calculator = HospitalCustomizationMetrics()
        print("  ✅ Metrics calculator initialized")
        
        # Create sample data
        sample_results = create_sample_query_results()
        print(f"  📋 Created {len(sample_results)} sample query results")
        
        # Test latency metrics
        print("  ⏱️  Testing latency metrics calculation...")
        latency_metrics = calculator.calculate_latency_metrics(sample_results)
        assert "metric_1_latency" in latency_metrics
        print("    ✅ Latency metrics calculated successfully")
        
        # Test relevance metrics
        print("  🎯 Testing relevance metrics calculation...")
        relevance_metrics = calculator.calculate_relevance_metrics(sample_results)
        assert "metric_3_relevance" in relevance_metrics
        print("    ✅ Relevance metrics calculated successfully")
        
        # Test coverage metrics
        print("  📋 Testing coverage metrics calculation...")
        coverage_metrics = calculator.calculate_coverage_metrics(sample_results)
        assert "metric_4_coverage" in coverage_metrics
        print("    ✅ Coverage metrics calculated successfully")
        
        # Test comprehensive metrics
        print("  🏆 Testing comprehensive metrics calculation...")
        comprehensive_metrics = calculator.calculate_comprehensive_metrics(sample_results)
        assert "evaluation_metadata" in comprehensive_metrics
        assert "metrics" in comprehensive_metrics
        assert "summary" in comprehensive_metrics
        print("    ✅ Comprehensive metrics calculated successfully")
        
        # Display key results
        summary = comprehensive_metrics["summary"]
        print(f"\n  📈 Test Results Summary:")
        print(f"    • Latency Performance: {summary.get('latency_performance', 'Unknown')}")
        print(f"    • Relevance Quality: {summary.get('relevance_quality', 'Unknown')}")
        print(f"    • Coverage Effectiveness: {summary.get('coverage_effectiveness', 'Unknown')}")
        print(f"    • Overall Assessment: {summary.get('overall_assessment', 'Unknown')}")
        
        return comprehensive_metrics
        
    except Exception as e:
        print(f"    ❌ Metrics calculator test failed: {e}")
        raise


def test_chart_generator(metrics):
    """Test the chart generator with calculated metrics."""
    print("\n📈 Testing Hospital Customization Chart Generator...")
    
    try:
        # Initialize chart generator
        test_charts_dir = "evaluation/results/test_charts"
        chart_generator = HospitalCustomizationChartGenerator(test_charts_dir)
        print("  ✅ Chart generator initialized")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Test latency charts
        print("  📊 Testing latency chart generation...")
        latency_files = chart_generator.generate_latency_charts(metrics, timestamp)
        print(f"    ✅ Generated {len(latency_files)} latency charts")
        
        # Test relevance charts
        print("  🎯 Testing relevance chart generation...")
        relevance_files = chart_generator.generate_relevance_charts(metrics, timestamp)
        print(f"    ✅ Generated {len(relevance_files)} relevance charts")
        
        # Test coverage charts
        print("  📋 Testing coverage chart generation...")
        coverage_files = chart_generator.generate_coverage_charts(metrics, timestamp)
        print(f"    ✅ Generated {len(coverage_files)} coverage charts")
        
        # Test comprehensive dashboard
        print("  🏆 Testing comprehensive dashboard generation...")
        dashboard_file = chart_generator.generate_comprehensive_dashboard(metrics, timestamp)
        print(f"    ✅ Generated dashboard: {Path(dashboard_file).name}")
        
        total_charts = len(latency_files) + len(relevance_files) + len(coverage_files) + 1
        print(f"  📁 Total charts generated: {total_charts}")
        print(f"  💾 Charts saved to: {chart_generator.output_dir}")
        
        return {
            "latency_charts": latency_files,
            "relevance_charts": relevance_files,
            "coverage_charts": coverage_files,
            "dashboard": dashboard_file
        }
        
    except Exception as e:
        print(f"    ❌ Chart generator test failed: {e}")
        raise


def test_complete_pipeline():
    """Test the complete evaluation pipeline with sample data."""
    print("🚀 Testing Complete Hospital Customization Evaluation Pipeline")
    print("=" * 60)
    
    try:
        # Test metrics calculator
        metrics = test_metrics_calculator()
        
        # Test chart generator
        chart_files = test_chart_generator(metrics)
        
        # Save test results
        print("\n💾 Saving test results...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        test_results = {
            "test_metadata": {
                "timestamp": datetime.now().isoformat(),
                "test_type": "pipeline_validation",
                "version": "1.0.0"
            },
            "metrics_test": {
                "success": True,
                "metrics": metrics
            },
            "chart_generation_test": {
                "success": True,
                "chart_files": chart_files
            }
        }
        
        results_file = Path("evaluation/results") / f"pipeline_test_results_{timestamp}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Test results saved to: {results_file}")
        
        print("\n" + "=" * 60)
        print("🎉 Complete Pipeline Test Successful!")
        print("=" * 60)
        
        print(f"\n📊 Test Summary:")
        print(f"  ✅ Metrics Calculator: Working")
        print(f"  ✅ Chart Generator: Working")
        print(f"  ✅ Sample Data Processing: Working")
        print(f"  📁 Test Results: {results_file.name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


def main():
    """Main function for running pipeline tests."""
    print("🧪 Hospital Customization Evaluation Pipeline Test")
    print("Testing Core Components Before Full System Integration")
    print("=" * 60)
    
    try:
        success = test_complete_pipeline()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected test error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)