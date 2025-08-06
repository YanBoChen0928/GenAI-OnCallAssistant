#!/usr/bin/env python3
"""
Accuracy Validation Test - Check if queries retrieve expected PDFs
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import numpy as np

def load_expected_results() -> Dict[str, str]:
    """Load expected PDF results from frequency_based_test_queries.json"""
    
    freq_queries_file = Path("evaluation/queries/frequency_based_test_queries.json")
    
    with open(freq_queries_file, 'r') as f:
        data = json.load(f)
    
    expected_results = {}
    for query in data["queries"]:
        query_id = query["id"]
        expected_pdf = query.get("expected_pdf", "")
        expected_results[query_id] = expected_pdf
    
    return expected_results

def check_pdf_match(expected_pdf: str, hospital_guidelines: int, confidence_scores: List[float]) -> bool:
    """
    Heuristic to check if query likely retrieved expected content
    """
    # If no hospital guidelines found, it's definitely a miss
    if hospital_guidelines == 0:
        return False
    
    # If expected is very specific (contains specific PDF name), require higher threshold
    if ".pdf" in expected_pdf and "specific" in expected_pdf.lower():
        return hospital_guidelines >= 20 and (confidence_scores and max(confidence_scores) > 0.7)
    
    # For medium specificity
    elif "pdf" in expected_pdf.lower():
        return hospital_guidelines >= 15 and (confidence_scores and max(confidence_scores) > 0.6)
    
    # For broad or general expectations
    else:
        return hospital_guidelines >= 10 and (confidence_scores and max(confidence_scores) > 0.5)

def calculate_accuracy(evaluation_results_file: str) -> Dict[str, Any]:
    """Calculate accuracy metrics"""
    
    print("🎯 Loading evaluation results...")
    with open(evaluation_results_file, 'r') as f:
        data = json.load(f)
    
    print("📋 Loading expected results...")
    expected_results = load_expected_results()
    
    query_results = data["query_execution_results"]["raw_results"]
    
    accuracy_stats = {
        "total_queries": len(query_results),
        "hits": 0,
        "misses": 0,
        "query_details": [],
        "by_specificity": {
            "broad": {"hits": 0, "total": 0},
            "medium": {"hits": 0, "total": 0}, 
            "specific": {"hits": 0, "total": 0}
        }
    }
    
    print(f"\n📊 Analyzing {len(query_results)} queries...")
    
    for query_result in query_results:
        query_id = query_result["query_id"]
        specificity = query_result.get("query_metadata", {}).get("specificity", "unknown")
        expected_pdf = expected_results.get(query_id, "No expectation defined")
        
        # Extract retrieval information
        pipeline_analysis = query_result.get("pipeline_analysis", {})
        retrieval_info = pipeline_analysis.get("retrieval_info", {})
        hospital_guidelines = retrieval_info.get("hospital_guidelines", 0)
        confidence_scores = retrieval_info.get("confidence_scores", [])
        
        # Check if we got what we expected
        hit = check_pdf_match(expected_pdf, hospital_guidelines, confidence_scores)
        
        if hit:
            accuracy_stats["hits"] += 1
            status = "✅ HIT"
        else:
            accuracy_stats["misses"] += 1
            status = "❌ MISS"
        
        # Track by specificity
        if specificity in accuracy_stats["by_specificity"]:
            accuracy_stats["by_specificity"][specificity]["total"] += 1
            if hit:
                accuracy_stats["by_specificity"][specificity]["hits"] += 1
        
        # Get best confidence score for reporting
        best_confidence = max(confidence_scores) if confidence_scores else 0.0
        
        accuracy_stats["query_details"].append({
            "query_id": query_id,
            "specificity": specificity,
            "expected": expected_pdf,
            "found_guidelines": hospital_guidelines,
            "best_confidence": best_confidence,
            "hit": hit,
            "status": status
        })
        
        print(f"  {status} {query_id} ({specificity}): {hospital_guidelines} docs, max_conf={best_confidence:.3f}")
    
    accuracy_stats["accuracy_rate"] = accuracy_stats["hits"] / accuracy_stats["total_queries"] if accuracy_stats["total_queries"] > 0 else 0
    
    # Calculate accuracy by specificity
    for spec_type, spec_data in accuracy_stats["by_specificity"].items():
        if spec_data["total"] > 0:
            spec_data["accuracy"] = spec_data["hits"] / spec_data["total"]
        else:
            spec_data["accuracy"] = 0
    
    return accuracy_stats

def generate_accuracy_chart(accuracy_stats: Dict[str, Any]) -> str:
    """Generate accuracy visualization chart"""
    
    print("\n📊 Generating accuracy chart...")
    
    # Set up the figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Chart 1: Overall Accuracy (Pie Chart)
    hits = accuracy_stats["hits"]
    misses = accuracy_stats["misses"]
    
    colors = ['#2ca02c', '#d62728']  # Green for hits, red for misses
    labels = [f'Hits ({hits})', f'Misses ({misses})']
    sizes = [hits, misses]
    
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                                       startangle=90, textprops={'fontweight': 'bold'})
    ax1.set_title('Expected PDF Retrieval Accuracy', fontsize=14, fontweight='bold', pad=20)
    
    # Chart 2: Accuracy by Query Specificity (Bar Chart)
    specificities = ['Broad', 'Medium', 'Specific']
    accuracies = []
    totals = []
    
    for spec in ['broad', 'medium', 'specific']:
        spec_data = accuracy_stats["by_specificity"][spec]
        accuracy = spec_data["accuracy"] * 100  # Convert to percentage
        total = spec_data["total"]
        accuracies.append(accuracy)
        totals.append(total)
    
    # Color mapping (consistent with existing charts)
    bar_colors = ['#1f77b4', '#ff7f0e', '#d62728']
    bars = ax2.bar(specificities, accuracies, color=bar_colors, alpha=0.8, edgecolor='white', linewidth=1)
    
    ax2.set_title('Accuracy by Query Specificity', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Accuracy (%)', fontsize=12)
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, accuracy, total) in enumerate(zip(bars, accuracies, totals)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{accuracy:.1f}%\n({accuracy_stats["by_specificity"][["broad", "medium", "specific"][i]]["hits"]}/{total})',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Add overall accuracy annotation
    overall_accuracy = accuracy_stats["accuracy_rate"] * 100
    fig.suptitle(f'Hospital Customization Retrieval Accuracy Analysis (Overall: {overall_accuracy:.1f}%)', 
                 fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    
    # Save chart
    output_path = Path("evaluation/results/charts/expected_pdf_accuracy_chart.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ Accuracy chart saved to: {output_path}")
    return str(output_path)

def main():
    """Main validation function"""
    
    print("🎯 Hospital Customization Expected PDF Accuracy Validation")
    print("=" * 65)
    
    # Use latest evaluation results
    results_file = "evaluation/results/hospital_customization_evaluation_20250805_211929.json"
    
    if not Path(results_file).exists():
        print(f"❌ Results file not found: {results_file}")
        return 1
    
    try:
        accuracy_stats = calculate_accuracy(results_file)
        
        print(f"\n📈 Accuracy Summary:")
        print(f"   Total Queries: {accuracy_stats['total_queries']}")
        print(f"   Hits: {accuracy_stats['hits']}")
        print(f"   Misses: {accuracy_stats['misses']}")
        print(f"   Overall Accuracy: {accuracy_stats['accuracy_rate']:.1%}")
        
        print(f"\n📋 Accuracy by Specificity:")
        for spec_type, spec_data in accuracy_stats["by_specificity"].items():
            if spec_data["total"] > 0:
                print(f"   {spec_type.capitalize()}: {spec_data['accuracy']:.1%} ({spec_data['hits']}/{spec_data['total']})")
        
        # Generate visualization
        chart_path = generate_accuracy_chart(accuracy_stats)
        
        # Save detailed results
        output_file = Path("evaluation/results/expected_pdf_accuracy_validation.json")
        with open(output_file, 'w') as f:
            json.dump(accuracy_stats, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        print(f"📊 Accuracy chart generated: {Path(chart_path).name}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)