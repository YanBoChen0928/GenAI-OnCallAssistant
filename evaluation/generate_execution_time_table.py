#!/usr/bin/env python3
"""
Generate execution time breakdown table as PNG for PPT use.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

def create_execution_time_table():
    """Create a professional execution time breakdown table."""
    
    # Data from the execution_time_breakdown.md
    data = {
        'Query ID': ['broad_1', 'broad_2', 'medium_1', 'medium_2', 'specific_1', 'specific_2'],
        'Query Type': ['Broad', 'Broad', 'Medium', 'Medium', 'Specific', 'Specific'],
        'Total Time (s)': [64.13, 56.85, 47.00, 52.85, 54.12, 57.64],
        'Search Time (s)': [6.476, 5.231, 4.186, 4.892, 3.784, 4.127],
        'Generation Time (s)': [57.036, 50.912, 42.149, 47.203, 49.681, 52.831],
        'Hospital Guidelines': [24, 53, 36, 24, 18, 22],
        'Search %': [10.1, 9.2, 8.9, 9.3, 7.0, 7.2],
        'Generation %': [89.0, 89.5, 89.7, 89.3, 91.8, 91.7]
    }
    
    df = pd.DataFrame(data)
    
    # Create figure with custom styling (smaller since no summary)
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Create the table
    table_data = []
    
    # Header row with two lines
    headers = [
        'Query ID\n(Type)',
        'Total Time\n(seconds)',
        'Search Time\n(seconds)',
        'Generation Time\n(seconds)', 
        'Hospital\nGuidelines',
        'Search\n%',
        'Generation\n%'
    ]
    
    # Data rows
    for i, row in df.iterrows():
        table_row = [
            f"{row['Query ID']}\n({row['Query Type']})",
            f"{row['Total Time (s)']:.1f}",
            f"{row['Search Time (s)']:.2f}",
            f"{row['Generation Time (s)']:.1f}",
            f"{row['Hospital Guidelines']}",
            f"{row['Search %']:.1f}%",
            f"{row['Generation %']:.1f}%"
        ]
        table_data.append(table_row)
    
    # Create table
    table = ax.table(
        cellText=table_data,
        colLabels=headers,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 2.5)
    
    # Header styling
    for i in range(len(headers)):
        cell = table[(0, i)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(weight='bold', color='white')
        cell.set_height(0.15)
    
    # Data cell styling
    colors = ['#E7F3FF', '#F8FBFF']  # Alternating row colors
    
    for i in range(1, len(table_data) + 1):
        row_color = colors[i % 2]
        
        for j in range(len(headers)):
            cell = table[(i, j)]
            cell.set_facecolor(row_color)
            cell.set_height(0.12)
            
            # Highlight fastest and slowest
            if j == 1:  # Total Time column (now index 1)
                value = float(df.iloc[i-1]['Total Time (s)'])
                if value == df['Total Time (s)'].min():  # Fastest
                    cell.set_facecolor('#90EE90')  # Light green
                    cell.set_text_props(weight='bold')
                elif value == df['Total Time (s)'].max():  # Slowest
                    cell.set_facecolor('#FFB6C1')  # Light red
                    cell.set_text_props(weight='bold')
            
            # Highlight highest guidelines count
            if j == 4:  # Hospital Guidelines column (now index 4)
                value = int(df.iloc[i-1]['Hospital Guidelines'])
                if value == df['Hospital Guidelines'].max():
                    cell.set_facecolor('#FFD700')  # Gold
                    cell.set_text_props(weight='bold')
    
    # Add title
    plt.suptitle('Hospital Customization System - Execution Time Breakdown Analysis', 
                 fontsize=18, fontweight='bold', y=0.95)
    
    # No summary statistics - removed as requested
    
    # Save the table
    output_path = Path("evaluation/results/execution_time_breakdown_table.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✅ Execution time breakdown table saved to: {output_path}")
    return str(output_path)


def create_performance_summary_table():
    """Create a compact performance summary table."""
    
    # Summary data by query type
    data = {
        'Question Type': ['Broad Questions', 'Medium Questions', 'Specific Questions', 'Overall Average'],
        'Avg Total Time (s)': [60.5, 49.9, 55.9, 55.5],
        'Avg Search Time (s)': [5.85, 4.54, 3.96, 4.78],
        'Avg Generation Time (s)': [54.0, 44.7, 51.3, 50.0],
        'Search % of Total': [9.6, 9.1, 7.1, 8.6],
        'Generation % of Total': [89.3, 89.5, 91.8, 90.2],
        'Success Rate': ['100%', '100%', '100%', '100%'],
        'Avg Guidelines': [38.5, 30.0, 20.0, 29.5]
    }
    
    df = pd.DataFrame(data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Create headers with two lines for better spacing
    headers_formatted = [
        'Question\nType',
        'Avg Total\nTime (s)',
        'Avg Search\nTime (s)', 
        'Avg Generation\nTime (s)',
        'Search %\nof Total',
        'Generation %\nof Total',
        'Success\nRate',
        'Avg\nGuidelines'
    ]
    
    # Create table
    table = ax.table(
        cellText=df.values,
        colLabels=headers_formatted,
        cellLoc='center',
        loc='center',
        bbox=[0, 0.15, 1, 0.75]
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.3, 2.5)
    
    # Header styling
    for i in range(len(headers_formatted)):
        cell = table[(0, i)]
        cell.set_facecolor('#2E86AB')
        cell.set_text_props(weight='bold', color='white')
        cell.set_height(0.18)
    
    # Data cell styling
    colors = ['#E7F3FF', '#F0F8FF', '#F8FBFF', '#FFE4B5']  # Different colors for each row
    
    for i in range(1, len(df) + 1):
        row_color = colors[i-1] if i-1 < len(colors) else '#F8F8FF'
        
        for j in range(len(headers_formatted)):
            cell = table[(i, j)]
            cell.set_facecolor(row_color)
            cell.set_height(0.14)
            
            # Highlight the overall average row
            if i == len(df):  # Last row (Overall Average)
                cell.set_text_props(weight='bold')
                cell.set_facecolor('#FFE4B5')
    
    # Add title
    plt.suptitle('Performance Summary by Question Type - Hospital Customization System', 
                 fontsize=16, fontweight='bold', y=0.92)
    
    # Save the table
    output_path = Path("evaluation/results/performance_summary_by_type_table.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✅ Performance summary table saved to: {output_path}")
    return str(output_path)


def main():
    """Generate both execution time tables."""
    print("🚀 Generating execution time breakdown tables for PPT...")
    
    # Generate detailed execution time breakdown
    detailed_table = create_execution_time_table()
    
    # Generate performance summary by type
    summary_table = create_performance_summary_table()
    
    print(f"\n🎉 Tables generated successfully!")
    print(f"📊 Detailed breakdown: {detailed_table}")
    print(f"📈 Performance summary: {summary_table}")
    print(f"💡 Both tables are optimized for PPT presentations with high DPI (300)")


if __name__ == "__main__":
    main()