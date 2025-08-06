#!/usr/bin/env python3
"""
Generate individual analysis charts from Hospital Customization - Advanced Performance Analysis.
Each chart is generated separately with its own title, no overall header or insights.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

def load_latest_evaluation_data():
    """Load the latest hospital customization evaluation data."""
    results_dir = Path("evaluation/results")
    
    # Find the latest hospital_customization_evaluation file
    json_files = list(results_dir.glob("hospital_customization_evaluation_*.json"))
    if not json_files:
        print("⚠️ No evaluation JSON files found. Using sample data.")
        return None
    
    # Sort by timestamp and get the latest
    latest_file = sorted(json_files, key=lambda x: x.stem.split('_')[-2:])[-1]
    print(f"📂 Loading data from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def extract_metrics_from_data(data):
    """Extract metrics from the evaluation data."""
    if not data:
        return None
    
    raw_results = data["query_execution_results"]["raw_results"]
    
    # Extract latencies and query types
    execution_order = []
    latencies = []
    query_types = []
    query_ids = []
    customization_times = []
    generation_times = []
    hospital_guidelines_counts = []
    
    for i, result in enumerate(raw_results, 1):
        execution_order.append(i)
        latencies.append(result["execution_time"]["total_seconds"])
        
        # Extract query type from specificity
        specificity = result["query_metadata"]["specificity"]
        query_types.append(specificity.capitalize())
        query_ids.append(result["query_id"])
        
        # Extract customization and generation times from processing steps
        processing = result["response"]["processing_steps"]
        
        # Parse customization time
        if "Customization time:" in processing:
            cust_time_str = processing.split("Customization time: ")[1].split("s")[0]
            customization_times.append(float(cust_time_str))
        else:
            customization_times.append(0)
        
        # Parse generation time
        if "Generation time:" in processing:
            gen_time_str = processing.split("Generation time: ")[1].split("s")[0]
            generation_times.append(float(gen_time_str))
        else:
            generation_times.append(0)
        
        # Get hospital guidelines count
        hospital_guidelines_counts.append(result["pipeline_analysis"]["retrieval_info"]["hospital_guidelines"])
    
    return {
        "execution_order": execution_order,
        "latencies": latencies,
        "query_types": query_types,
        "query_ids": query_ids,
        "customization_times": customization_times,
        "generation_times": generation_times,
        "hospital_guidelines_counts": hospital_guidelines_counts
    }

def create_performance_trend_chart(metrics=None):
    """Create Performance Trend During Evaluation chart."""
    
    if metrics:
        # Use actual data
        execution_order = metrics["execution_order"]
        latencies = metrics["latencies"]
        query_types = metrics["query_types"]
    else:
        # Fallback to sample data
        execution_order = [1, 2, 3, 4, 5, 6]
        latencies = [64.1, 56.9, 47.0, 52.9, 54.1, 57.6]
        query_types = ['Broad', 'Broad', 'Medium', 'Medium', 'Specific', 'Specific']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color mapping (consistent with friend's standard colors)
    colors = {'Broad': '#1f77b4', 'Medium': '#ff7f0e', 'Specific': '#d62728'}
    point_colors = [colors[qt] for qt in query_types]
    
    # Plot line with points
    ax.plot(execution_order, latencies, 'o-', linewidth=2, markersize=8, color='gray', alpha=0.7)
    
    # Color code the points
    for i, (x, y, color) in enumerate(zip(execution_order, latencies, point_colors)):
        ax.scatter(x, y, c=color, s=100, zorder=5, edgecolors='white', linewidth=2)
    
    # Customization
    ax.set_title('Performance Trend During Evaluation', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Execution Order', fontsize=12)
    ax.set_ylabel('Latency (seconds)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(40, 70)
    
    # Legend
    legend_elements = [plt.scatter([], [], c=color, s=100, label=query_type, edgecolors='white', linewidth=1) 
                      for query_type, color in colors.items()]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    
    # Save
    output_path = Path("evaluation/results/individual_charts/performance_trend_chart.png")
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ Performance Trend chart saved to: {output_path}")
    return str(output_path)


def create_system_efficiency_chart(metrics=None):
    """Create System Efficiency Analysis chart."""
    
    if metrics:
        # Calculate chunks per second from actual data
        query_ids = metrics["query_ids"]
        query_types = metrics["query_types"]
        
        # Calculate efficiency as guidelines per second
        chunks_per_second = []
        for i in range(len(query_ids)):
            guidelines_count = metrics["hospital_guidelines_counts"][i]
            total_time = metrics["latencies"][i]
            efficiency = guidelines_count / total_time if total_time > 0 else 0
            chunks_per_second.append(efficiency)
    else:
        # Fallback to sample data
        query_ids = ['broad_1', 'broad_2', 'medium_1', 'medium_2', 'specific_1', 'specific_2']
        chunks_per_second = [0.37, 0.93, 0.77, 0.45, 0.33, 0.38]
        query_types = ['Broad', 'Broad', 'Medium', 'Medium', 'Specific', 'Specific']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color mapping (consistent with friend's standard colors)
    colors = {'Broad': '#1f77b4', 'Medium': '#ff7f0e', 'Specific': '#d62728'}
    bar_colors = [colors[qt] for qt in query_types]
    
    # Create bar chart
    bars = ax.bar(query_ids, chunks_per_second, color=bar_colors, alpha=0.8, edgecolor='white', linewidth=1)
    
    # Add value labels on bars
    for bar, value in zip(bars, chunks_per_second):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                f'{value:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Customization
    ax.set_title('System Efficiency Analysis', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Query ID', fontsize=12)
    ax.set_ylabel('Chunks per Second', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1.0)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Save
    output_path = Path("evaluation/results/individual_charts/system_efficiency_chart.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ System Efficiency chart saved to: {output_path}")
    return str(output_path)


def create_quality_quantity_tradeoff_chart(metrics=None):
    """Create Quality vs Quantity Trade-off chart."""
    
    if metrics:
        # Use actual data
        hospital_chunks = metrics["hospital_guidelines_counts"]
        query_ids = metrics["query_ids"]
        query_types = metrics["query_types"]
        
        # Calculate similarity scores as customization_time / total_time
        similarity_scores = []
        for i in range(len(query_ids)):
            if metrics["latencies"][i] > 0:
                # Use ratio of customization time to total time as a proxy for quality
                ratio = metrics["customization_times"][i] / metrics["latencies"][i]
                similarity_scores.append(min(ratio, 1.0))  # Cap at 1.0
            else:
                similarity_scores.append(0.5)  # Default value
    else:
        # Fallback to sample data
        hospital_chunks = [24, 53, 36, 24, 18, 22]
        similarity_scores = [0.334, 0.825, 0.804, 0.532, 0.426, 0.420]
        query_ids = ['broad_1', 'broad_2', 'medium_1', 'medium_2', 'specific_1', 'specific_2']
        query_types = ['Broad', 'Broad', 'Medium', 'Medium', 'Specific', 'Specific']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color mapping (consistent with friend's standard colors)
    colors = {'Broad': '#1f77b4', 'Medium': '#ff7f0e', 'Specific': '#d62728'}
    point_colors = [colors[qt] for qt in query_types]
    
    # Create scatter plot
    for i, (x, y, color, qid) in enumerate(zip(hospital_chunks, similarity_scores, point_colors, query_ids)):
        ax.scatter(x, y, c=color, s=150, alpha=0.8, edgecolors='white', linewidth=2)
        ax.annotate(qid, (x, y), xytext=(5, 5), textcoords='offset points', fontsize=9, alpha=0.8)
    
    # Customization
    ax.set_title('Quality vs Quantity Trade-off', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Hospital Chunks Retrieved', fontsize=12)
    ax.set_ylabel('Estimated Similarity Score', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(10, 60)
    ax.set_ylim(0, 1)
    
    # Legend
    legend_elements = [plt.scatter([], [], c=color, s=150, label=query_type, edgecolors='white', linewidth=1) 
                      for query_type, color in colors.items()]
    ax.legend(handles=legend_elements, loc='upper left')
    
    plt.tight_layout()
    
    # Save
    output_path = Path("evaluation/results/individual_charts/quality_quantity_tradeoff_chart.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ Quality vs Quantity Trade-off chart saved to: {output_path}")
    return str(output_path)


def create_comprehensive_performance_profile_chart(metrics=None):
    """Create Comprehensive Performance Profile chart (radar chart)."""
    
    # Data for radar chart
    categories = ['Speed\n(Inverse Latency)', 'Content Volume\n(Guidelines)', 'Efficiency\n(Guidelines/sec)', 'Quality\n(Customization Ratio)']
    
    if metrics:
        # Calculate normalized data from actual metrics
        def normalize_to_100(values, inverse=False):
            if not values or all(v == 0 for v in values):
                return [50] * len(values)  # Default to middle if no data
            min_val, max_val = min(values), max(values)
            if min_val == max_val:
                return [50] * len(values)
            if inverse:
                return [100 - ((v - min_val) / (max_val - min_val)) * 100 for v in values]
            else:
                return [((v - min_val) / (max_val - min_val)) * 100 for v in values]
        
        # Group by query type
        broad_indices = [i for i, qt in enumerate(metrics["query_types"]) if qt == "Broad"]
        medium_indices = [i for i, qt in enumerate(metrics["query_types"]) if qt == "Medium"]
        specific_indices = [i for i, qt in enumerate(metrics["query_types"]) if qt == "Specific"]
        
        # Calculate averages for each metric by query type
        def calc_avg(indices, values):
            return sum(values[i] for i in indices) / len(indices) if indices else 0
        
        # Speed (inverse latency)
        broad_speed = calc_avg(broad_indices, normalize_to_100(metrics["latencies"], inverse=True))
        medium_speed = calc_avg(medium_indices, normalize_to_100(metrics["latencies"], inverse=True))
        specific_speed = calc_avg(specific_indices, normalize_to_100(metrics["latencies"], inverse=True))
        
        # Content volume (guidelines count)
        broad_volume = calc_avg(broad_indices, normalize_to_100(metrics["hospital_guidelines_counts"]))
        medium_volume = calc_avg(medium_indices, normalize_to_100(metrics["hospital_guidelines_counts"]))
        specific_volume = calc_avg(specific_indices, normalize_to_100(metrics["hospital_guidelines_counts"]))
        
        # Efficiency (guidelines per second)
        efficiency_values = [metrics["hospital_guidelines_counts"][i] / metrics["latencies"][i] 
                           if metrics["latencies"][i] > 0 else 0 
                           for i in range(len(metrics["latencies"]))]
        broad_efficiency = calc_avg(broad_indices, normalize_to_100(efficiency_values))
        medium_efficiency = calc_avg(medium_indices, normalize_to_100(efficiency_values))
        specific_efficiency = calc_avg(specific_indices, normalize_to_100(efficiency_values))
        
        # Quality (customization ratio)
        quality_values = [metrics["customization_times"][i] / metrics["latencies"][i] * 100
                         if metrics["latencies"][i] > 0 else 50
                         for i in range(len(metrics["latencies"]))]
        broad_quality = calc_avg(broad_indices, quality_values)
        medium_quality = calc_avg(medium_indices, quality_values)
        specific_quality = calc_avg(specific_indices, quality_values)
        
        broad_data = [broad_speed, broad_volume, broad_efficiency, broad_quality]
        medium_data = [medium_speed, medium_volume, medium_efficiency, medium_quality]
        specific_data = [specific_speed, specific_volume, specific_efficiency, specific_quality]
    else:
        # Fallback to sample data
        broad_data = [20, 80, 65, 58]    # Broad queries average
        medium_data = [100, 60, 85, 75]  # Medium queries average  
        specific_data = [40, 45, 50, 65] # Specific queries average
    
    # Number of variables
    N = len(categories)
    
    # Compute angle for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the circle
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    # Add each query type
    broad_data += broad_data[:1]
    medium_data += medium_data[:1]  
    specific_data += specific_data[:1]
    
    ax.plot(angles, broad_data, 'o-', linewidth=2, label='Broad', color='#1f77b4')
    ax.fill(angles, broad_data, alpha=0.25, color='#1f77b4')
    
    ax.plot(angles, medium_data, 'o-', linewidth=2, label='Medium', color='#ff7f0e')
    ax.fill(angles, medium_data, alpha=0.25, color='#ff7f0e')
    
    ax.plot(angles, specific_data, 'o-', linewidth=2, label='Specific', color='#d62728')
    ax.fill(angles, specific_data, alpha=0.25, color='#d62728')
    
    # Add category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    
    # Set y-axis limits
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
    ax.grid(True)
    
    # Title and legend
    ax.set_title('Comprehensive Performance Profile', fontsize=16, fontweight='bold', pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
    
    plt.tight_layout()
    
    # Save
    output_path = Path("evaluation/results/individual_charts/comprehensive_performance_profile_chart.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ Comprehensive Performance Profile chart saved to: {output_path}")
    return str(output_path)


def main():
    """Generate all four individual analysis charts using latest evaluation data."""
    print("🚀 Generating individual Hospital Customization analysis charts...")
    
    try:
        # Load latest evaluation data
        print("📂 Loading latest evaluation data...")
        data = load_latest_evaluation_data()
        metrics = extract_metrics_from_data(data)
        
        if metrics:
            print(f"✅ Using actual data from latest evaluation ({len(metrics['latencies'])} queries)")
            print(f"   • Latency range: {min(metrics['latencies']):.1f}s - {max(metrics['latencies']):.1f}s")
            print(f"   • Query types: {set(metrics['query_types'])}")
        else:
            print("⚠️  Using sample data (no evaluation file found)")
        
        # Generate each chart separately with actual data
        print("\n📈 Generating charts...")
        chart1 = create_performance_trend_chart(metrics)
        chart2 = create_system_efficiency_chart(metrics)
        chart3 = create_quality_quantity_tradeoff_chart(metrics)
        chart4 = create_comprehensive_performance_profile_chart(metrics)
        
        print(f"\n🎉 All 4 individual charts generated successfully!")
        print(f"📊 Performance Trend: {Path(chart1).name}")
        print(f"📊 System Efficiency: {Path(chart2).name}")
        print(f"📊 Quality vs Quantity: {Path(chart3).name}")
        print(f"📊 Performance Profile: {Path(chart4).name}")
        print(f"💡 All charts optimized for PPT presentations with high DPI (300)")
        print(f"🎯 Charts based on {'actual evaluation data' if metrics else 'sample data'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating individual charts: {e}")
        import traceback
        print(f"   {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    main()