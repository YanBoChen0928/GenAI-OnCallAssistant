#!/usr/bin/env python3
"""
Quick Script to Generate Hospital Customization Charts with Sample Data
This script generates all hospital customization charts with the unified style.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.modules.chart_generator import HospitalCustomizationChartGenerator
from evaluation.modules.metrics_calculator import HospitalCustomizationMetrics


def create_sample_data():
    """Create realistic sample data for hospital customization evaluation."""
    return [
        {
            "query_id": "broad_1",
            "query_text": "I have been feeling tired and weak lately",
            "query_type": "broad",
            "retrieval_mode": "Hospital Only",
            "execution_time": 28.543,
            "customization_time": 8.234,
            "hospital_guidelines": [
                {"document": "Fatigue Management Protocol.pdf", "score": 0.823},
                {"document": "General Weakness Evaluation.pdf", "score": 0.756},
                {"document": "Chronic Fatigue Guidelines.pdf", "score": 0.692}
            ],
            "coverage_keywords": ["fatigue", "weakness", "evaluation", "management"],
            "matched_keywords": ["fatigue", "weakness", "evaluation"]
        },
        {
            "query_id": "broad_2",
            "query_text": "My chest hurts and I'm having trouble breathing",
            "query_type": "broad",
            "retrieval_mode": "Hospital Only",
            "execution_time": 31.892,
            "customization_time": 9.567,
            "hospital_guidelines": [
                {"document": "Chest Pain Protocol.pdf", "score": 0.912},
                {"document": "Dyspnea Management.pdf", "score": 0.867},
                {"document": "Cardiac Emergency Guidelines.pdf", "score": 0.834}
            ],
            "coverage_keywords": ["chest", "pain", "dyspnea", "cardiac", "emergency"],
            "matched_keywords": ["chest", "pain", "dyspnea", "cardiac"]
        },
        {
            "query_id": "medium_1",
            "query_text": "60-year-old patient with hypertension presenting with dizziness",
            "query_type": "medium",
            "retrieval_mode": "Hospital Only", 
            "execution_time": 25.234,
            "customization_time": 7.891,
            "hospital_guidelines": [
                {"document": "Hypertension Management.pdf", "score": 0.789},
                {"document": "Dizziness Evaluation Protocol.pdf", "score": 0.812},
                {"document": "Geriatric Care Guidelines.pdf", "score": 0.723}
            ],
            "coverage_keywords": ["hypertension", "dizziness", "geriatric", "evaluation"],
            "matched_keywords": ["hypertension", "dizziness", "evaluation"]
        },
        {
            "query_id": "medium_2",
            "query_text": "Diabetic patient complaining of numbness in feet",
            "query_type": "medium",
            "retrieval_mode": "Hospital Only",
            "execution_time": 22.456,
            "customization_time": 6.234,
            "hospital_guidelines": [
                {"document": "Diabetic Neuropathy Protocol.pdf", "score": 0.945},
                {"document": "Peripheral Neuropathy Guidelines.pdf", "score": 0.892},
                {"document": "Diabetes Management.pdf", "score": 0.823}
            ],
            "coverage_keywords": ["diabetes", "neuropathy", "peripheral", "numbness", "management"],
            "matched_keywords": ["diabetes", "neuropathy", "numbness", "management"]
        },
        {
            "query_id": "specific_1",
            "query_text": "Suspected acute myocardial infarction with ST elevation",
            "query_type": "specific",
            "retrieval_mode": "Hospital Only",
            "execution_time": 18.923,
            "customization_time": 5.123,
            "hospital_guidelines": [
                {"document": "STEMI Protocol.pdf", "score": 0.978},
                {"document": "Cardiac Emergency Response.pdf", "score": 0.934},
                {"document": "MI Management Guidelines.pdf", "score": 0.912}
            ],
            "coverage_keywords": ["STEMI", "myocardial", "infarction", "cardiac", "emergency", "elevation"],
            "matched_keywords": ["STEMI", "myocardial", "infarction", "cardiac", "emergency"]
        },
        {
            "query_id": "specific_2",
            "query_text": "Management of anaphylactic shock in emergency department",
            "query_type": "specific",
            "retrieval_mode": "Hospital Only",
            "execution_time": 16.234,
            "customization_time": 4.567,
            "hospital_guidelines": [
                {"document": "Anaphylaxis Emergency Protocol.pdf", "score": 0.989},
                {"document": "Shock Management Guidelines.pdf", "score": 0.923},
                {"document": "Emergency Drug Administration.pdf", "score": 0.867}
            ],
            "coverage_keywords": ["anaphylaxis", "shock", "emergency", "epinephrine", "management"],
            "matched_keywords": ["anaphylaxis", "shock", "emergency", "management"]
        }
    ]


def main():
    """Generate all hospital customization charts with unified style."""
    print("🎨 Generating Hospital Customization Charts with Unified Style")
    print("=" * 60)
    
    # Create sample data
    sample_results = create_sample_data()
    print(f"✅ Created {len(sample_results)} sample query results")
    
    # Initialize components
    calculator = HospitalCustomizationMetrics()
    chart_gen = HospitalCustomizationChartGenerator("evaluation/results/charts")
    
    # Calculate metrics
    print("\n📊 Calculating comprehensive metrics...")
    metrics = calculator.calculate_comprehensive_metrics(sample_results)
    print("✅ Metrics calculated successfully")
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate all charts
    print("\n📈 Generating charts with unified style...")
    all_charts = []
    
    # 1. Latency charts
    print("  📊 Generating latency charts...")
    latency_charts = chart_gen.generate_latency_charts(metrics, timestamp)
    all_charts.extend(latency_charts)
    print(f"    ✅ Generated {len(latency_charts)} latency charts")
    
    # 2. Relevance charts
    print("  🎯 Generating relevance charts...")
    relevance_charts = chart_gen.generate_relevance_charts(metrics, timestamp)
    all_charts.extend(relevance_charts)
    print(f"    ✅ Generated {len(relevance_charts)} relevance charts")
    
    # 3. Coverage charts
    print("  📋 Generating coverage charts...")
    coverage_charts = chart_gen.generate_coverage_charts(metrics, timestamp)
    all_charts.extend(coverage_charts)
    print(f"    ✅ Generated {len(coverage_charts)} coverage charts")
    
    # 4. Comprehensive dashboard
    print("  🏆 Generating comprehensive dashboard...")
    dashboard_file = chart_gen.generate_comprehensive_dashboard(metrics, timestamp)
    all_charts.append(dashboard_file)
    print(f"    ✅ Generated dashboard: {Path(dashboard_file).name}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🎉 Successfully Generated {len(all_charts)} Charts!")
    print("\n📁 Charts saved to: evaluation/results/charts/")
    print("\n📊 Generated charts:")
    for chart in all_charts:
        print(f"  • {Path(chart).name}")
    
    # Save metrics for reference
    metrics_file = Path("evaluation/results/charts") / f"metrics_data_{timestamp}.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"\n💾 Metrics data saved to: {metrics_file.name}")


if __name__ == "__main__":
    main()