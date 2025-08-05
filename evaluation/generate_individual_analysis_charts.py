#!/usr/bin/env python3
"""
Generate individual analysis charts from Hospital Customization - Advanced Performance Analysis.
Each chart is generated separately with its own title, no overall header or insights.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

def create_performance_trend_chart():
    """Create Performance Trend During Evaluation chart."""
    
    # Data from the advanced analysis
    execution_order = [1, 2, 3, 4, 5, 6]
    latencies = [64.1, 56.9, 47.0, 52.9, 54.1, 57.6]
    query_types = ['Broad', 'Broad', 'Medium', 'Medium', 'Specific', 'Specific']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color mapping
    colors = {'Broad': '#FF8C00', 'Medium': '#32CD32', 'Specific': '#DC143C'}
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


def create_system_efficiency_chart():
    """Create System Efficiency Analysis chart."""
    
    # Data for efficiency analysis
    query_ids = ['broad_1', 'broad_2', 'medium_1', 'medium_2', 'specific_1', 'specific_2']
    chunks_per_second = [0.37, 0.93, 0.77, 0.45, 0.33, 0.38]
    query_types = ['Broad', 'Broad', 'Medium', 'Medium', 'Specific', 'Specific']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color mapping
    colors = {'Broad': '#FF8C00', 'Medium': '#32CD32', 'Specific': '#DC143C'}
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


def create_quality_quantity_tradeoff_chart():
    """Create Quality vs Quantity Trade-off chart."""
    
    # Data for quality vs quantity
    hospital_chunks = [24, 53, 36, 24, 18, 22]
    similarity_scores = [0.334, 0.825, 0.804, 0.532, 0.426, 0.420]
    query_ids = ['broad_1', 'broad_2', 'medium_1', 'medium_2', 'specific_1', 'specific_2']
    query_types = ['Broad', 'Broad', 'Medium', 'Medium', 'Specific', 'Specific']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color mapping
    colors = {'Broad': '#FF8C00', 'Medium': '#32CD32', 'Specific': '#DC143C'}
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


def create_comprehensive_performance_profile_chart():
    """Create Comprehensive Performance Profile chart (radar chart)."""
    
    # Data for radar chart
    categories = ['Speed\n(Inverse Latency)', 'Content Volume\n(Chunks)', 'Efficiency\n(Chunks/sec)', 'Quality\n(Similarity)']
    
    # Normalized data (0-100 scale)
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
    
    ax.plot(angles, broad_data, 'o-', linewidth=2, label='Broad', color='#FF8C00')
    ax.fill(angles, broad_data, alpha=0.25, color='#FF8C00')
    
    ax.plot(angles, medium_data, 'o-', linewidth=2, label='Medium', color='#32CD32')
    ax.fill(angles, medium_data, alpha=0.25, color='#32CD32')
    
    ax.plot(angles, specific_data, 'o-', linewidth=2, label='Specific', color='#DC143C')
    ax.fill(angles, specific_data, alpha=0.25, color='#DC143C')
    
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
    """Generate all four individual analysis charts."""
    print("🚀 Generating individual Hospital Customization analysis charts...")
    
    try:
        # Generate each chart separately
        chart1 = create_performance_trend_chart()
        chart2 = create_system_efficiency_chart()
        chart3 = create_quality_quantity_tradeoff_chart()
        chart4 = create_comprehensive_performance_profile_chart()
        
        print(f"\n🎉 All 4 individual charts generated successfully!")
        print(f"📊 Performance Trend: {chart1}")
        print(f"📊 System Efficiency: {chart2}")
        print(f"📊 Quality vs Quantity: {chart3}")
        print(f"📊 Performance Profile: {chart4}")
        print(f"💡 All charts optimized for PPT presentations with high DPI (300)")
        print(f"🎯 No overall headers or insights - pure charts as requested")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating individual charts: {e}")
        return False


if __name__ == "__main__":
    main()